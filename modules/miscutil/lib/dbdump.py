# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2009, 2010, 2011, 2012 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Invenio DB dumper.
"""

import os
import re
import time

from invenio.config import CFG_LOGDIR, CFG_PATH_MYSQL, CFG_PATH_GZIP
from invenio.dbquery import CFG_DATABASE_HOST, \
                            CFG_DATABASE_USER, \
                            CFG_DATABASE_PASS, \
                            CFG_DATABASE_NAME, \
                            CFG_DATABASE_PORT, \
                            CFG_DATABASE_SLAVE, \
                            CFG_DATABASE_DBDUMP_TEMP_DIR, \
                            CFG_DATABASE_DBDUMP_EOS_DIR, \
                            CFG_DATABASE_DBDUMP_EOS_USER, \
                            get_connection_for_dump_on_slave, \
                            run_sql
from invenio.bibtask import task_init, \
                            write_message, \
                            task_set_option, \
                            task_get_option, \
                            task_update_progress, \
                            task_get_task_param, \
                            task_low_level_submission
from invenio.shellutils import run_shell_command, \
                               escape_shell_arg

def get_table_names(value):
    """
    Get table names of the tables matching the given regular expressions
    @param option: list of regular expressions
    @return: list of strings
    """
    rex = re.compile(value)
    return [row[0] for row in run_sql("SHOW TABLES") if rex.search(row[0])]

def check_slave_is_up(connection=None):
    """Raise an StandardError in case the slave is not correctly up."""
    if connection is None:
        connection = get_connection_for_dump_on_slave()
    res = run_sql("SHOW SLAVE STATUS", with_dict=True, connection=connection)
    if res[0]['Slave_IO_Running'] != 'Yes':
        raise StandardError("Slave_IO_Running is not set to 'Yes'")
    if res[0]['Slave_SQL_Running'] != 'Yes':
        raise StandardError("Slave_SQL_Running is not set to 'Yes'")

def check_slave_is_down(connection=None):
    """Raise an StandardError in case the slave is not correctly down."""
    if connection is None:
        connection = get_connection_for_dump_on_slave()
    res = run_sql("SHOW SLAVE STATUS", with_dict=True, connection=connection)
    if res[0]['Slave_SQL_Running'] != 'No':
        raise StandardError("Slave_SQL_Running is not set to 'No'")

def detach_slave(connection=None):
    """Detach the slave."""
    if connection is None:
        connection = get_connection_for_dump_on_slave()
    run_sql("STOP SLAVE SQL_THREAD", connection=connection)
    check_slave_is_down(connection)

def attach_slave(connection=None):
    """Attach the slave."""
    if connection is None:
        connection = get_connection_for_dump_on_slave()
    run_sql("START SLAVE", connection=connection)
    check_slave_is_up(connection)

def check_slave_is_in_consistent_state(connection=None):
    """
    Check if the slave is already aware that dbdump task is running.
    dbdump being a monotask, guarantee that no other task is currently
    running and it's hence safe to detach the slave and start the
    actual dump.
    """
    if connection is None:
        connection = get_connection_for_dump_on_slave()
    i = 0
    ## Let's take the current status of dbdump (e.g. RUNNING, ABOUT TO STOP, etc.)...
    current_status = run_sql("SELECT status FROM schTASK WHERE id=%s", (task_get_task_param('task_id'), ))[0][0]
    while True:
        if i == 10:
            ## Timeout!!
            raise StandardError("The slave seems not to pick up with the master")
        ## ...and let's see if it matches with what the slave sees.
        if run_sql("SELECT status FROM schTASK WHERE id=%s AND status=%s", (task_get_task_param('task_id'), current_status), connection=connection):
            ## Bingo!
            return
        time.sleep(3)
        i += 1


def dump_database(dump_path, host=CFG_DATABASE_HOST, port=CFG_DATABASE_PORT, \
                  user=CFG_DATABASE_USER, passw=CFG_DATABASE_PASS, \
                  name=CFG_DATABASE_NAME, params=None, compress=False, \
                  ignore_tables=None):
    """
    Dump Invenio database into SQL file located at DUMP_PATH.

    Will perform the command to mysqldump with the given host configuration
    and user credentials.

    Optional mysqldump parameters can also be passed. Otherwise, a default
    set of parameters will be used.

    @param dump_path: path on the filesystem to save the dump to.
    @type dump_path: string

    @param host: hostname of mysql database node to connect to.
    @type host: string

    @param port: port of mysql database node to connect to
    @type port: string

    @param user: username to connect with
    @type user: string

    @param passw: password to connect to with
    @type passw: string

    @param name: name of mysql database node to dump
    @type name: string

    @param params: command line parameters to pass to mysqldump. Optional.
    @type params: string

    @param compress: should the dump be compressed through gzip?
    @type compress: bool

    @param ignore_tables: list of tables to ignore in the dump
    @type ignore: list of string
    """
    write_message("... writing %s" % (dump_path,))

    partial_dump_path = dump_path + ".part"

    # Is mysqldump installed or in the right path?
    cmd_prefix = CFG_PATH_MYSQL + 'dump'
    if not os.path.exists(cmd_prefix):
        raise StandardError("%s is not installed." % (cmd_prefix))

    if not params:
        # No parameters set, lets use the default ones.
        params = " --skip-opt --add-drop-table --add-locks --create-options" \
                 " --quick --extended-insert --set-charset --disable-keys" \
                 " --lock-tables=false --max_allowed_packet=2G "

    if ignore_tables:
        params += " ".join([escape_shell_arg("--ignore-table=%s.%s" % (CFG_DATABASE_NAME, table)) for table in ignore_tables])

    dump_cmd = "%s %s " \
               " --host=%s --port=%s --user=%s --password=%s %s" % \
               (cmd_prefix, \
                params, \
                escape_shell_arg(host), \
                escape_shell_arg(str(port)), \
                escape_shell_arg(user), \
                escape_shell_arg(passw), \
                escape_shell_arg(name))

    if compress:
        dump_cmd = "%s | %s -cf; exit ${PIPESTATUS[0]}" % \
                   (dump_cmd, \
                    CFG_PATH_GZIP)
        dump_cmd = "bash -c %s" % (escape_shell_arg(dump_cmd),)

    write_message(dump_cmd, verbose=2)

    exit_code, stdout, stderr = run_shell_command(dump_cmd, None, partial_dump_path)

    if exit_code:
        raise StandardError("ERROR: mysqldump exit code is %s. stderr: %s stdout: %s" % \
                            (repr(exit_code), \
                             repr(stderr), \
                             repr(stdout)))
    else:
        os.rename(partial_dump_path, dump_path)
        write_message("... completed writing %s" % (dump_path,))


def _dbdump_elaborate_submit_param(key, value, dummyopts, dummyargs):
    """
    Elaborate task submission parameter.  See bibtask's
    task_submit_elaborate_specific_parameter_fnc for help.
    """
    if key in ('-n', '--number'):
        try:
            task_set_option('number', int(value))
        except ValueError:
            raise StandardError("ERROR: Number '%s' is not integer." % (value,))
    elif key in ('--params',):
        task_set_option('params', value)
    elif key in ('--compress',):
        if not CFG_PATH_GZIP or (CFG_PATH_GZIP and not os.path.exists(CFG_PATH_GZIP)):
            raise StandardError("ERROR: No valid gzip path is defined.")
        task_set_option('compress', True)
    elif key in ('-S', '--slave'):
        if value:
            task_set_option('slave', value)
        else:
            if not CFG_DATABASE_SLAVE:
                raise StandardError("ERROR: No slave defined.")
            task_set_option('slave', CFG_DATABASE_SLAVE)
    elif key in ('--dump-on-slave-helper', ):
        task_set_option('dump_on_slave_helper_mode', True)
    elif key in ('--ignore-tables',):
        try:
            re.compile(value)
            task_set_option("ignore_tables", value)
        except re.error:
            raise StandardError, "ERROR: Passed string: '%s' is not a valid regular expression." % value
    elif key in ('--ftag',):
        task_set_option('ftag', value)
    else:
        return False
    return True


def _dbdump_run_task_core():
    """
    Run DB dumper core stuff.

    Note: do not use task_can_sleep() stuff here because we don't want
    other tasks to interrupt us while we are dumping the DB content.
    """
    # read params:
    host = CFG_DATABASE_HOST
    port = CFG_DATABASE_PORT
    connection = None
    try:
        if task_get_option('slave') and not task_get_option('dump_on_slave_helper_mode'):
            connection = get_connection_for_dump_on_slave()
            write_message("Dump on slave requested")
            write_message("... checking if slave is well up...")
            check_slave_is_up(connection)
            write_message("... checking if slave is in consistent state...")
            check_slave_is_in_consistent_state(connection)
            write_message("... detaching slave database...")
            detach_slave(connection)
            write_message("... scheduling dump on slave helper...")
            helper_arguments = []
            if task_get_option("number"):
                helper_arguments += ["--number", str(task_get_option("number"))]
            if task_get_option("params"):
                helper_arguments += ["--params", str(task_get_option("params"))]
            if task_get_option("ignore_tables"):
                helper_arguments += ["--ignore-tables", str(task_get_option("ignore_tables"))]
            if task_get_option("compress"):
                helper_arguments += ["--compress"]
            if task_get_option("slave"):
                helper_arguments += ["--slave", str(task_get_option("slave"))]
            if task_get_option("ftag"):
                helper_arguments += ["--ftag", str(task_get_option("ftag"))]
            helper_arguments += ['-N', 'slavehelper', '--dump-on-slave-helper']
            task_id = task_low_level_submission('dbdump', task_get_task_param('user'), '-P4', *helper_arguments)
            write_message("Slave scheduled with ID %s" % task_id)
            task_update_progress("DONE")
            return True
        elif task_get_option('dump_on_slave_helper_mode'):
            write_message("Dumping on slave mode")
            connection = get_connection_for_dump_on_slave()
            write_message("... checking if slave is well down...")
            check_slave_is_down(connection)
            host = CFG_DATABASE_SLAVE

        task_update_progress("Reading parameters")
        write_message("Reading parameters started")
        output_num = task_get_option('number', 5)
        params = task_get_option('params', None)
        compress = task_get_option('compress', False)
        slave = task_get_option('slave', False)
        ignore_tables = task_get_option('ignore_tables', None)
        ftag = task_get_option('ftag', '')
        if ignore_tables:
            ignore_tables = get_table_names(ignore_tables)
        else:
            ignore_tables = None

        output_file_suffix = task_get_task_param('task_starting_time')
        output_file_suffix = output_file_suffix.replace(' ', '_') + '.sql'
        if compress:
            output_file_suffix = "%s.gz" % (output_file_suffix,)
        write_message("Reading parameters ended")

        # make dump:
        task_update_progress("Dumping database")
        write_message("Database dump started")

        output_file_prefix = '{slave}{dbname}{ftag}-dbdump'.format(
            slave='slave-' if slave else '',
            dbname=CFG_DATABASE_NAME,
            ftag='-'+ftag if ftag else ''
        )

        output_file = '{prefix}-{suffix}'.format(
            prefix=output_file_prefix,
            suffix=output_file_suffix
        )
        dump_path = os.path.join(CFG_DATABASE_DBDUMP_TEMP_DIR, output_file)
        dump_database(dump_path, \
                        host=host,
                        port=port,
                        params=params, \
                        compress=compress, \
                        ignore_tables=ignore_tables)
        write_message("Database dump ended")
    finally:
        if connection and task_get_option('dump_on_slave_helper_mode'):
            write_message("Reattaching slave")
            attach_slave(connection)

    task_update_progress("Moving new dump to EOS")
    write_message("Moving new dump to EOS started")

    _new_kerberos_token()

    _move_dump(dump_path, CFG_DATABASE_DBDUMP_EOS_DIR)

    write_message("Moving new dump to EOS ended")

    # prune old dump files:
    task_update_progress("Pruning old dump files")
    write_message("Pruning old dump files started")

    _delete_old_dumps(CFG_DATABASE_DBDUMP_EOS_DIR, output_file_prefix, output_num)

    write_message("Pruning old dump files ended")
    # we are done:
    task_update_progress("Done.")
    return True


def _new_kerberos_token():
    """Renew Kerberos token."""
    cmd = 'unset KRB5CCNAME && kinit -kt /etc/{0}.keytab {0} && eosfusebind'.format(
        CFG_DATABASE_DBDUMP_EOS_USER
    )
    write_message(cmd, verbose=2)

    exit_code, stdout, stderr = run_shell_command(cmd, None, None)

    if exit_code:
        raise StandardError(
            "ERROR: mv db dump to EOS exit code is %s. stderr: %s stdout: "
            "%s" % \
            (repr(exit_code), \
             repr(stderr), \
             repr(stdout)))


def _move_dump(dump_filepath, dumps_dir):
    """Move the dump file to the backup dir."""
    write_message("... moving {0} to {1}".format(dump_filepath, dumps_dir))

    cmd = 'mv {0} {1}'.format(dump_filepath, dumps_dir)
    write_message(cmd, verbose=2)

    exit_code, stdout, stderr = run_shell_command(cmd, None, None)

    if exit_code:
        raise StandardError("ERROR: mv db dump to EOS exit code is %s. stderr: %s stdout: %s" % \
                            (repr(exit_code), \
                             repr(stderr), \
                             repr(stdout)))
    else:
        write_message("... done moving")


def _delete_old_dumps(dirname, filename_prefix, number_to_keep):
    """
    Look for files in DIRNAME directory starting with FILENAME
    pattern.  Delete up to NUMBER_TO_KEEP files (when sorted
    alphabetically, which is equal to sorted by date).  Useful to
    prune old dump files.
    """
    cmd = 'ls -t {dirname_prefix}* | tail -n +{keep} | xargs rm -f'.format(
        dirname_prefix=os.path.join(dirname, filename_prefix),
        keep=number_to_keep+1
    )
    write_message(cmd, verbose=2)

    exit_code, stdout, stderr = run_shell_command(cmd, None, None)

    if exit_code:
        raise StandardError("ERROR: delete old db dumps from EOS exit code is %s. stderr: %s stdout: %s" % \
                            (repr(exit_code), \
                             repr(stderr), \
                             repr(stdout)))


def main():
    """Main that construct all the bibtask."""
    task_init(authorization_action='rundbdump',
              authorization_msg="DB Dump Task Submission",
              help_specific_usage="""\
  -n, --number=NUM      Keep up to NUM previous dump files. [default=5]
  --params=PARAMS       Specify your own mysqldump parameters. Optional.
  --compress            Compress dump directly into gzip.
  -S, --slave=HOST      Perform the dump from a slave, if no host use CFG_DATABASE_SLAVE.
  --ignore-tables=regex Ignore tables matching the given regular expression
  --ftag                Define a tag that will be added to the filename. Useful if you need to distinguish different db dumps.

Examples:
    $ dbdump --ignore-tables '^(idx|rnk)'
    $ dbdump -n3 -o/tmp -s1d -L 02:00-04:00
""",
              specific_params=("n:p:S:",
                               ["number=", "params=", "slave=", "compress", 'ignore-tables=', "dump-on-slave-helper", "ftag="]),
              task_submit_elaborate_specific_parameter_fnc=_dbdump_elaborate_submit_param,
              task_run_fnc=_dbdump_run_task_core)


if __name__ == '__main__':
    main()
