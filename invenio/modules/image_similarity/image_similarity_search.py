import pylire
import numpy
from sklearn.cluster import spectral_clustering

from image_similarity_config import CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES, \
    CFG_IMAGE_SIMILARITY_TRANSFORM_THRESHOLDS, \
    CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES, \
    CFG_IMAGE_SIMILARITY_DUPLICATE_THRESHOLDS, \
    CFG_IMAGE_SIMILARITY_INDEX_FOLDER, \
    CFG_IMAGE_SIMILARITY_COMBINE_FEATURES, \
    CFG_IMAGE_SIMILARITY_STANDARDIZE_FEATURES, \
    CFG_IMAGE_SIMILARITY_CLUE_FEATURES, \
    CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_SEEDS, \
    CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_HITS_PER_SEED


from image_similarity_engine import handler
from image_similarity_utils import get_image_path_from_rec_id

#--------put in controller/engine----------SET EVERYTHING UP
#pylire.initVM()
index_folder = CFG_IMAGE_SIMILARITY_INDEX_FOLDER
num_seeds = CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_SEEDS
num_seeded = CFG_IMAGE_SIMILARITY_CLUE_NUMBER_OF_HITS_PER_SEED
#handler = pylire.InvenioHandler()




# Finds identical images (actually, all images which are scored below every feature's threshold)
'''
Finds EXACT duplicates to an image given by path. No check will be done for having search image in results.
'''
def find_identical_versions_from_path(imgPath):
    hits = handler.search(imgPath, index_folder, CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES)

    results = dict()
    for ft in CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES:
        results[ft] = set()

    iterator = CFG_IMAGE_SIMILARITY_DUPLICATE_FEATURES.__iter__()
    for hit in hits:
        ft = iterator.next()
        for i in range(len(hit)):
            doc = hit[i]
            if hit.score(i) <= CFG_IMAGE_SIMILARITY_DUPLICATE_THRESHOLDS[ft]:
                results[ft].add(doc.get("descriptorImageIdentifier"))
                #print 'Distance from query : ' + str(hit.score(i))
            else:
                break
    resultsIntersect = set.intersection(*[featureSet for featureSet in results.values()]) 
    return resultsIntersect

'''
Finds EXACT duplicates to an image given by recid. Search recid will be removed from results.
'''
def find_identical_versions_from_recid(recid):
    img_path = get_image_path_from_rec_id(recid)[0]
    results = find_identical_versions_from_path(img_path)
    return results.difference(set(str(recid)))




# Finds approximate duplicates, i.e. at least below one feature's threshold
'''
Finds APPROXIMATE duplicates to an image given by path. No check will be done for having search image in results.
'''
def find_transformed_versions_from_path(img_path):
    hits = handler.search(img_path, index_folder, CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES)
    
    results = list()
    iterator = CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES.__iter__()
    for hit in hits:
        ft = iterator.next()
        for i in range(len(hit)):
            doc = hit[i]
            if hit.score(i) <= CFG_IMAGE_SIMILARITY_TRANSFORM_THRESHOLDS[ft]:
                results.append(doc.get("descriptorImageIdentifier"))
                #print 'Distance from query : ' + str(hit.score(i))
            else:
                break # since hits are ordered by score, as soon as one is above threshold all subsequent will also be
    return list(set(results))

'''
Finds APPROXIMATE duplicates to an image given by recid. Search recid will be removed from results.
'''
def find_transformed_versions_from_recid(recid):
    img_path = get_image_path_from_rec_id(recid)[0]
    results = find_transformed_versions_from_path(img_path)
    return list(set(results).difference(set(str(recid))))



def find_similar_from_path(img_path, method, number_of_results_wanted):
    results = list()
    # sift - entropy - clue - combined - BOVW
    if method=='CLUE':
        clue_results = handler.clueSearch(img_path, index_folder, CFG_IMAGE_SIMILARITY_CLUE_FEATURES,num_seeds,num_seeded)
        adjmat = clue_results.adjacencyMatrix
        rows = list()
        for i in range(len(adjmat)):
            row = list()
            line = pylire.JArray('double').cast_(adjmat[i])
            for j in range(len(line)):
                row.append(line[j])
            rows.append(row)
        adjmat = numpy.array(rows)
        labels = spectral_clustering(adjmat, n_clusters=2)
        recid_to_position = dict()
        for label in labels:
            print label



        # make various clusters (simply lists of recids) from labels and clue_results.mapIdToPosition

    if method=='COMBINE':
        hits = handler.search(img_path, index_folder, CFG_IMAGE_SIMILARITY_COMBINE_FEATURES,number_of_results_wanted)
        h_n,h_d = translateHitsToDictionary(hits,CFG_IMAGE_SIMILARITY_COMBINE_FEATURES)
        norm_d = normalizeScores(h_d)
        comb_hits, comb_dists = combine(h_n,norm_d,0,number_of_results_wanted)
        return comb_hits
    

    if method=='STANDARDIZE':
        hits = handler.search(img_path, index_folder, CFG_IMAGE_SIMILARITY_STANDARDIZE_FEATURES,number_of_results_wanted)
        h_n,h_d = translateHitsToDictionary(hits,CFG_IMAGE_SIMILARITY_STANDARDIZE_FEATURES)
        std_d = normalizeScores(h_d)
        std_hits, std_dists = combine(h_n,std_d,0,number_of_results_wanted)
        return std_hits



    return results


def find_similar_from_recid(recid, method, number_of_results_wanted):
    img_path = get_image_path_from_rec_id(recid)[0]
    results = find_similar_from_path(img_path, method, number_of_results_wanted)
    return list(set(results).difference(set(str(recid))))



