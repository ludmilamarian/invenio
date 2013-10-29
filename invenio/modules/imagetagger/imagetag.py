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
    invenio.modules.imagetagger.imagetag
    ------------------------------

    Tag class.
"""

from .models import ItgTAG

class Imagetag:
	def __init__(self, tag_id=0, tag_type=0, title=0, x=0, y=0, w=0, h=0, image_width=0, array=[], db_object=None):
		if db_object is not None:
			self.id = db_object.id
			self.title = db_object.title
			self.x = int(db_object.x)
			self.y = int(db_object.y)
			self.w = int(db_object.width )
			self.h = int(db_object.height)
			self.type = db_object.tag_type
			self.image_width = int(db_object.image_width)
			self.id_image = int(db_object.id_image)
		else:
			if len(array) > 0:
				if len(array) > 4:
					self.id = tag_id
					self.title = array[0]
					self.x = int(array[1])
					self.y = int(array[2])
					self.w = int(array[3])
					self.h = int(array[4])
					self.type = array[5]
					self.image_width = int(array[6])
				else:
					self.id = -1
					self.title = ''
					self.x = int(array[0])
					self.y = int(array[1])
					self.w = int(array[2])
					self.h = int(array[3])
					self.type = "face"
					self.image_width = image_width
			else:
				self.id = tag_id
				self.type = tag_type
				self.title = title
				self.x = int(x)
				self.y = int(y)
				self.w = int(w)
				self.h = int(h)
				self.image_width = int(image_width)

	def __eq__(self, tag2):
		factor = self.image_width / tag2.image_width
		return self.x == int(tag2.x*factor)\
		 and self.y == int(tag2.y*factor) \
		 and self.w == int(tag2.w*factor) \
		 and self.h == int(tag2.h*factor)

	def to_array(self, image_width=0):
		factor =1
		if image_width != 0 and image_width != self.image_width:
			factor = float(image_width)/float(self.image_width)
		return [self.id, self.title, self.x, self.y, self.w, self.h, self.h+5, self.type, self.image_width]

	def to_json(self):
		return {'id':self.id, 'title':self.title, 'x':self.x, 'y':self.y, 'w':self.w, 'h':self.h, 'type':self.type, 'image_width':self.image_width}

	def to_opencv(self, factor=1):
		return [int(self.x*factor), int(self.y*factor), int(self.w*factor), int(self.h*factor)]
