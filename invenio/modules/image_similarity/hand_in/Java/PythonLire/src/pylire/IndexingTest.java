package pylire;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
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

public class IndexingTest {
	// TODO see index() {}
	// TODO and index2() {}

	public static void index(String pathToIndexFolder , String pathToImageFolder, String[] features, HashMap<String,String> pathToId, boolean overwrite) {
		try {
			Document document;
			ArrayList<String> pathToImages = FileUtils.getAllImages(new File(pathToImageFolder), false);
			Iterator<String> imageIterator = pathToImages.iterator();
			ArrayList<DocumentBuilder> builders = new ArrayList<DocumentBuilder>(); // Use HashMap between String(feature) and Builder
			ArrayList<IndexWriter> writers = new ArrayList<IndexWriter>(); // Use HashMap
			IndexWriterConfig conf = new IndexWriterConfig(LuceneUtils.LUCENE_VERSION,
	                new WhitespaceAnalyzer(LuceneUtils.LUCENE_VERSION));
			if (overwrite) conf.setOpenMode(IndexWriterConfig.OpenMode.CREATE);
			String indexFolder;
			for(String feature: features) { // TODO add feature checks here
				indexFolder = pathToIndexFolder + File.separator + feature;
				File file = new File(indexFolder);
				file.getParentFile().mkdirs(); // TODO check if necessary?
				builders.add(getBuilder(feature));
				writers.add(new IndexWriter(FSDirectory.open(new File(indexFolder)), conf));
			}
			BufferedImage img;
			String nextImage;
			Iterator<DocumentBuilder> builderIterator = builders.iterator();
			Iterator<IndexWriter> writerIterator = writers.iterator();
			StringField id;
			while(imageIterator.hasNext()) {
				nextImage = imageIterator.next();
				img = ImageIO.read(new FileInputStream(nextImage));
				for(String feature: features) {
					document = builderIterator.next().createDocument(img, nextImage);
					id =new StringField(DocumentBuilder.FIELD_NAME_IDENTIFIER, pathToId.get(document.get(DocumentBuilder.FIELD_NAME_IDENTIFIER)), Field.Store.YES);
					document.removeField(DocumentBuilder.FIELD_NAME_IDENTIFIER);
					document.add(id);
					writerIterator.next().addDocument(document);
				}
				builderIterator = builders.iterator();
				writerIterator = writers.iterator();
			}
			for(String feature: features) {
				writerIterator.next().close();
			}
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

	}
	
	public static void index2(String pathToIndexes , String pathToImages, String[] features, HashMap<String,String> pathToId, boolean overwrite) {
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
				File fileOrFolderCheck = new File(pathToImages);
				ArrayList<String> images;
				if (fileOrFolderCheck.isDirectory()) {
					images = FileUtils.getAllImages(new File(pathToImages), false); //descend into sub-directories? false
				}
				else {
					images = new ArrayList<String>();
					images.add(pathToImages);
				}
				Iterator<String> imageIterator = images.iterator();
				while (imageIterator.hasNext()) {
					String nextImage = imageIterator.next();
					BufferedImage img = ImageIO.read(new FileInputStream(nextImage)); //TODO make buffered image once for all features
					Document document = builder.createDocument(img, nextImage); //TODO overwrite ID
					String recid = pathToId.get(document.get(DocumentBuilder.FIELD_NAME_IDENTIFIER));
					document.removeField(DocumentBuilder.FIELD_NAME_IDENTIFIER);
					document.add(new StringField(DocumentBuilder.FIELD_NAME_IDENTIFIER, recid, Field.Store.YES));
					writer.addDocument(document);
				}
				writer.close();
			} catch (IOException e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}			
		}
	}
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
	public static void index(String pathToIndexes , String pathToImages, String[] features, HashMap<String,String> pathToId) {
		index(pathToIndexes, pathToImages, features, pathToId, false);
	}
	
	private static DocumentBuilder getBuilder(String feature) {
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
        // TODO add support for SIFT, MSER, etc
        return null;
        
	}
	
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
                writer.updateDocument(toDel, document);
                //writer.forceMergeDeletes(); // Use if we need update to be immediately visible
		        writer.close();
			}
	        System.out.println(imageID + " successfully updated!");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
	}
	
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
		        writer.forceMerge(1); // may need to change this...
		        //writer.commit();
		       // writer.deleteUnusedFiles();
//		        writer.close(true);
		        writer.close();
			}
	        System.out.println(imageID + " successfully deleted!");
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public static ImageSearchHits[] search(String pathToSearch, String pathToIndexes, String[] features) { //input: list of paths to images, list of recids (same order and length)
		int numberOfFeatures = features.length;
		ImageSearchHits[] hits = new ImageSearchHits[numberOfFeatures];
		int numHits = 0;
		try {
			FileInputStream in = new FileInputStream(pathToSearch);
	        BufferedImage buff = ImageIO.read(in);
			for (String feature: features) {
				IndexReader reader = DirectoryReader.open(FSDirectory.open(new File(pathToIndexes+"/"+feature)));
				ImageSearcher searcher = getSearcher(feature);
                hits[numHits] = searcher.search(buff, reader);
                reader.close();                  
                numHits ++;				
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return hits;
	}

	private static ImageSearcher getSearcher(String feature) {
		int numResults = 60; //make it sent as parameter for different use cases, also to check the index actually has enough elements (otherwise we get null pointer exception...???)
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
        // TODO add support for SIFT, MSER, etc
        return null;
					
	}
	
}