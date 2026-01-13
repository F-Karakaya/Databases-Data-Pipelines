import os
import time
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "product_embeddings"
VECTOR_SIZE = 384  # Matching all-MiniLM-L6-v2 dimension

def create_index():
    """
    Initializes Qdrant client and recreates the collection with specific vector parameters.
    """
    logger.info(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}...")
    
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == COLLECTION_NAME for c in collections)
        
        if exists:
            logger.warning(f"Collection '{COLLECTION_NAME}' already exists. Recreating it...")
            client.delete_collection(collection_name=COLLECTION_NAME)
        
        # Create collection with Cosine distance
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )
        
        # create payload index for filtering
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name="category",
            field_schema="keyword"
        )
        
        logger.info(f"Successfully created collection '{COLLECTION_NAME}' with size {VECTOR_SIZE} and Cosine distance.")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create index: {e}")
        return False

if __name__ == "__main__":
    # Wait for service to be potentially ready if running in orchestration
    # time.sleep(5) 
    create_index()
