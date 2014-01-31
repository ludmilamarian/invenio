package pylire;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

import javax.imageio.ImageIO;

import net.semanticmetadata.lire.DocumentBuilder;
import net.semanticmetadata.lire.ImageSearchHits;
import net.semanticmetadata.lire.ImageSearcher;
import net.semanticmetadata.lire.imageanalysis.AutoColorCorrelogram;
import net.semanticmetadata.lire.imageanalysis.CEDD;
import net.semanticmetadata.lire.imageanalysis.ColorLayout;
import net.semanticmetadata.lire.imageanalysis.EdgeHistogram;
import net.semanticmetadata.lire.imageanalysis.FCTH;
import net.semanticmetadata.lire.imageanalysis.Gabor;
import net.semanticmetadata.lire.imageanalysis.JCD;
import net.semanticmetadata.lire.imageanalysis.JpegCoefficientHistogram;
import net.semanticmetadata.lire.imageanalysis.LireFeature;
import net.semanticmetadata.lire.imageanalysis.LuminanceLayout;
import net.semanticmetadata.lire.imageanalysis.OpponentHistogram;
import net.semanticmetadata.lire.imageanalysis.PHOG;
import net.semanticmetadata.lire.imageanalysis.ScalableColor;
import net.semanticmetadata.lire.imageanalysis.SimpleColorHistogram;
import net.semanticmetadata.lire.imageanalysis.Tamura;
import net.semanticmetadata.lire.imageanalysis.joint.JointHistogram;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.store.FSDirectory;


public class Clue {

    //private static boolean ASC = true;
    private static boolean DESC = false;
    private static int numberOfFeatures = 1; // TODO test with more than one feature, if works add selection of number of features to use as clueSearch method parameter, actually no, simply deduce number of features from number of features sent to method! 
    private static HashMap<String, Set<Document>> docs = new HashMap<String,Set<Document>>();
    private static HashMap<String, List<String>> docsNames = new HashMap<String,List<String>>();
    private static Set<String> allDocsNames = new HashSet<String>();
	
    /**
     * Perform CLUE search up to the point of adjacency matrix. To complete CLUE, Ncut needs to be performed on resulting adjmat. Main function which calls all other functions in this file.
     * @param imagePath : path to query image
     * @param pathToIndexes : path to parent folder of indexes
     * @param fields : features to search
     * @param numberOfSeeds : number of closest hits to query image to then use as search when creating list of hits.
     * @param numberOfSeeded : number of hits to find for each seed search.
     * @return : ClueResults object containing adjmat and mapping from ids to positions in adjmat.
     * @throws FileNotFoundException
     * @throws IOException
     */
	public static ClueResults searchForImage(String imagePath, String pathToIndexes, String[] fields, int numberOfSeeds, int numberOfSeeded) throws FileNotFoundException, IOException {
        final String path = imagePath;
                try { 
                    // each of the features gets a hit list
                    ImageSearchHits[] hits = new ImageSearchHits[numberOfFeatures];
                    for (int i=0; i<numberOfFeatures; i++) {
	                         IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(pathToIndexes+File.separator+fields[i])));
	                         ImageSearcher searcher = InvenioHandler.getSearcher(fields[i],numberOfSeeds);           
	                         hits[i] = searcher.search(ImageIO.read(new FileInputStream(path)), reader);
	                         reader.close();
                    	
                    }
                    
                    addHits2Docs(hits, numberOfSeeds, fields);
                    Map<String, Double> sortedStdMap = standardScores(hits);

                    getClueHits(sortedStdMap,numberOfSeeds, numberOfSeeded,fields,pathToIndexes);     
                    
                    /*
                     *  1) make a lire feature for each image in clueHits and the initial query image
                     *  2) for each pair do: feature1.getDistance(feature2);
                     *  3) add normalized and reversed distance (i.e. similarity) to adjacency matrix                      
                     */
                    ClueResults clueAdjMatAndMap = makeAdjacencyMatrix(path,fields);
//                    double[][] adjacencyMatrix = clueAdjMatAndMap.adjacency_matrix;
//                    System.out.println("AdjMat dim = " + adjacencyMatrix.length);
//                    for (int i = 0; i<adjacencyMatrix.length;i++) {
//                    	System.out.println();
//                    	for (int j = 0; j<adjacencyMatrix[i].length;j++) {
//                    		System.out.print(adjacencyMatrix[i][j] + " ");
//                    	}
//                    	
//                    }
//                                        
//                    System.out.println(" Documents: ");
//                    Document[] doccy = new Document[docs.get(fields[0]).size()];
//                    doccy = docs.get(fields[0]).toArray(doccy);
//                    for (int i = 0; i<docs.get(fields[0]).size();i++) {
//                    	System.out.println(i+" : " +doccy[i].getField("descriptorImageIdentifier"));
//                    }

