"""Invenio Image Similarity config parameters."""

# Selection of features to be used in exact duplicate search.
CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES = ["descriptorColorLayout","descriptorEdgeHistogram"]
# Corresponding decision boundaries. An AND operation will be performed: i.e. only duplicate if below all thresholds. Exact duplicate search should have lower boundaries. (these taken from cascade)
CFG_IMAGE_SIMILARITY_DUPLICATE_THRESHOLDS = {"descriptorColorLayout":0, "descriptorEdgeHistogram":0}

# Selection of features to be used in search for transformed duplicates. Our first detects scale changes. Our second detects colour and luminosity changes.
CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES = ["descriptorColorLayout","descriptorEdgeHistogram"]
# Corresponding decision boundaries. OR operation: i.e. transformed duplicate if any score below its threshold.
CFG_IMAGE_SIMILARITY_TRANSFORM_THRESHOLDS = {"descriptorColorLayout":6, "descriptorEdgeHistogram":37.565898895263672}


# Path to folder where images are preprocessed before sent to indexing
#CFG_IMAGE_SIMILARITY_IMAGE_FOLDER = '/home/michael/Test pylire/Images'
# Path to folder where indexes are stored
CFG_IMAGE_SIMILARITY_INDEX_FOLDER = '/home/michael/demo/Indexes'

# Invenio collections whose images are to be indexed
CFG_IMAGE_SIMILARITY_IMAGE_COLLECTIONS = ['Pictures']


# Batch size for indexing
CFG_IMAGE_SIMILARITY_BATCH_SIZE = 20


CFG_IMAGE_SIMILARITY_STANDARDIZE_FEATURES = ["descriptorColorLayout","descriptorEdgeHistogram"]

CFG_IMAGE_SIMILARITY_COMBINE_FEATURES = ["descriptorColorLayout","descriptorEdgeHistogram"]


CFG_IMAGE_SIMILARITY_CLUE_FEATURES = ["descriptorColorLayout","descriptorEdgeHistogram"]

CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_SEEDS = 4

CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_HITS_PER_SEED = 3


CFG_IMAGE_SIMILARITY_SIMILAR_SEARCH_ALGO = 'COMBINE'

CFG_IMAGE_SIMILARITY_SIMILAR_NUM_RESULTS = 50