# hits = handler.search(img_path, index_folder, CFG_IMAGE_SIMILARITY_TRANSFORM_FEATURES)
# h_n,h_d = translateHitsToDictionary(hits)
# std_d = createStdScoresUsingAllTrainData(h_d)
# norm_d = normalizeScores(h_d)
# comb_hits = combine(h_n,norm_d,0,50)
# std_hits = combine(h_n,std_d,0,50)

'''
Prepare hits for combining scores either using normalized scores, or using standardized scores.
'''
def translateHitsToDictionary(hits,features):
    hits_names = dict()
    hits_dists = dict()

    iterator = features.__iter__()
    for hit in hits:        
        ft = iterator.next()
        hits_names[ft] = list()
        hits_dists[ft] = list()
        for i in range(len(hit)):
            doc = hit[i]
            hits_names[ft].append(doc.get("descriptorImageIdentifier"))
            hits_dists[ft].append(hit.score(i))
    return hits_names, hits_dists




'''
The following section are functions to create standard scores and normalized scores given hits from several features.
'''
def createStdScoresUsingAllTrainData(dists):
    ''' input: score 'x'
        output: score 'z'
        z = (x-mean)/std
    '''
    # Here we calculate each feature's mean and std for standardization:
    # Finally, we can get the largest standardized distance for each feature and  rescale all std dists so that in [0;1]
    
    distsbyfeature = dict()
    for feature in dists.keys():
        distsbyfeature[feature] = list()
    

    for feature in distsbyfeature:
        for element in dists[feature]:
            if element:
                distsbyfeature[feature].append(float(element))

    stdsbyfeature = dict()
    meansbyfeature = dict()
    maxbyfeature = dict()

    for feature in distsbyfeature.keys():
        stdsbyfeature[feature] = numpy.std(distsbyfeature[feature])
        meansbyfeature[feature] = numpy.mean(distsbyfeature[feature])
        maxbyfeature[feature] = numpy.amax(distsbyfeature[feature])

    any_standard_deviation_is_zero = False
    for feature in stdsbyfeature:
        if stdsbyfeature[feature] == 0:
            any_standard_deviation_is_zero = True

    if any_standard_deviation_is_zero:
        return normalizeScores(dists)


    newdists = dict()
    for feature in dists:
        newdists[feature] = list()

    for feature in dists:
        search = dists[feature]
        newdists[feature].append([-1*((float(sch)-float(meansbyfeature[feature]))/float(stdsbyfeature[feature])-maxbyfeature[feature]) for sch in search if sch])
        
    # Next job is to combine our distances into standardized
    return newdists

def normalizeScores(dists):
    newdists = dict()
    for feat in dists:
        newdists[feat] = list()
        for sch in dists[feat]:
            search = dists[feat]
            # Here we have to take last element of current list divide all by this, except first element, then do 1-this to all list (except first elem)
            toAdd = list()
            #toAdd.append(0)
            if sch:
                toAdd.append(1-float(sch)/float(search[len(search)-1]))
            newdists[feat].append(toAdd)
    return newdists

'''
Takes as input:
hbt: dictionary by feature of strings corresponding to hits from search
dbt: dictionary by feature of floats corresponding to normallized scores or standard scores from a search (send raw scores through one of the corresponding functions before calling this function)
'''
def combine(hbt, dbt, weighted, number_of_results_wanted):
    search = list()
    searchdist = list()
    resultshits = list()
    resultsdists = list()

    weights = dict()
    features = ["descriptorColorLayout","featureCEDD","featureFCTH","featureJCD","descriptorScalableColor","descriptorEdgeHistogram","featureAutoColorCorrelogram","featureTAMURA","featureGabor","featureColorHistogram","featureJpegCoeffs","featOpHist","featureJointHist","featLumLay","featPHOG"]
    averages = [81.887,94.0439,92.0057,95.2231,79.7855,71.016,97.4941,45.9965,28.3834,86.3699,43.1617,85.3699,78.5992,41.4267,78.1127]
    weightsByFeature = dict()
    if weighted==1:
        for i in range(len(features)):
            weights.update({features[i]: averages[i]})
        for feature in hbt.keys():
            weightsByFeature.update({feature: weights[feature]})
    else:
        for feature in hbt.keys():
            weightsByFeature.update({feature: 1})

    for i in range(len(hbt[hbt.keys()[0]])):
        for feature in hbt.keys():
            search.append(hbt[feature][i])
            searchdist.append([d*weightsByFeature[feature] for d in dbt[feature][i]]) # to weight each feature: apply weigths by feature to each elem of this dbt[ft][i] before sending to next function
        results1, results2 = combineBySearch(search, searchdist, number_of_results_wanted)
        resultshits.append(results1)
        resultsdists.append(results2)
        search = list()
        searchdist = list()
    return resultshits, resultsdists


def combineBySearch(names, scores, number_of_results_wanted): # names are search results for one search, one list for every feature. scores are corresp dists
    results = dict()
    for i in range(len(names[0])): #each of these is a search result
        for j in range(len(names)): #each of these is a feature
            if names[j][i]:
                if names[j][i] in results.keys():
                    results[names[j][i]] += scores[j][i-1]
                else:
                    results.update({names[j][i]: scores[j][i-1]})
    # we have combine all search results from various features, we need to sort and pick number_of_results_wanted highest

    returnnames = list()
    returndists = list()
    topnames = sorted(results, key=results.get, reverse=True)[0:number_of_results_wanted]
    topdists = sorted(results.values(), reverse=True)[0:number_of_results_wanted]

    returnnames.extend([name for name in topnames])
    returndists.extend([dist for dist in topdists])

    return returnnames,returndists