                   return clueAdjMatAndMap;
                } catch (Exception e) {
                    // Nothing to do here ....
                 e.printStackTrace();
                }
                return null;
    }
    
	
	/**
	 * Creates adjacency matrix from all search hits. Call once all seeds have been found and global variables are set. 
	 * @param path : query image path, used for making fields if image was not in index and so is not a hit
	 * @param fields : features used
	 * @return : adjacency matrix and map between identifiers and adjmat row numbers
	 */
	private static ClueResults makeAdjacencyMatrix(String path, String[] fields) {
        try {

            HashMap<String,Document[]> docsList = new HashMap<String,Document[]>();
            for (int i=0;i<numberOfFeatures;i++) {
                 Document[] dcarray = new Document[docs.get(fields[i]).size()];
                 docs.get(fields[i]).toArray(dcarray);
                 docsList.put(fields[i], dcarray);
            }
           
           
            HashMap<String,LireFeature[]> feature = new HashMap<String,LireFeature[]>();

            //ChainedDocumentBuilder builder = new ChainedDocumentBuilder();
            // builder.addBuilder(new EasyBuilder3());//TODO fix for feature selection
            // TODO we should have a builder per field and create a doc for each, current implementation only covers the case of using one feature in search
            DocumentBuilder builder = InvenioHandler.getBuilder(fields[0]); // TODO if change to support several features, change this
            Document doc = builder.createDocument(new FileInputStream(path), path);
            int addQueryImageToAdjMat = 0; // set to 1 if we need to add the query image to our list of documents (typically if query image was not in index)
            if (!allDocsNames.contains(doc.getField("descriptorImageIdentifier").stringValue())) {
                 addQueryImageToAdjMat = 1;
            }
            double[][] adjacencyMatrix = new double[allDocsNames.size()+addQueryImageToAdjMat][allDocsNames.size()+addQueryImageToAdjMat]; // all docs from our hits and seeded hits plus initial search document (this is the +1)
            for (int i=0; i<adjacencyMatrix.length; i++) {
                for (int j=0; j<adjacencyMatrix[i].length; j++) {
                    adjacencyMatrix[i][j] = 0;
                }
            }
           
            for (int j=0; j<numberOfFeatures; j++) {
                 feature.put(fields[j], new LireFeature[docsList.get(fields[j]).length+addQueryImageToAdjMat]);
                for (int i=0; i<docsList.get(fields[j]).length; i++) {
                	feature.get(fields[j])[i] = getLireFeature(fields[j]); // initialize with empty field of correct feature
                	feature.get(fields[j])[i].setByteArrayRepresentation(docsList.get(fields[j])[i].getField(fields[j]).binaryValue().bytes, docsList.get(fields[j])[i].getField(fields[j]).binaryValue().offset, docsList.get(fields[j])[i].getField(fields[j]).binaryValue().length);
                }
            }
           
            if (addQueryImageToAdjMat==1) { // if query image not in result (eg not in index), add its feature to set of features for comparing and building adjacency matirx later
                    for (int i=0; i<numberOfFeatures; i++) {
                    	feature.get(fields[i])[docsList.get(fields[i]).length] = getLireFeature(fields[i]);
                    	feature.get(fields[i])[docsList.get(fields[i]).length].setByteArrayRepresentation(doc.getField(fields[i]).binaryValue().bytes, doc.getField(fields[i]).binaryValue().offset, doc.getField(fields[i]).binaryValue().length);
                    }
            }
           
            HashMap<String,Integer> mapIdToPosition = new HashMap<String,Integer>(); // create map telling us which image is which row of adjmat. useful if using several features and they didn't all have the same list of hits. 
            Iterator<String> it = allDocsNames.iterator();
            for (int i=0; i<allDocsNames.size(); i++) {  
                 String temp = it.next();
                mapIdToPosition.put(temp, i);
            }
            if (addQueryImageToAdjMat==1) {
                 mapIdToPosition.put(doc.getField("descriptorImageIdentifier").stringValue(), allDocsNames.size());
            }
           
            // populate adjmat. 
            // Step 1: find all distance measures
            // Step 2: normalize and reverse distances (i.e. 0 is highest distance, 1 is closest)
            // Step 3: insert in adjmat in correct place
            for (int k=0; k<numberOfFeatures;k++) {
                double[] allDistances = new double[feature.get(fields[k]).length*feature.get(fields[k]).length];
                for (int i=0; i<feature.get(fields[k]).length; i++) {
                    for (int j=0; j<feature.get(fields[k]).length; j++) {
                        allDistances[i*feature.get(fields[k]).length+j] = feature.get(fields[k])[i].getDistance(feature.get(fields[k])[j]);
                    }
                }
                double max = 0;
                for (int l=0; l<allDistances.length;l++) {
                    if (allDistances[l]>max) {
                        max = allDistances[l];
                    }
                }
                for (int l=0; l<allDistances.length;l++) {
                    allDistances[l] = 1 - allDistances[l]/max;
                }
                for (int i=0; i<feature.get(fields[k]).length; i++) {
                    for (int j=0; j<feature.get(fields[k]).length; j++) {
                         if (addQueryImageToAdjMat == 1) {
                                  if (i==feature.get(fields[k]).length-1 && j!=feature.get(fields[k]).length-1) {
                                          adjacencyMatrix[mapIdToPosition.get(doc.getField("descriptorImageIdentifier").stringValue())][mapIdToPosition.get(docsList.get(fields[k])[j].getField("descriptorImageIdentifier").stringValue())] += allDistances[i*feature.get(fields[k]).length+j];
                                  }
                                  else if(j==feature.get(fields[k]).length-1 && i!=feature.get(fields[k]).length-1) {
                                          adjacencyMatrix[mapIdToPosition.get(docsList.get(fields[k])[i].getField("descriptorImageIdentifier").stringValue())][mapIdToPosition.get(doc.getField("descriptorImageIdentifier").stringValue())] += allDistances[i*feature.get(fields[k]).length+j];
                                  }
                                  else if(j==feature.get(fields[k]).length-1 && i==feature.get(fields[k]).length-1) {
                                          adjacencyMatrix[mapIdToPosition.get(doc.getField("descriptorImageIdentifier").stringValue())][mapIdToPosition.get(doc.getField("descriptorImageIdentifier").stringValue())] += allDistances[i*feature.get(fields[k]).length+j];
                                  }
                                  else {
                                          adjacencyMatrix[mapIdToPosition.get(docsList.get(fields[k])[i].getField("descriptorImageIdentifier").stringValue())][mapIdToPosition.get(docsList.get(fields[k])[j].getField("descriptorImageIdentifier").stringValue())] += allDistances[i*feature.get(fields[k]).length+j];
                                  }
                         }
                         else {
                                 adjacencyMatrix[mapIdToPosition.get(docsList.get(fields[k])[i].getField("descriptorImageIdentifier").stringValue())][mapIdToPosition.get(docsList.get(fields[k])[j].getField("descriptorImageIdentifier").stringValue())] += allDistances[i*feature.get(fields[k]).length+j];
                         }
                    }
                }
            }
            ClueResults results = new ClueResults(adjacencyMatrix, mapIdToPosition);
            return results;
        } catch(Exception e) {
            e.printStackTrace();
        }
        return null;
    }
	
	/**
	 * Given initial query's search results, identify seeds and perform searches on seeds. (when searching for seeds, all new documents are added to global variable)
	 * @param sortedStdMap : sorted map of initial query's hits
	 * @param numberOfSeeds : number of seeds to use
	 * @param numberOfSeeded : number of seed hits to keep from seed queries
	 * @param fields : list of features to use
	 * @param pathToIndexes : path to parent folder of indexes
	 */
	private static void getClueHits(Map<String, Double> sortedStdMap, int numberOfSeeds, int numberOfSeeded,String[] fields, String pathToIndexes) {
		Iterator<String> its = sortedStdMap.keySet().iterator();
//		HashMap<String, Double> clueHits = new HashMap<String, Double>();
        int seen = 0;
        while (its.hasNext() && seen <= numberOfSeeds) {
                String name = its.next();
            		seen = seen + 1;
            		searchForSeed(name, numberOfSeeded,fields, pathToIndexes);
//                if (!clueHits.containsKey(name)) {
//                	clueHits.put(name, sortedStdMap.get(name));
//                }
//                Iterator<String> itSeeded = seeded.keySet().iterator();
//                int seenSeeded =0;
//                while (itSeeded.hasNext() && seenSeeded <= numberOfSeeded){
//                	seenSeeded = seenSeeded+1;
//                	String seededName = itSeeded.next();
//                	if (!clueHits.containsKey(seededName)) {
//                    	clueHits.put(seededName, seeded.get(seededName));
//                    }
//                }
        }
	}
    
	/**
	 * Given array of hits, adds hit identifiers to list of document identifiers
	 * @param hits : array of hits per feature. Each feature has an array of hits.
	 * @param num_seeds_wanted : number of hits whose identifiers should be added to list of document identifiers
	 * @param fields : features
	 */
	private static void addHits2Docs(ImageSearchHits[] hits, int num_seeds_wanted, String[] fields) {
        for (int i=0; i<hits.length; i++) {
            if (docsNames.containsKey(fields[i])) {
                for (int j=0; j<Math.min(hits[i].length(),num_seeds_wanted); j++) {
                    if (!docsNames.get(fields[i]).contains(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue())) { 
                        docs.get(fields[i]).add(hits[i].doc(j));
                        docsNames.get(fields[i]).add(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue());
                        }
                    allDocsNames.add(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue());
                }
            }
            else {
                docs.put(fields[i], new HashSet<Document>());
                docsNames.put(fields[i], new ArrayList<String>());
                for (int j=0; j<Math.min(hits[i].length(),num_seeds_wanted); j++) {
                    if (!docsNames.get(fields[i]).contains(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue())) { 
                        docs.get(fields[i]).add(hits[i].doc(j));
                        docsNames.get(fields[i]).add(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue());
                        }
                    allDocsNames.add(hits[i].doc(j).getField("descriptorImageIdentifier").stringValue());
                }
            }
        }
    }


	/**
	 * Perform search on seeds and add to list of overall hits.
	 * @param name : path to seed
	 * @param numberOfSeeded : number of hits to find per seed
	 * @param fields : features to search
	 * @param pathToIndexes : path to index parent folder
	 */
	private static void searchForSeed(String name, int numberOfSeeded,String[] fields, String pathToIndexes) {
    	final String path = name;
        try {
            // each of the features gets a hit list
            ImageSearchHits[] hits = new ImageSearchHits[numberOfFeatures];
            for (int i=0; i<numberOfFeatures; i++) {
                     IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(pathToIndexes+File.separator+fields[i])));
                     ImageSearcher searcher = InvenioHandler.getSearcher(fields[i],numberOfSeeded);           
                     hits[i] = searcher.search(ImageIO.read(new FileInputStream(path)), reader);
                     reader.close();            
            }
            addHits2Docs(hits, numberOfSeeded,fields);        	        
        }catch(Exception e){
        	e.printStackTrace();        	
        }
            
	}


	/**
	 * Produce standard scores from several features' hit lists. Not useful in case of only one feature being used.
	 * @param hits : array of hit lists
	 * @return : sorted map of standardized scores and paths to images
	 */
    private static Map<String, Double> standardScores(ImageSearchHits[] hits) {
    	// Here we calculate each feature's mean and std for standardization:
        //  input: score 'x'
        //  output: score 'z'
        //  z = (x-mean)/std
        double [] means = new double[hits.length];
        double[] maxes = new double[hits.length];
        double[] stds = new double[hits.length];
        double[][] stdScores = new double[hits.length][hits[0].length()];
        // find means
        for (int i=0; i<hits.length; i++) {
        	maxes[i] = Double.MIN_VALUE;
        	for (int j=0; j<hits[i].length(); j++) {
        		means[i] = means[i] + hits[i].score(j);
        	}
        	means[i] = means[i]/hits[i].length();
        }
        
        // use means to finds standard deviations
        for (int i=0; i<hits.length; i++) {
        	for (int j=0; j<hits[i].length(); j++) {
        		stds[i] = stds[i] + Math.pow((hits[i].score(j) - means[i]),2);
        	}
        	stds[i] = stds[i] / hits[i].length();
        	stds[i] = Math.sqrt(stds[i]);
        	//stds[i] = stds[i] - maxes[i];
        }
        
        // get std scores minus the min in each feature
        for (int i=0; i<hits.length; i++) {
        	for (int j=0; j<hits[i].length(); j++) {
        		stdScores[i][j] = (hits[i].score(j) - means[i]) / stds[i];
        		if (stdScores[i][j] > maxes[i]) {
        			maxes[i] = stdScores[i][j];
        		}
        	}    
        	for (int j=0; j<hits[i].length(); j++) {
        		stdScores[i][j] = stdScores[i][j] - maxes[i]; // put standard scores between -x and 0. best at -x and worst hit at 0
        		stdScores[i][j] = -1*stdScores[i][j];
        	}
        }
        //summing all distances to make total distance
        HashMap<String,Double> stdMap = new HashMap<String,Double>();
      
        // This loop fills map with every single hit and its score, as given by the rankings of each method
        for (int i=0; i<hits.length; i++) {
             for (int j=0; j<hits[i].length(); j++) {
              String key = hits[i].doc(j).getField("pathToImage").stringValue();
                     if (stdMap.containsKey(key)) {
                      double update = stdMap.get(key) + stdScores[i][j];
                      stdMap.remove(key);
                      stdMap.put(key, update);
                     }
                     else {
                      stdMap.put(key, stdScores[i][j]);
                     }
             }
        }
        return sortByComparator(stdMap, DESC);
        
    }
    
    /**
     * Utils function for ordering similarity values in a <id, score> mapping.
     * @param unsortMap : unsorted map
     * @param order : order is true->ASC or false->DESC
     * @return : sorted map
     */
	private static Map<String, Double> sortByComparator(Map<String, Double> unsortMap, final boolean order) {

        List<Entry<String, Double>> list = new LinkedList<Entry<String, Double>>(unsortMap.entrySet());

        // Sorting the list based on values
        Collections.sort(list, new Comparator<Entry<String, Double>>()
        {
            public int compare(Entry<String, Double> o1,
                    Entry<String, Double> o2)
            {
                if (order)
                {
                    return o1.getValue().compareTo(o2.getValue());
                }
                else
                {
                    return o2.getValue().compareTo(o1.getValue());

                }
            }
        });

        // Maintaining insertion order with the help of LinkedList
        Map<String, Double> sortedMap = new LinkedHashMap<String, Double>();
        for (Entry<String, Double> entry : list)
        {
            sortedMap.put(entry.getKey(), entry.getValue());
        }

        return sortedMap;
    }
    
	
	/**
	 * Utils method for making empty field of chosen LIRE feature
	 * @param feature : feature to initialize
	 * @return : initialized and empty field
	 */
	private static LireFeature getLireFeature(String feature) {
		try {
			if (feature.equals(DocumentBuilder.FIELD_NAME_COLORLAYOUT)) return (LireFeature) ColorLayout.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_EDGEHISTOGRAM))  return (LireFeature) EdgeHistogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_AUTOCOLORCORRELOGRAM)) return (LireFeature) AutoColorCorrelogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_CEDD)) return (LireFeature) CEDD.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_COLORHISTOGRAM)) return (LireFeature) SimpleColorHistogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_FCTH)) return (LireFeature) FCTH.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_GABOR)) return (LireFeature) Gabor.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_JCD)) return (LireFeature) JCD.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_JOINT_HISTOGRAM)) return (LireFeature) JointHistogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_JPEGCOEFFS)) return (LireFeature) JpegCoefficientHistogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_LUMINANCE_LAYOUT)) return (LireFeature) LuminanceLayout.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_OPPONENT_HISTOGRAM)) return (LireFeature) OpponentHistogram.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_PHOG)) return (LireFeature) PHOG.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_SCALABLECOLOR)) return (LireFeature) ScalableColor.class.newInstance();
	        else if (feature.equals(DocumentBuilder.FIELD_NAME_TAMURA)) return (LireFeature) Tamura.class.newInstance();
		}
		catch (IllegalAccessException iae) {
			iae.printStackTrace();
		} catch (InstantiationException ie) {
			ie.printStackTrace();
		}
        // TODO add support for MSER, etc ?
        return null;
	}
    
}
