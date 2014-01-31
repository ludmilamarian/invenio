package pylire;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;

import javax.imageio.ImageIO;

import org.apache.lucene.analysis.core.WhitespaceAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.index.Term;
import org.apache.lucene.store.FSDirectory;

import net.semanticmetadata.lire.DocumentBuilder;
import net.semanticmetadata.lire.DocumentBuilderFactory;
import net.semanticmetadata.lire.ImageSearchHits;
import net.semanticmetadata.lire.ImageSearcher;
import net.semanticmetadata.lire.ImageSearcherFactory;
import net.semanticmetadata.lire.utils.FileUtils;
import net.semanticmetadata.lire.utils.LuceneUtils;

public class InvenioHandler {
		
	/**
	 * Creats or appends to a selection of Lucene indexes storing LIRE documents.
	 * @param pathToIndexes : path to parent folder of indexes. Each index in separate folder named after its feature.
	 * @param features : LIRE features to extract and add to index. Each feature has its own index.
	 * @param pathToId : mapping between image identifier (recid in invenio) and path to image. key:path, value:recid.
	 * @param overwrite : flag for specifying whether to make a new index, overwriting any previous one, or whether to add new images to existing index (if one exists)
	 */
	public static void index(String pathToIndexes, String[] features, HashMap<String,String> pathToId, boolean overwrite) {
		// TODO check whether images are already in index?
		for(String feature: features) {
			String indexFolder = pathToIndexes + File.separator + feature;
			File file = new File(indexFolder);
			file.getParentFile().mkdirs(); // TODO check feature is compatible	
			 
			IndexWriterConfig conf = new IndexWriterConfig(LuceneUtils.LUCENE_VERSION,
	                new WhitespaceAnalyzer(LuceneUtils.LUCENE_VERSION));
			if (overwrite) conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
	        try {	        	
				IndexWriter writer = new IndexWriter(FSDirectory.open(new File(indexFolder)), conf);
				DocumentBuilder builder = getBuilder(feature);
				// TODO check builder not null. If null do not make anything.
				for (String nextImagePath: pathToId.keySet()) {
					File fileOrFolderCheck = new File(nextImagePath);
					if (!fileOrFolderCheck.isDirectory()) {
						BufferedImage img = ImageIO.read(new FileInputStream(nextImagePath)); 
						Document document = builder.createDocument(img, nextImagePath); 
						String recid = pathToId.get(document.get(DocumentBuilder.FIELD_NAME_IDENTIFIER));
						document.removeField(DocumentBuilder.FIELD_NAME_IDENTIFIER);
						document.add(new StringField(DocumentBuilder.FIELD_NAME_IDENTIFIER, recid, Field.Store.YES));
						document.add(new StringField("pathToImage", nextImagePath, Field.Store.YES));
						writer.addDocument(document);
					}
				}
				writer.close();
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}			
		}
	}
	
	/**
	 * In case user doesn't want mapping. Just want image ids to be image paths. Index all images in folder "pathToImages". Not useful for invenio!!!
	 * @param pathToIndexes
	 * @param pathToImages
	 * @param features
	 * @param overwrite
	 */
	public static void index(String pathToIndexes , String pathToImages, String[] features, boolean overwrite) {
		// TODO check whether images are already in index?
		for(String feature: features) {
			String indexFolder = pathToIndexes + File.separator + feature;
			File file = new File(indexFolder);
			file.getParentFile().mkdirs(); // TODO check feature is compatible	
			 
			IndexWriterConfig conf = new IndexWriterConfig(LuceneUtils.LUCENE_VERSION,
	                new WhitespaceAnalyzer(LuceneUtils.LUCENE_VERSION));
			if (overwrite) conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
	        try {	        	
				IndexWriter writer = new IndexWriter(FSDirectory.open(new File(indexFolder)), conf);
				DocumentBuilder builder = getBuilder(feature);
				// TODO check builder not null. If null do not make anything.
				ArrayList<String> images = FileUtils.getAllImages(new File(pathToImages), false); //descend into sub-directories? false
				Iterator<String> imageIterator = images.iterator();
				while (imageIterator.hasNext()) {
					String nextImage = imageIterator.next();
					BufferedImage img = ImageIO.read(new FileInputStream(nextImage)); //TODO make buffered image once for all features
					Document document = builder.createDocument(img, nextImage); //TODO overwrite ID
					document.add(new StringField("pathToImage", nextImage, Field.Store.YES));
					
					//document.removeField(DocumentBuilder.FIELD_NAME_IDENTIFIER);
					//document.add(new StringField(DocumentBuilder.FIELD_NAME_IDENTIFIER, nextImage, Field.Store.YES));
					writer.addDocument(document);
				}
				writer.close();
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}			
		}
	}
	
	/**
	 * If append/overwrite index not specified then append
	 * @param pathToIndexes : parent folder of indexes
	 * @param features : list of features/indexes to append to
	 * @param pathToId : mapping between each image and its recid
	 */
	public static void index(String pathToIndexes, String[] features, HashMap<String,String> pathToId) {
		index(pathToIndexes, features, pathToId, false);
	}
	
