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
from .models import *


def write_json(tags, path='/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/json/imagetagger/json.txt'):
	"""function for testing"""
	response = {}
	for tag in tags:
		response[str(tag.id)] = tag.to_json()
	response2 = {}
	response2['tags'] = response
	result = jsonify([[0, response2]])
	json_file = open(path, "w")
	json_file.write(result.data)
	json_file.close()
	return result

def to_json(record_id, tags_array):
	"""tag list to json format"""
	response = {}
	for tag in tags_array:
		response[str(tag.id)] = tag.to_json()
	response2 = {}
	response2['tags'] = response
	result = jsonify([[record_id, response2]])
	return result

def get_json(id_bibrec, id_image=-1):
	from invenio.ext.sqlalchemy import db
	if id_image != -1:
		json_string = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).filter_by(id_image=id_image).all()
	else:
		json_string = db.session.query(ItgTAGJson).filter_by(id_bibrec=id_bibrec).all()
	if len(json_string) > 0:
		return json.loads(json_string[0].content)
	else:
		return []

def read_json(path='/home/cern/.virtualenvs/invenionext/src/invenio/invenio/modules/imagetagger/static/json.txt'):
	"""function for testing"""
	try:
		json_file = open(path, 'r')
	except IOError:
		print "oups"
	strj = json.loads(json_file.read())
	return strj

def json_exists(path='/home/cern/.virtualenvs/invenionext/src/invenio/invenio/modules/imagetagger/static/json.txt'):
	"""function for testing"""
	try:
		open(path)
	except IOError:
		return False
	return True

def json_remove(path):
	"""function for testing"""
	if os.path.isfile(path):
		os.remove(path)


def json_to_array(tags, image_width=0):
	"""json format to tag list for html display"""
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
