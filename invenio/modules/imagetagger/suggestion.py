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

import cv2
import cv2.cv as cv
import numpy as np
from imagetag import Imagetag

class Suggestion:
	""" class used in CollectionHandler, associates a tag with its source and its measure of confidence
	
	tag -- Imagetag object
	distance -- value returned using the recognition method (either bayesian, eigenfaces or recognition from clothes)
	src -- source of the suggestion (machine learning methods or clothes comparison methods
	"""
	def __init__(self, tag, distance, src):
		self.tag = tag
		self.distance = distance
		self.src = src

	def __eq__(self, s2):
		result = cv2.groupRectangles(np.array([self.tag.to_opencv(), s2.tag.to_opencv()]).tolist(), 0)
		return (len(result) == 1)
		
	def to_array(self, width=0):
		return self.tag.to_array(width)