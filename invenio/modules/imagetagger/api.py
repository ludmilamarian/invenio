# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013, 2014 CERN.
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

import cv2
import numpy as np
import os

from flask import (render_template, request, flash, 
                   redirect, url_for, jsonify, Blueprint, 
                   json, escape)
from invenio.ext.sqlalchemy import db
from invenio.ext.template import render_template_to_string
from sqlalchemy.exc import SQLAlchemyError

from .json_utils import * #FIXME don't use * import
from .face_detection import find_faces
from .imagetag import Imagetag
from .models import ItgTAG
from .CollectionHandler import CollectionHandler
from .face_normalization import normalizeAndSave
from .utils import get_path, is_collection, get_image_list, temp_training_dir
import bayesian_model
import eigenfaces_model


def save_tags(id_bibrec, tags, id_image=-1):
    """tag saving in the DB: 
	each separately
	+a json file per image
	+if it's a face: the normalized face (for training)
	"""
    if id_image == -1:
        id_image = id_bibrec
    for_json = []
    db.session.query(ItgTAG).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
    for tag in tags:
        merged_object = db.session.merge(ItgTAG(id=tag.id, id_image=id_image, title=tag.title, x=tag.x, y=tag.y, width=tag.w, height=tag.h, tag_type=tag.type, image_width=tag.image_width, id_bibrec=id_bibrec))
        db.session.flush()
        for_json.append(Imagetag(db_object=merged_object))
        path, full_path = get_path(id_bibrec, id_image)
        normalizeAndSave(full_path, temp_training_dir, tag, id_bibrec, id_image)

    json_file = to_json(id_bibrec ,for_json)
    db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).delete()
    db.session.merge(ItgTAGJson(id_bibrec=id_bibrec, id_image=id_image, content=json_file.data))
    db.session.flush()
    db.session.commit()


def run_training(method):
    temp_dir = temp_training_dir
    if method == 0:
        res = eigenfaces_model.run_training()
        #if res:
        #    eigenfaces_model.save_recognizer(temp_dir+'/eigen.xml')
    else:
        bayesian_model.run_training(temp_training_dir)
        #bayesian_model.save_recognizer(path)