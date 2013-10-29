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
	Face recognition based on eigenfaces, using amodified version of opencv's implementation
	see Lawrence Sirovich and Michael Kirby. Low-dimensional procedure for the characterization of human faces.
"""

from eigenfaces import *
from face_normalization import normalizeFor
from invenio.ext.sqlalchemy import db
from .models import ItgTAG
from .utils import temp_training_dir, get_path

eigenfaces_recognizer = Eigenfaces2()

def load_recognizer(path):
	"""load an already trained model from an xml file
	"""
	return eigenfaces_recognizer.load(path)

def save_recognizer(path):
	"""save model after training"""
	eigenfaces_recognizer.save(path)

def check_format(image):
	if image[-3:] != 'pgm':
		img = cv2.imread(image, 0)
		cv2.imwrite(image[:-4]+".pgm", img)
		return image[:-4]+".pgm"
	return image

def run_training():
	"""training of the recognizer using the faces tagged previously and stored in the database"""
	tags = db.session.query(ItgTAG).filter_by(tag_type="face")
	images = []
	labels = []
	for tag in tags:
		path, full_path = get_path(tag.id_bibrec, tag.id_image)
		full_path = check_format(full_path)
		tag_path = temp_training_dir+tag.id+".pgm"
		norm = normalizeFor(full_path, tag_path, tag, 1)
		if norm:
			if len(images) == 0:
				images = [tag_path]
				labels = [tag.id]
			else:
				images.append(tag_path)
				labels.append(tag.id)
	res = eigenfaces_recognizer.train(images, labels)
	return res

def predict(image, n=1):   
	"""retrieve the n best possibilities for the considered tag"""
	if not eigenfaces_recognizer.isTrained():
		return[]
	return eigenfaces_recognizer.predictN(image, n)
