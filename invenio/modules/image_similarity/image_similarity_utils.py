from invenio.flaskshell import *
from invenio import search_engine
from invenio.bibdocfile import BibRecDocs

from image_similarity_config import CFG_IMAGE_SIMILARITY_IMAGE_COLLECTIONS


def get_image_paths_with_rec_ids():
    recids = list()
    for collection in CFG_IMAGE_SIMILARITY_IMAGE_COLLECTIONS:
        recids.extend(search_engine.get_collection_reclist(collection).tolist())
    filepaths = list()
    for recid in recids:
        filepaths.extend(get_image_path_from_rec_id(recid))
    return dict(zip(recids, filepaths))


# TODO!!! Change subformat check to ';lire'
def get_image_path_from_rec_id(recid):
    return [f.get_full_path() for f in BibRecDocs(recid).list_bibdocs()[0].list_latest_files() if f.subformat == '']
