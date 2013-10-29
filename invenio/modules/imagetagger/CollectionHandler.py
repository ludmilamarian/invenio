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
    invenio.modules.imagetagger.CollectionHandler
    ------------------------------

    CollectionHandler class.
"""

from invenio.ext.sqlalchemy import db
from .models import ItgTAG
from .face_in_collection_similarity import find_faces_in_collection
from .imagetag import *
from .suggestion import *
import eigenfaces_model
import bayesian_model
from .face_normalization import normalizeFor
from .utils import get_path, bpath, epath, n, method, path_frontal, path_torso
import cv2
import cv2.cv as cv

#frontal face detector for the recognition
face_detector = cv2.CascadeClassifier(path_frontal)

class CollectionHandler:
	"""class for handling a collection of images
	contains:
		list of tagged and not yet tagged images
		suggestions of tags for the untagged images
		data for the recognizers
	"""
	def __init__(self, image_list=[], collection_id="", torso_path=path_torso, image_width=800):
		if len(image_list) > 0:
			self.untagged = image_list
			self.tagged = []
			self.collection_id = collection_id
			self.tag_list = {}
			self.suggestion_list = {}
			self.torso_path = torso_path
			self.image_width = image_width
			print "loading ml models"
			self.with_ml = self.init_ml_recognizer(epath, bpath[0], bpath[1], method)
			print "fetching tags in DB"
			self.fetch_tags_in_db()
			print "starting suggestions"
			self.suggest()
		
	def init_ml_recognizer(self, path1, path2="", path3="", method="eigen"):
		"""load the recognizers from file
		path1 -- path to the eigenfaces model file
		path2 -- path to the bayesian intrapersonal file
		path3 -- path to the bayesian extrapersonal file
		"""
		if method == "eigen":
			from eigenfaces_model import load_recognizer
			return load_recognizer(path1)
		else:
			from bayesian_model import load_recognizer
			return load_recognizer(path1, path2, path3)

	def fetch_tags_in_db(self):
		"""get the tags for the collection"""
		tags = db.session.query(ItgTAG).filter_by(id_bibrec=self.collection_id)
		for tag in tags:
			if str(tag.id_image) not in self.tagged:
				self.tagged.append(str(tag.id_image))
				self.tag_list[str(tag.id_image)] = [Imagetag(db_object=tag)]
				del self.untagged[self.untagged.index(str(tag.id_image))]
			else:
				if str(tag.id_image) in self.tag_list.keys():
					self.tag_list[str(tag.id_image)].append(Imagetag(db_object=tag))
				else:
					self.tag_list[str(tag.id_image)] = [Imagetag(db_object=tag)]
		for image in self.tagged:
			print 'suggesting ', image, self.tag_list[image]
			self.suggest_with_collection(image, self.tag_list[image])

	def suggest(self):
		if self.with_ml:
			self.suggest_with_ml()
		self.suggest_with_collection()
		
	def suggest_with_ml(self):
		"""Suggestion using data found in the database
		1) detect frontal faces
		2) normalize the faces 
		3) find a correspondence using the eigenfaces or bayesian model
		4) append to the suggestion list
		"""
		if method == "eigen":
			from eigenfaces_model import predict
			type = 1
			n = 1
			suffix = ".pgm"
		else:
			from bayesian_model import predict
			type = 0	
			suffix = ".sfi"	
		for image in self.untagged.keys():
			path, full_path = get_path(self.collection_id, int(image))
			gray = cv2.imread(full_path, 0)
			if gray != None:
				h, w =gray.shape[:2]
				faces = face_detector.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 2, minSize = (1,1), flags = cv.CV_HAAR_SCALE_IMAGE)
				for face in faces:
					normalizeFor(full_path, full_path[:-4]+suffix, Imagetag(array=face, image_width=w), type, is_db=False)
					tag = predict(full_path[:-4]+suffix, n)
					if len(tag) > 0:
						if type == "bayesian":
							tag = tag[0]
						dbTag = db.session.query(ItgTAG).filter_by(id=tag).first()
						slist = self.suggestion_list[image]
						if slist == None or len(slist) == 0:
							self.suggestion_list[image] = Suggestion(Imagetag(tag_id=-1,tag_type="face",title=dbTag.title,x=face[0],y=face[1],w=face[2],h=face[3],image_width=w), 0, dbTag.id)

	def suggest_one_image(self, image, width):
		"""Static method for suggestion in one single image"""
		self.init_ml_recognizer(epath, bpath[0], bpath[1], method)
		
		if method == "eigen":
			from eigenfaces_model import predict
			type = 1
			n = 1
			suffix = ".pgm"
		else:
			from bayesian_model import predict
			type = 0	
			suffix = ".sfi"	
		gray = cv2.imread(image, 0)
		h, w = gray.shape[:2]
		faces = face_detector.detectMultiScale(gray, scaleFactor = 1.2, minNeighbors = 2, minSize = (1,1), flags = cv.CV_HAAR_SCALE_IMAGE)
		result = []
		for face in faces:
			normalizeFor(image, image[:-4]+suffix, Imagetag(array=face, image_width=w), type, is_db=False)
			tag = predict(image[:-4]+suffix, n)
			if type == "bayesian":
				tag = tag[0]
			dbTag = db.session.query(ItgTAG).filter_by(id=tag).first()
			if len(result) == 0:
				result = [Imagetag(tag_type="face", title=dbTag.title, x=face[0], y=face[1], w=face[2], h=face[3], image_width=w).to_array(width)]
			else:
				result.append(Imagetag(tag_type="face", title=dbTag.title, x=face[0], y=face[1], w=face[2], h=face[3], image_width=w).to_array(width))
		return result

	def to_path_list(self, id_list):
		result = []
		for id_image in id_list:
			path, full_path = get_path(self.collection_id, id_image)
			if len(result) == 0:
				result = [full_path]
			else:
				result.append(full_path)
		return result
					
	def suggest_with_collection(self, id_image=-1, tag_list=[]):
		"""suggestion using the tagged pictures and the tag list of this collection"""
		if int(id_image) == -1 and self.with_ml: #no new tags added, we are using ml suggestions and propagate them to profile faces
			temp = self.suggestion_list.copy()
			for image in temp.keys():
				if image in self.untagged:
					temp_img_list = self.untagged[:]
					del temp_img_list[temp_img_list.index(image)]
					path, full_path = get_path(self.collection_id, int(image))
					tags = find_faces_in_collection(full_path, temp[image].tag.to_array(), temp_img_list, self.torso_path, self.image_width, collection_id=self.collection_id)
					for img in tags.keys():
						self.combine_tags(img, tags[img])

		else:#list of tags to study
			path, full_path = get_path(self.collection_id, int(id_image))
			tags = find_faces_in_collection(full_path, tag_list, self.untagged, self.torso_path, self.image_width, suggestion=True, collection_id=self.collection_id)
			for img in tags.keys():
				self.combine_tags(img, tags[img])

	def combine_tags(self, image, new_tags):
		"""check for suggestions that overlap"""
		if str(image) not in self.suggestion_list:
			self.suggestion_list[str(image)] = []
		slist = self.suggestion_list[str(image)]
		for suggestion in new_tags:
			if suggestion not in slist:
				slist.append(suggestion)
			else:#keep the best
				if slist.index(suggestion).distance > suggestion.distance:
					slist[slist.index(suggestion)] = suggestion

	def new_tags_in_list(self, original_tags, new_tags):
		"""compare two sets of tags and retrieve the freshly added tags"""
		result = []
		for tag in new_tags:
			if tag not in original_tags:
				if len(result) == 0:
					result = [tag]
				else:
					result.append(tag)
		return result

	def add(self, tags, id_image):
		"""called when an image has been tagged and saved
		propagate the suggestion to the untagged photos
		"""
		if str(id_image) in self.untagged:
			new_tags = tags
			self.tagged.append(str(id_image))
			self.tag_list[str(id_image)] = tags
			del self.untagged[self.untagged.index(str(id_image))]
		else:
			new_tags = self.new_tags_in_list(self.tag_list[str(id_image)], tags)
			self.tag_list[str(id_image)] = tags

		self.suggest_with_collection(str(id_image), new_tags)
		
	def to_array_list(self, llist):
		"""formatting for display"""
		result = []
		for tag in llist:
			result.append(tag.to_array())
		return result

	def get_suggestions(self, id_image=-1):
		"""called when an image is about to be tagged by the user"""
		if int(id_image) == -1:
			return self.suggestion_list;
		if str(id_image) in self.suggestion_list.keys():
			return self.to_array_list(self.suggestion_list[str(id_image)])
		else:
			return []
