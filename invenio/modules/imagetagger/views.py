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

"""
    invenio.modules.imagetagger.views
    ---------------------------------

    Tagging interface.
"""

#FIXME add user authentication!!!
from flask import (request, flash, 
                   redirect, url_for, Blueprint, 
                   json)
from invenio.ext.sqlalchemy import db
from invenio.ext.template import render_template_to_string
from sqlalchemy.exc import SQLAlchemyError

from .json_utils import get_json, json_to_array
from .face_detection import find_faces
from .imagetag import Imagetag
from .models import ItgTAG, ItgNormalizedFace, ItgTAGJson
from .CollectionHandler import CollectionHandler
from .face_normalization import normalizeAndSave
from .utils import get_path, is_collection, get_image_list, temp_training_dir
from .api import save_tags, run_training

blueprint = Blueprint('imagetagger', __name__, url_prefix='/imagetagger',
                      template_folder='templates', static_folder='static')



from invenio.modules.record.views import request_record
from flask.ext.login import current_user, login_required

#FIXME this needs refactoring to allow multiple processes run the code
ch = None

@blueprint.route('/record/<int:recid>',
                 methods=['GET', 'POST'])
@blueprint.route('/record/<int:recid>/<int:docid>',
                 methods=['GET', 'POST'])
@login_required
@request_record
def edit(recid, docid=None, width=800):
    global ch
    path, full_path = get_path(recid, docid)
    from .template_context_functions.tfn_imagetagger_overlay import template_context_function

    if ch == None:
        ch = CollectionHandler(image_list=get_image_list(recid), collection_id=recid)
        
    if not is_collection(recid):
        if request.method == 'POST':#tags have just be saved
            nb_tags = request.form["nb_tags"]
            tags = []
            already_tagged = []
            for id_tag in request.form.keys():
                if id_tag == "nb_tags":
                    continue
                val = Imagetag (tag_id=id_tag[3:], array=request.form[id_tag].split(';'))
                tags.append(val)
                if val.type == "face":
                    already_tagged.append(val.to_array())
            potential_tags = find_faces(full_path, width=width, already_tagged=already_tagged)
            save_tags(recid, tags)
            return template_context_function(recid, path, tags=already_tagged, faces=potential_tags, width=width)
        else:
            result = get_json(recid)
            potential_tags = find_faces(full_path, width=width, already_tagged=json_to_array(result))
            suggestions = CollectionHandler().suggest_one_image(full_path, width)
            return template_context_function(recid, path, tags=json_to_array(result), faces=potential_tags, width=width, suggested=suggestions)
    else:
        if request.method == 'POST':
            nb_tags = request.form["nb_tags"]
            tags = []
            face_tags = []
            already_tagged = []
            for id_tag in request.form.keys():
                if id_tag == "nb_tags":
                    continue
                val = Imagetag (tag_id=id_tag[3:], array=request.form[id_tag].split(';'))
                tags.append(val)
                if val.type == 'face':
                    face_tags.append(val)
                    already_tagged.append(val.to_array())
            save_tags(recid, tags, id_image=docid)
            ch.add(face_tags, docid)
            return template_context_function(recid, path, tags=already_tagged, width=width)
        else:
            result = get_json(recid, docid)
            jsontags = json_to_array(result)
            suggestions = ch.get_suggestions(docid) 
            if len(suggestions) > 0:                  
                if len(jsontags) == 0:                
                    jsontags = suggestions
                else:
                    jsontags.append(suggestions)
            potential_tags = find_faces(full_path, width=width, already_tagged=jsontags)
            return template_context_function(recid, path, tags=json_to_array(result), faces=potential_tags, width=width, suggested=suggestions)
           
@blueprint.route('/record/<int:recid>/delete', methods=['GET', 'POST'])
@blueprint.route('/record/<int:recid>/delete/<int:docid>',
                 methods=['GET', 'POST'])
@login_required
@request_record
def delete(recid, docid=None):
    """tag deleting (the whole tags for a photo)"""
    where = {'id_bibrec': recid}
    if docid is not None:
        where['id_image'] = docid

    db.session.query(ItgTAG).filter_by(**where).delete()
    db.session.query(ItgNormalizedFace).filter_by(**where).delete()
    db.session.query(ItgTAGJson).filter_by(**where).delete()
    db.session.commit()
    redirect(url_for(".record", recid=recid, docid=docid))



@blueprint.route('/record/<int:recid>')
@blueprint.route('/record/<int:recid>/<int:docid>')
def view(recid, docid=None):
    """request the json file from the DB"""
    where = {'id_bibrec': recid}
    if docid is not None:
        where['id_image'] = docid

    tag = db.session.query(ItgTAGJson).query.filter_by(**where).one_or_404()
    return json.loads(tag.content)


