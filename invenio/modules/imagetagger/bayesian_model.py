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
	Face recognition based on bayes law, using csu's implementation
	see http://www.cs.colostate.edu/evalfacerec/papers/teixeiraThesis.pdf
"""

from .bayesian import *
import eigenfaces_model
from invenio.ext.sqlalchemy import db
from .models import ItgNormalizedFace
from .utils import get_path
import os
import cv2
import cv2.cv as cv

bayesian_recognizer = BayesianRecognizer()

def load_recognizer(pathIntra, pathExtra, pathEigen):
	"""load an already trained model from files:
	pathIntra -- intrapersonal subspace file
	pathExtra -- extrapersonal subspace file
	pathEigen -- eigenfaces model file
	"""
	res = bayesian_recognizer.load(pathIntra, pathExtra)
	if res:
		res = eigenfaces_model.load_recognizer(pathEigen)
	return res

def save_recognizer(pathIntra, pathExtra, pathEigen):
	"""save model after training"""
	bayesian_recognizer.save(pathIntra, pathExtra)
	eigenfaces_model.save_recognizer(pathEigen)

def write_image(directory, content, id):
	"""write the content stored in the DB in a file for training"""
	path = os.path.join(directory, str(id)+".sfi")
	file = open(path, "w")
	file.write(content)
	file.close()
	
def clean_directory(directory):
	"""erase all the temporary files"""
	for the_file in os.listdir(directory):
		file_path = os.path.join(directory, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception, e:
			print e
	
def run_training(tempDir):
	"""training of the recognizer using the faces tagged previously
	tempDir -- temporary directory for writing normalized images
	"""
	description_file = open(os.path.join(tempDir, "imageList.txt"), "w")
	images = db.session.query(ItgNormalizedFace).order_by(ItgNormalizedFace.title)
	previous_title = ""
	for image in images:
		if previous_title != "" and previous_title != image.title:
			description_file.write("\n")
		write_image(tempDir, image.content, image.id_tag)
		description_file.write(str(image.id_tag)+".sfi ")
		previous_title = image.title
	description_file.close()
	bayesian_recognizer.train(os.path.join(tempDir, "imageList.txt"), tempDir)
	clean_directory(tempDir)
	
def get_possibilities(possibilities, tempDir):
	"""the Eigenfaces method retrieves the tag id of the first n best choices
	this method gets the normalized corresponding face from the DB
	"""
	image_list = []
	for possibility in possibilities[0]:
		result = db.session.query(ItgNormalizedFace).filter_by(id_tag=possibility)
		for res in result:
			write_image(tempDir, res.content, res.id_tag)
			image_list.append(os.path.join(directory, str(id)+".sfi"))
			break
	return image_list
		

def predict(image, n, tempDir):  
	"""face recognition based on machine learning
	1) get the n best choices using the eigenfaces method
	2) find the best choice among these n using the bayesian method
	"""
	possibilities = eigenfaces_model.predict(image, n)
	result = bayesian_recognizer.predict(image, get_possibilities(possibilities))
	clean_directory(tempDir)
	return possibilities[0][result]