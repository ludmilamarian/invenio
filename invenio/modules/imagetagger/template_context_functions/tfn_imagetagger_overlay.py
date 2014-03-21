# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""""""

# Flask
from flask import url_for
from invenio.ext.template import render_template_to_string
from invenio.base.globals import cfg


def template_context_function(id_bibrec, image, tags='', faces='', suggested='', width=800, text=''):
    """
    :param id_bibrec: ID of record
    :return: HTML containing image overlay
    """

    if id_bibrec:
        return render_template_to_string(
            'imagetagger/overlay_tag.html',
            image=image, tags=tags, faces=faces, suggested=suggested, width=width)
    else:
        return text
