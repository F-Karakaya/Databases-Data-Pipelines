import os
import json
import logging
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from embedding_model import EmbeddingModel
from qdrant_client import QdrantClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - RECOMMENDER - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "product_embeddings"

class Recommender:
    def __init__(self):
        self.encoder = EmbeddingModel()
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    def get_recommendations_by_text(self, query, top_k=3):
        """
            Recommend products based on text query (Search).
        """
        try:
            logger.info(f"Generating recommendations for query: '{query}'")
            query_vector = self.encoder.encode(query).tolist()
            
            search_result = self.qdrant.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=top_k
            )
            
            recommendations = []
            for hit in search_result:
                recommendations.append({
                    "product_id": hit.payload.get("product_id"),
                    "description": hit.payload.get("description"),
                    "category": hit.payload.get("category"),
                    "similarity_score": hit.score,
                    "reason": "Matched content description"
                })
            
            return recommendations
        except Exception as e:
            logger.error(f"Recommendation failed: {e}")
            return []

    def recommend_for_user_history(self, user_history_descriptions, top_k=3):
        """
        Recommend products based on a list of product descriptions user has liked/viewed.
        Demonstrates aggregation of vectors (User Profile Vector).
        """
        try:
            if not user_history_descriptions:
                return []
            
            logger.info(f"Generating user profile from {len(user_history_descriptions)} items...")
            
            # Generate vectors for all history items
            history_vectors = self.encoder.encode(user_history_descriptions)
            
            # Create Average User Vector
            user_profile_vector = np.mean(history_vectors, axis=0).tolist()
            
            search_result = self.qdrant.search(
                collection_name=COLLECTION_NAME,
                query_vector=user_profile_vector,
                limit=top_k
            )
            
            recommendations = []
            for hit in search_result:
                recommendations.append({
                    "product_id": hit.payload.get("product_id"),
                    "description": hit.payload.get("description"),
                    "score": hit.score,
                    "reason": "Based on aggregate user history"
                })
                
            return recommendations
            
        except Exception as e:
            logger.error(f"User history recommendation failed: {e}")
            return []

def generate_sample_outputs():
    """ Runs the recommender and saves results to file. """
    recommender = Recommender()
    
    output_data = {
        "text_search_example": [],
        "user_profile_example": []
    }
    
    # 1. Text Search Scenario
    query = "wireless headphones for gym"
    output_data["text_search_example"] = recommender.get_recommendations_by_text(query)
    
    # 2. User History Scenario
    # User liked Sci-Fi books
    history = [
        "Science fiction novel about interstellar travel",
        "Space opera with aliens" # Hypothetical 
    ]
    output_data["user_profile_example"] = recommender.recommend_for_user_history(history)
    
    # Save Output
    os.makedirs("recommendation", exist_ok=True)
    with open("recommendation/recommendations.json", "w") as f:
        json.dump(output_data, f, indent=2)
    logger.info("Saved recommendations.json")

if __name__ == "__main__":
    generate_sample_outputs()
