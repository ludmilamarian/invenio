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

prefix = "/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/"
fake_bibrec = ["img/imagetagger/test_model.jpg", "img/imagetagger/test_test.jpg"]

#location of the two files from the bayesian recognizer training
bpath = ["", ""]
#location of the file from the eigenfaces recognizer training
epath = "/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/ml/eigen.xml"
#recognizing method
method = "eigen"
#parameter for the eigenfaces recognizer
n = 10
#threshold for the torso recognizer
th_torso = 280000. 
#path to the torso mask
path_torso = "/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/img/imagetagger/torso1.jpg"
#path to openCV basic face detector
path_frontal = "/home/cern/Downloads/opencv-2.4.6.1/data/haarcascades/haarcascade_frontalface_alt2.xml"
#path to openCV eye cascade
path_eyes = "/home/cern/Downloads/opencv-2.4.6.1/data/haarcascades/haarcascade_eye.xml"
#cascade list for complete face detection
path_cascades = "/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/cascades/"
method_cascades = "1"
list_cascades = [prefix+"15/"+"cascade"+method_cascades+"/cascade.xml", prefix+"30/"+"cascade"+method_cascades+"/cascade.xml", prefix+"45/"+"cascade"+method_cascades+"/cascade.xml", prefix+"60/"+"cascade"+method_cascades+"/cascade.xml", prefix+"75/"+"cascade"+method_cascades+"/cascade.xml", prefix+"90/"+"cascade"+method_cascades+"/cascade.xml"]
#temporary directory to hold training data
temp_training_dir = "/home/cern/.virtualenvs/it/src/invenio/invenio/modules/imagetagger/static/ml"

def get_path(id_record, id_image):
    #return [f.get_full_path() for f in BibRecDocs(id_record).list_bibdocs()[0].list_latest_files() if f.subformat == '']
    # from invenio.modules.records.models import Record as Bibrec
    # record = Bibrec.query.get(id_record)
    # print dir(record)
    #return image_path, image_model_path
	return fake_bibrec[id_image%len(fake_bibrec)], prefix+fake_bibrec[id_image%len(fake_bibrec)]

def is_collection(id_record):
    if id_record == 1:
        return False 
    else:
        return True

def get_image_list(id_collection):
    """returns image ids for a corresponding bib_rec"""
    #return range(len(fake_bibrec))
    res = []
    for i in range(len(fake_bibrec)):
    	if len(res) == 0:
    		res = [str(i)]
    	else:
    		res.append(str(i))
    return res