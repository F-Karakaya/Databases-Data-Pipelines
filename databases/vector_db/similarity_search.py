import os
import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "product_embeddings"
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

def search_products(query_text, top_k=5, category_filter=None):
    """
    Performs a semantic search on the product catalog.
    
    Args:
        query_text (str): The user's search query.
        top_k (int): Number of results to return.
        category_filter (str, optional): Filter results by category.
        
    Returns:
        list: List of similar products with scores.
    """
    try:
        # Load model for query embedding
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
        query_vector = model.encode(query_text).tolist()
        
        # Connect to Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Define filter if provided
        query_filter = None
        if category_filter:
            from qdrant_client.http import models
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="category",
                        match=models.MatchValue(value=category_filter)
                    )
                ]
            )
            
        logger.info(f"Searching for: '{query_text}' (Filter: {category_filter})")
        
        search_result = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        
        results = []
        for hit in search_result:
            results.append({
                "product_id": hit.payload.get("product_id"),
                "description": hit.payload.get("description"),
                "category": hit.payload.get("category"),
                "score": hit.score
            })
            
        return results

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return []

if __name__ == "__main__":
    # Example Usage
    query = "running shoes for marathon"
    results = search_products(query)
    
    print(f"\nResults for '{query}':")
    print(json.dumps(results, indent=2))
    
    # Save results to output
    output_path = os.path.join("outputs", "vector_search_results.json")
    os.makedirs("outputs", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_path}")
