# -*- coding: utf-8 -*-
#
## This file is part of Invenio.
## Copyright (C) 2011, 2012 CERN.
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
## 59 Temple Place, Suite 330, Boston, MA 02D111-1307, USA.

"""
ImageTagger database models.
"""

# General imports.
from invenio.ext.sqlalchemy import db
from sqlalchemy.ext.hybrid import hybrid_property

# Related models
from invenio.modules.records.models import Record as Bibrec

# Create your models here.

class ItgTAG(db.Model):
    """Represents a tag"""
    __tablename__ = 'itgTAG'
    id = db.Column(db.Integer(15, unsigned=True), primary_key=True,
                   autoincrement=True)

    id_bibrec = db.Column(db.Integer(15, unsigned=True),
                          db.ForeignKey(Bibrec.id),
                          nullable=False,
                          index=True)
    id_image = db.Column(db.Integer(15, unsigned=True), nullable=False)
    x = db.Column(db.Integer(5, unsigned=True), 
    				nullable=False)
    y = db.Column(db.Integer(5, unsigned=True), 
    				nullable=False)
    width = db.Column(db.Integer(5, unsigned=True), 
    				nullable=False)
    height = db.Column(db.Integer(5, unsigned=True), 
    				nullable=False)
    title = db.Column(db.String(255),
                     nullable=False,
                     server_default='',
                     index=True)
    image_width = db.Column(db.Integer(5, unsigned=True), 
    				nullable=False)
    tag_type = db.Column(db.Integer(1, unsigned=True), 
    				nullable=False)


    bibrec = db.relationship(Bibrec,
                             backref=db.backref('image_tags_association',
                                                cascade='all'))


    TYPE_NAMES = {
        0: 'face',
        1: 'object',
        2: 'other',
    }

class ItgTAGJson(db.Model):
    """Represents an image's json file with tags"""
    __tablename__ = 'itgTAGJson'
    id = db.Column(db.Integer(15, unsigned=True), primary_key=True,
                   autoincrement=True)

    id_bibrec = db.Column(db.Integer(15, unsigned=True),
                          db.ForeignKey(Bibrec.id),
                          nullable=False,
                          primary_key=True,
                          index=True)

    id_image = db.Column(db.Integer(15, unsigned=True),
                          nullable=False,
                     index=True)

    content = db.Column(db.String(10000),
                     nullable=False)
					 
    title = db.Column(db.String(255),
                     nullable=False,
                     server_default='',
                     index=True)

    bibrec = db.relationship(Bibrec,
                             backref=db.backref('json_tags_association',
                                                cascade='all'))

class ItgNormalizedFace(db.Model):
    """Represents the tag of a face, normalized and eyes aligned"""
    __tablename__ = 'itgNormalizedFace'
    id = db.Column(db.Integer(15, unsigned=True), primary_key=True,
                   autoincrement=True)

    id_tag = db.Column(db.Integer(15, unsigned=True),
                          db.ForeignKey(ItgTAG.id),
                          nullable=False,
                          primary_key=True,
                          index=True)

    id_bibrec = db.Column(db.Integer(15, unsigned=True),
                          nullable=False,
                          primary_key=True,
                          index=True)

    id_image = db.Column(db.Integer(15, unsigned=True),
                          nullable=False,
                     index=True)

    content = db.Column(db.LargeBinary,
                     nullable=False)

    # bibrec = db.relationship(Bibrec,
    #                          backref=db.backref('json_tags_association',
    #                                             cascade='all'))

    itgtag = db.relationship(ItgTAG,
                             backref=db.backref('face tag association',
                                                cascade='all'))