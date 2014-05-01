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

"""Json encoding and decoding"""

import os
from flask import url_for, jsonify, json
from .models import ItgTAGJson

def to_json(record_id, tags_array):
	"""tag list to json format
	
	record_id -- bibrec id
	tags_array -- array of Imagetag objects
	"""
	response = {}
	for tag in tags_array:
		response[str(tag.id)] = tag.to_json()
	response2 = {}
	response2['tags'] = response
	result = jsonify([[record_id, response2]])
	return result
	

def get_json(id_bibrec, id_image=-1):
	"""get the json file corresponding to the record and image ids"""
	from invenio.ext.sqlalchemy import db
	if id_image != -1:
		json_string = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).all()
	else:
		json_string = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).all()
	if len(json_string) > 0:
		return json.loads(json_string[0].content)
	else:
		return []


def json_to_array(tags, image_width=0):
	"""json format to tag list for html display
	
	tags -- json content retrieved from the DB
	image_width -- width of the image that is about to be displayed
	
	returns an array of arrays of the form [id, title, x, y, w, h, h+5, type, image_width]
	"""
	if len(tags) == 0:
		return []
	result = []
	for ind in tags[tags.keys()[0]]['tags'].keys():
		tab = tags[tags.keys()[0]]['tags']
		if image_width == 0:
			result.append([ind, tab[ind]['title'], int(float(tab[ind]['x'])), int(float(tab[ind]['y'])), int(float(tab[ind]['w'])), int(float(tab[ind]['h'])), int(float(tab[ind]['h']))+5, tab[ind]['type'], int(float(tab[ind]['image_width']))])
		else:
			pass
	return result
