package pylire;

import java.util.HashMap;
import java.util.Set;

public class ClueResults {
   double[][] adjacency_matrix;
   HashMap<String,Integer> mapIdToPosition;
  
   public ClueResults(double[][] adjacency_matrix, HashMap<String,Integer> mapIdToPosition) {
           this.adjacency_matrix = adjacency_matrix;
           this.mapIdToPosition = mapIdToPosition;
   }
  
   public double[][] getAdjacencyMatrix() {
      return this.adjacency_matrix;
   }
   public HashMap<String,Integer> getMapIdToPositions() {
      return this.mapIdToPosition;
   }
   public HashMap<Integer,String> getReverseMapping() {
	   HashMap<Integer,String> reverseMap = new HashMap<Integer,String>();
	   Set<String> keys = this.mapIdToPosition.keySet();
	   for (String key: keys) {
		   reverseMap.put(this.mapIdToPosition.get(key), key);
	   }
	   return reverseMap;
   }
}