	/**
	 * Used when performing a query or when adding to an index. A builder is used to extract the correct feature and make the correct Lucene document.
	 * @param feature : type of builer to make.
	 * @return : Lucene document builder
	 */
	public static DocumentBuilder getBuilder(String feature) {
        if (feature.equals(DocumentBuilder.FIELD_NAME_COLORLAYOUT)) return DocumentBuilderFactory.getColorLayoutBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_EDGEHISTOGRAM))  return DocumentBuilderFactory.getEdgeHistogramBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_AUTOCOLORCORRELOGRAM)) return DocumentBuilderFactory.getAutoColorCorrelogramDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_CEDD)) return DocumentBuilderFactory.getCEDDDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_COLORHISTOGRAM)) return DocumentBuilderFactory.getColorHistogramDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_FCTH)) return DocumentBuilderFactory.getFCTHDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_GABOR)) return DocumentBuilderFactory.getGaborDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JCD)) return DocumentBuilderFactory.getJCDDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JOINT_HISTOGRAM)) return DocumentBuilderFactory.getJointHistogramDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JPEGCOEFFS)) return DocumentBuilderFactory.getJpegCoefficientHistogramDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_LUMINANCE_LAYOUT)) return DocumentBuilderFactory.getLuminanceLayoutDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_OPPONENT_HISTOGRAM)) return DocumentBuilderFactory.getOpponentHistogramDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_PHOG)) return DocumentBuilderFactory.getPHOGDocumentBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_SCALABLECOLOR)) return DocumentBuilderFactory.getScalableColorBuilder();
        else if (feature.equals(DocumentBuilder.FIELD_NAME_TAMURA)) return DocumentBuilderFactory.getTamuraDocumentBuilder();
        // TODO add support for MSER, etc?
        return null;
        
	}
	
	/**
	 * Updates an entry in index. Use if image associated with image identifier is modified.
	 * @param pathToIndexes : path to parent folder containing all indexes. Indexes are in separate folders.
	 * @param pathToImage : path to new version of the image, the one whose features will replace index entry's current features.
	 * @param imageID : identifier in indexes of image whose entry is to be updated.
	 * @param features : features/indexes on which to perform the update.
	 */
	public static void updateIndexes(String pathToIndexes, String pathToImage, String imageID, String[] features) {
		try {
			for (String feature:features) {
				String currentIndex = pathToIndexes + File.separator + feature;
				Term toDel = new Term(DocumentBuilder.FIELD_NAME_IDENTIFIER, imageID);
				IndexWriterConfig conf = new IndexWriterConfig(LuceneUtils.LUCENE_VERSION,
		                new WhitespaceAnalyzer(LuceneUtils.LUCENE_VERSION));
		        IndexWriter writer = new IndexWriter(FSDirectory.open(new File(currentIndex)), conf);

		        DocumentBuilder builder = getBuilder(feature);
		        BufferedImage img = ImageIO.read(new FileInputStream(pathToImage));
                Document document = builder.createDocument(img, pathToImage);
		        document.removeField(DocumentBuilder.FIELD_NAME_IDENTIFIER);
				document.add(new StringField(DocumentBuilder.FIELD_NAME_IDENTIFIER, imageID, Field.Store.YES));
				document.add(new StringField("pathToImage", pathToImage, Field.Store.YES));
                writer.updateDocument(toDel, document);
                //writer.forceMergeDeletes(); // TODO Use if we need update to be immediately visible
		        writer.close();
			}
	        //System.out.println(imageID + " successfully updated!");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
	/**
	 * Removes entry in chosen indexes of specified image. 
	 * @param pathToIndexes : path to parent folder of indexes.
	 * @param imageID : image descriptor used when adding to index (for invenio this is recid), this specifies which image to remove from indexes. 
	 * @param features : features/indexes from which to remove chosen image.
	 */
	public static void deleteFromIndexes(String pathToIndexes, String imageID, String[] features) {
		try {
			for (String feature:features) {
				String currentIndex = pathToIndexes + File.separator + feature;
				Term toDel = new Term(DocumentBuilder.FIELD_NAME_IDENTIFIER, imageID);
				IndexWriterConfig conf = new IndexWriterConfig(LuceneUtils.LUCENE_VERSION,
		                new WhitespaceAnalyzer(LuceneUtils.LUCENE_VERSION));
		        IndexWriter writer = new IndexWriter(FSDirectory.open(new File(currentIndex)), conf);
		        
		        /* DEBUG START */		        
		        /*Query query = new TermQuery(toDel);
		        IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(currentIndex)));
		        IndexSearcher searcher = new IndexSearcher(reader);
		        ScoreDoc[] docs = searcher.search(query, 100).scoreDocs;
		        for (int i = 0; i<docs.length; i++) {
		        	System.out.println(docs[i].doc + "   :    " + docs[i].score);
		        	System.out.println("Query found : " + reader.document(docs[i].doc));
		        }*/
		        /* DEBUG END */
		        
		        writer.deleteDocuments(toDel);
		        // writer.forceMerge(1); // TODO this is not necessarily something to do, but if you want the index to always be correct, use this line. otherwise segments with deleted image will wait to be merged and other images in segment will not be findable, segment is tagged as containing a deletion.
		        writer.close();
			}
	        System.out.println(imageID + " successfully deleted!");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	/**
	 * Launches a search operation on a set of indexes
	 * @param pathToSearch : path to query image file, make sure it is preprocessed and java-friendly! 
	 * @param pathToIndexes : path to parent folder of the indexes to be searched (not all the indexes have to be used, see 'features')
	 * @param features : selection of features to extract. indexes are named after their feature, so this doubles as index selection.
	 * @param numResults : number of results to retrieve
	 * @return : table of arrays of ImageSearchHit objects. each entry in table is for a feature/index. each array in a table is the corresponding feature's 'numResults' hits.  
	 */
	public static ImageSearchHits[] search(String pathToSearch, String pathToIndexes, String[] features, int numResults) {
		int numberOfFeatures = features.length;
		ImageSearchHits[] hits = new ImageSearchHits[numberOfFeatures];
		int numHits = 0;
		try {
			FileInputStream in = new FileInputStream(pathToSearch);
	        BufferedImage buff = ImageIO.read(in);
			for (String feature: features) {
				IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(pathToIndexes+File.separator+feature)));
				ImageSearcher searcher = getSearcher(feature, numResults);
                hits[numHits] = searcher.search(buff, reader);
                reader.close();                  
                numHits ++;				
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return hits;
	}

	/**
	 * Launches search with relaxed call parameters. 'numResults' to retrieve is defaulted to 50. See above.
	 * @param pathToSearch
	 * @param pathToIndexes
	 * @param features
	 * @return
	 */
	public static ImageSearchHits[] search(String pathToSearch, String pathToIndexes, String[] features) {
		return search(pathToSearch, pathToIndexes, features, 50);
	}
	
	/**
	 * Launches search for an image using an algorithm based on CLUE. Ncut is not implemented here, but in python.
	 * For more information on the algorithm, see:
	 * Yixin Chen, James Z. Wang and Robert Krovetz ``CLUE: Cluster-based Retrieval of Images by Unsupervised Learning,''IEEE Transactions on Image Processing, vol. 14, no. 8, pp. 1187-1201, 2005
	 * 
	 * @param pathToSearch : path to query image
	 * @param pathToIndexes : path to parent folder containing all index folders.
	 * @param features : set of features/indexes to use in query
	 * @param numberOfSeeds : number of hits to return in initial search (search on query image)
	 * @param numberOfSeeded : number of hits to return for subsequent searches on seeds found from query image.
	 * @return : ClueResults object, containing the adjacency matrix of all found images and mapping between image ids (recids with invenio) and their corresponding position (which row is theirs) in the matrix.
	 */
	public static ClueResults clueSearch(String pathToSearch, String pathToIndexes, String[] features, int numberOfSeeds, int numberOfSeeded) {
		try {
			return Clue.searchForImage(pathToSearch, pathToIndexes, features, numberOfSeeds, numberOfSeeded);
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return null;
	}
	
	/**
	 * Utils method to select the correct document searcher when performing a search. Each searcher handles a different feature, mainly through defining how to compare two instances of said feature.
	 * @param feature : type of builder to return
	 * @param numResults : number of results the returned searcher will have to find (and remember internally)
	 * @return : image index searcher
	 */
	public static ImageSearcher getSearcher(String feature, int numResults) {
		if (feature.equals(DocumentBuilder.FIELD_NAME_COLORLAYOUT)) return ImageSearcherFactory.createColorLayoutImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_EDGEHISTOGRAM))  return ImageSearcherFactory.createEdgeHistogramImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_AUTOCOLORCORRELOGRAM)) return ImageSearcherFactory.createAutoColorCorrelogramImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_CEDD)) return ImageSearcherFactory.createCEDDImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_COLORHISTOGRAM)) return ImageSearcherFactory.createColorHistogramImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_FCTH)) return ImageSearcherFactory.createFCTHImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_GABOR)) return ImageSearcherFactory.createGaborImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JCD)) return ImageSearcherFactory.createJCDImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JOINT_HISTOGRAM)) return ImageSearcherFactory.createJointHistogramImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_JPEGCOEFFS)) return ImageSearcherFactory.createJpegCoefficientHistogramImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_LUMINANCE_LAYOUT)) return ImageSearcherFactory.createLuminanceLayoutImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_OPPONENT_HISTOGRAM)) return ImageSearcherFactory.createOpponentHistogramSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_PHOG)) return ImageSearcherFactory.createPHOGImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_SCALABLECOLOR)) return ImageSearcherFactory.createScalableColorImageSearcher(numResults);
        else if (feature.equals(DocumentBuilder.FIELD_NAME_TAMURA)) return ImageSearcherFactory.createTamuraImageSearcher(numResults);
        // TODO add support for MSER, etc ?
        return null;
					
	}
	
}