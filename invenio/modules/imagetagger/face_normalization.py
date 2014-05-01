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

""" face normalization: for face recognition, faces need to be the same size and have the eyes and mouth at the same location"""

import normalization
import cv2
import cv2.cv as cv
import os
from .imagetag import *
from invenio.ext.sqlalchemy import db
from .models import ItgNormalizedFace
from .utils import path_eyes

#eye detector using OpenCV
eye_cascade = None

def open_cascade(path=path_eyes):
	"""open the face detector from a path to the xml file describing the model"""
	global eye_cascade
	eye_cascade = cv2.CascadeClassifier(path)


def find_eyes(gray):
	"""eye detection that filters false detections and find which rectangles are the left and right eyes
	gray -- grayscale image
	"""
	percentage_area = 0.5
	if eye_cascade == None:
		open_cascade()
	gray = cv2.pyrUp(gray)
	result = eye_cascade.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 2, minSize = (1,1), flags = cv.CV_HAAR_SCALE_IMAGE)
	left = []
	right = []
	h, w = gray.shape[:2]
	if result == () or len(result) < 2:
		return [], []
	else:
		most_left = -1
		most_right = -1
		tmp = []
		for res in result:
			center = [res[0]+res[2]/2,res[1]+res[3]/2]
			if center[1] < h * percentage_area:
				if len(tmp) < 1:
					tmp = [center]
				else:
					tmp.append(center)
				if most_left == -1 or tmp[most_left][0] > center[0]:
					most_left = len(tmp) - 1
				if most_right == -1 or tmp[most_right][0] < center[0]:
					most_right = len(tmp) - 1
		if len(tmp) > 1:
			return tmp[most_right], tmp[most_left]
		return [], []

def readNormalizedFile(path):
	"""read file for saving in the DB"""
	nFile = open(path, 'r')
	content = nFile.read()
	nFile.close()
	os.unlink(path)
	return content

def check_format(image):
	"""The bayesian api only accepts pgm images so we need to check and convert"""
	if image[-3:] != 'pgm':
		img = cv2.imread(image, 0)
		cv2.imwrite(image[:-4]+".pgm", img)
		return image[:-4]+".pgm"
	return image
	
def normalizeFor(imagePath, outputPath, tag, type, is_db=True):
	"""normalization
	imagePath -- path to the image to normalize (this is the whole image, we need to specifiy the face position with the param tag)
	outputPath -- path to the normalized image that will be created
	tag -- rectangle [x, y, w, h] specifying the face position
	type -- recognizing method (the output format is different depending on the method, bayesian or eigenfaces)
	is_db -- format matter, if true tag is of the type ItgTAG, if false it is of the type Imagetag
	"""

	imagePath = check_format(imagePath)
	gray = cv2.imread(imagePath, 0)
	h, w = gray.shape[:2]
	if is_db:
		factor = float(w) / float(tag.image_width)
		face = gray[int(tag.y*factor):int((tag.y+tag.height)*factor),int(tag.x*factor):int((tag.x+tag.width)*factor)]
	else:
		factor = float(w) / float(tag.image_width)
		face = gray[int(tag.y*factor):int((tag.y+tag.h)*factor),int(tag.x*factor):int((tag.x+tag.w)*factor)]
	right, left = find_eyes(face)
	if len(right) > 1:
		print 'outpath',outputPath
		normalization.normalizeImageAndWrite(imagePath, outputPath, float(left[0])/2., float(left[1])/2., float(right[0])/2., float(right[1])/2., type)
		return True
	return False

def normalizeAndSave(imagePath, tempOutputDir, tag, id_bibrec, id_image):
	"""called after a new tag is added to the DB: the face is cut, normalized and saved in the DB
	imagePath -- path to the image containing the face to normalize
	tempOutputDir -- temporary directory where to write the normalized face
	tag -- position of the face in the image
	id_bibrec -- record id
	id_image -- image id
	"""
	gray = cv2.imread(imagePath, 0)
	h, w = gray.shape[:2]
	factor = float(w) / float(tag.image_width)
	face = gray[int(tag.y*factor):int((tag.y+tag.h)*factor),int(tag.x*factor):int((tag.x+tag.w)*factor)]
	right, left = find_eyes(face)
	if len(right) > 1:
		outPath = os.path.join(tempOutputDir, imagePath[:-4]+".sfi")
		imagePath = check_format(imagePath)
		normalization.normalizeImageAndWrite(imagePath, outPath, float(left[0]), float(left[1]), float(right[0]), float(right[1]), 0)
		content = readNormalizedFile(outPath)
		db.session.query(ItgNormalizedFace).filter_by(id_tag=tag.id).delete()
		db.session.add(ItgNormalizedFace(id_tag=tag.id, id_bibrec=id_bibrec, id_image=id_image, content=content))
		db.session.flush()
    	db.session.commit()
