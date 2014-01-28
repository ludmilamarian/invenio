import pylire
import Image
import os

from cStringIO import StringIO

from image_similarity_config import CFG_IMAGE_SIMILARITY_INDEX_FOLDER, \
    CFG_IMAGE_SIMILARITY_BATCH_SIZE, \
    CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES, \
    CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES

from image_similarity_utils import get_image_paths_with_rec_ids, \
    get_image_path_from_rec_id


pylire.initVM()
# how many images do we preprocess and index at a time?
batch_size = CFG_IMAGE_SIMILARITY_BATCH_SIZE
pylire_features = list(set.union(set(CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES), set(CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES))) #['',''] # Union of cfg_img_sim_dup_ft and _trans_ft, i.e. all pylire features
handler = pylire.InvenioHandler() 

# def preprocessImage(recId):
#     #TODO load image given recId
#     img = Image.open(recId)
#     img = img.convert("RGB")
#     name = recId
#     img.save(name+'.jpg','JPEG',quality=100) #by default, quality is 75%


'''for each recId in recIds:
add to pylire.HashMap pathToImage - recId

then
for feature in set.union([lists of features]) (these are all our pylire features)
add record(recid)'s preprocessed image (subformat=';lire') to indexes
'''
def initial_index_setup():   
    recids = get_image_paths_with_rec_ids() # defined in InvenioUtils.py
    batches_processed = 0
    while batches_processed*batch_size < len(recids):
        path2Id = pylire.HashMap()
        for recid in recids.keys()[batches_processed*batch_size:(batches_processed+1)*batch_size]:
            path2Id.put(recids[recid], str(recid))

        handler.index(CFG_IMAGE_SIMILARITY_INDEX_FOLDER, pylire_features, path2Id, True)
        batches_processed = batches_processed + 1





def delete_from_indexes(recid): 
    handler.deleteFromIndexes(CFG_IMAGE_SIMILARITY_INDEX_FOLDER, str(recid), pylire_features)


 
def update_entry_in_indexes(recid):
    path_to_image = get_image_path_from_rec_id(recid)
    handler.updateIndexes(CFG_IMAGE_SIMILARITY_INDEX_FOLDER, path_to_image, str(recid), pylire_features)


def append_to_indexes(recids):
    batches_processed = 0
    while batches_processed*batch_size < len(recids):
        path_and_id = pylire.HashMap()
        for recid in recids[batches_processed*batch_size:(batches_processed+1)*batch_size]:
            path_and_id.put(get_image_path_from_rec_id(recid)[0], str(recid))
            handler.index(CFG_IMAGE_SIMILARITY_INDEX_FOLDER, pylire_features, path_and_id, False)
        batches_processed += 1
