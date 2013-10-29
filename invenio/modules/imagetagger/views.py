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
    invenio.modules.imagetagger.blueprint
    ------------------------------

    Tagging interface.
"""

import os
import numpy as np
import cv2
from werkzeug import LocalProxy
from flask import render_template, request, flash, redirect, url_for, \
    jsonify, Blueprint, json, escape
from invenio.ext.template import render_template_to_string
from sqlalchemy.exc import SQLAlchemyError
from invenio.ext.sqlalchemy import db


from .json_utils import *
from .face_detection import find_faces
from .imagetag import *
from .models import ItgTAG
from .CollectionHandler import CollectionHandler
from .face_normalization import normalizeAndSave
from .utils import get_path, is_collection, get_image_list, temp_training_dir
import bayesian_model
import eigenfaces_model

blueprint = Blueprint('imagetagger', __name__, url_prefix='/imagetagger',
                      template_folder='templates', static_folder='static')

ch = None
actions = {0:'edit', 1:'create'}

@blueprint.route('/record/<int:id_bibrec>/<int:id_image>/<int:action>', methods=['GET', 'POST'])
@blueprint.route('/record/<int:id_bibrec>/<int:action>', methods=['GET', 'POST'])
def editor(id_bibrec, action, id_image=-1, width=800):
    """edit or create interface for photo tagging
    width -- image width for display
    """
    global ch
    path, full_path = get_path(id_bibrec, id_image)
    from .template_context_functions.tfn_imagetagger_overlay import template_context_function
    if(id_image != -1):
        current_url = '/record/'+str(id_bibrec)+"/"+str(id_image)
    else:
        current_url = '/record/'+str(id_bibrec)

    if ch == None:
        print "loading collection handler..."
        ch = CollectionHandler(image_list=get_image_list(id_bibrec), collection_id=id_bibrec)
        print "done"
		
    if not is_collection(id_bibrec):
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
            save_tags(id_bibrec, tags, action)
            #run_training(0)
            return template_context_function(id_bibrec, path, tags=already_tagged, faces=potential_tags, width=width, current_url=current_url, action=action)
        else:
            if actions[action] == 'edit':
                result = get_json(id_bibrec)
                potential_tags = find_faces(full_path, width=width, already_tagged=json_to_array(result))
                return template_context_function(id_bibrec, path, tags=json_to_array(result), faces=potential_tags, width=width, current_url=current_url, action=action)
            elif actions[action] == 'create':
                result = get_json(id_bibrec)
                potential_tags = find_faces(full_path, width=width, already_tagged=json_to_array(result))
                #suggestions = CollectionHandler().suggest_one_image(full_path, width)
                suggestions = []
                return template_context_function(id_bibrec, path, tags=json_to_array(result), faces=potential_tags, width=width, current_url=current_url, action=action, suggested=suggestions)
            else:
                potential_tags = find_faces(full_path, width=width)
                #suggestions = CollectionHandler().suggest_one_image(full_path, width)
                return template_context_function(id_bibrec, path, faces=potential_tags, width=width, current_url=current_url, action=action, suggested=suggestions)
    else:
        if id_image == -1:
            return ch;
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
                save_tags(id_bibrec, tags, action, id_image=id_image)
                ch.add(face_tags, id_image)
                return template_context_function(id_bibrec, path, tags=already_tagged, width=width, action=action, current_url=current_url)
            else:
                if actions[action] == 'edit':
                    result = get_json(id_bibrec, id_image)  
                    jsontags = json_to_array(result)
                    suggestions = ch.get_suggestions(id_image)
                    if len(suggestions) > 0:  
                        if len(jsontags) == 0:                
                            jsontags = suggestions
                        else:
                            jsontags.append(suggestions)
                    potential_tags = find_faces(full_path, width=width, already_tagged=jsontags)
                    return template_context_function(id_bibrec, path, tags=json_to_array(result), faces=potential_tags, width=width, suggested=suggestions, action=action, current_url=current_url)
                elif actions[action] == 'create':
                    result = get_json(id_bibrec, id_image)
                    jsontags = json_to_array(result)
                    suggestions = ch.get_suggestions(id_image) 
                    if len(suggestions) > 0:                  
                        if len(jsontags) == 0:                
                            jsontags = suggestions
                        else:
                            jsontags.append(suggestions)
                    potential_tags = find_faces(full_path, width=width, already_tagged=jsontags)
                    return template_context_function(id_bibrec, path, tags=json_to_array(result), faces=potential_tags, width=width, suggested=suggestions, action=action, current_url=current_url)
                else:
                    suggestions = ch.get_suggestions(id_image)                  
                    potential_tags = find_faces(full_path, width=width, already_tagged=suggestions)
                    return template_context_function(id_bibrec, path, faces=potential_tags, width=width, suggested=suggestions, action=action, current_url=current_url)

@blueprint.route('/record/<int:id_bibrec>/delete', methods=['GET', 'POST'])
@blueprint.route('/record/<int:id_bibrec>/<int:id_image>/delete', methods=['GET', 'POST'])
def delete(id_bibrec, id_image=-1):
    """tag deleting (the whole tags for a photo)"""
    if id_image == -1:
        db.session.query(ItgTAG).filter_by(id_bibrec=id_bibrec).delete()
        db.session.query(ItgNormalizedFace).filter_by(id_bibrec=id_bibrec).delete()
        db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).delete()
        redirect(url_for("./record/"+id_bibrec+"/1"))
    else:
        db.session.query(ItgTAG).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
        db.session.query(ItgNormalizedFace).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
        db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
        redirect(url_for("./record/"+id_bibrec+"/"+id_image+"/1"))

@blueprint.route('/record/<int:id_bibrec>/<int:id_image>')
@blueprint.route('/record/<int:id_bibrec>')
def get_tags_for_image(id_bibrec, id_image=-1):
    """request the json file from the DB"""
    if id_image == -1:
        result = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec)
        for res in result:
            return json.loads(res.content)
    else:
        result = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image)
        for res in result:
            return json.loads(res.content)

@blueprint.route('/seedb')
def seedb():
    from .template_context_functions.tfn_imagetagger_overlay import template_context_function
    res = db.session.query(ItgTAG);
    text = ""
    for r in res:
        text = text + "id"+ str(r.id)+","+str(r.title)+","+str(r.id_bibrec)+","+str(r.x)+"<br/>"
    text = text + "json<br/>"
    res = db.session.query(ItgTAGJson);
    for r in res:
        text = text + "id"+ str(r.id)+","+str(r.id_bibrec)+","+r.content+"<br/>"
    return template_context_function(None, '', faces=[], suggested=[], text=text)

@blueprint.route('/deletedb')
def deletedb():
    db.session.query(ItgTAG).delete()
    db.session.query(ItgNormalizedFace).delete()
    db.session.query(ItgTAGJson).delete()
    return "deleted"

def save_tags(id_bibrec, tags, action, id_image=-1):
    """tag saving in the DB: 
	each separately
	+a json file per image
	+if it's a face: the normalized face (for training)
	"""
    if id_image == -1:
        id_image = id_bibrec
    for_json = []
    db.session.query(ItgTAG).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
    if actions[action] == 'edit':
        for tag in tags:
            merged_object = db.session.merge(ItgTAG(id=tag.id, id_image=id_image, title=tag.title, x=tag.x, y=tag.y, width=tag.w, height=tag.h, tag_type=tag.type, image_width=tag.image_width, id_bibrec=id_bibrec))
            db.session.flush()
            for_json.append(Imagetag(db_object=merged_object))
            path, full_path = get_path(id_bibrec, id_image)
            normalizeAndSave(full_path, tempDir, tag, id_bibrec, id_image)
    else:
        for tag in tags:
            new_obj = ItgTAG(title=tag.title, id_image=id_image, x=tag.x, y=tag.y, width=tag.w, height=tag.h, tag_type=tag.type, image_width=tag.image_width, id_bibrec=id_bibrec)
            merged = db.session.merge(new_obj)
            db.session.flush()
            for_json.append(Imagetag(db_object=merged))
            path, full_path = get_path(id_bibrec, id_image)
            normalizeAndSave(full_path, tempDir, tag, id_bibrec, id_image)

    json_file = to_json(id_bibrec ,for_json)
    db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
    db.session.merge(ItgTAGJson(id_bibrec=id_bibrec, id_image=id_image, content=json_file.data))
    db.session.flush()
    db.session.commit()

def run_training(method):
    temp_dir = temp_training_dir
    if method == 0:
        res = eigenfaces_model.run_training()
        if res:
            eigenfaces_model.save_recognizer(temp_dir+'/eigen.xml')
    else:
        bayesian_model.run_training()
	


