import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http import models
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

# Sample Product Data (Simulated Catalog)
# In a real scenario, this would come from a database query
SAMPLE_PRODUCTS = [
    {"product_id": "PROD-999", "category": "Electronics", "description": "High-end smartphone with OLED display and 5G connectivity."},
    {"product_id": "PROD-123", "category": "Books", "description": "Science fiction novel about interstellar travel and AI ethics."},
    {"product_id": "PROD-456", "category": "Clothing", "description": "Men's cotton t-shirt, breathable fabric, blue color."},
    {"product_id": "PROD-789", "category": "Sports", "description": "Professional tennis racket, lightweight carbon fiber."},
    {"product_id": "PROD-124", "category": "Books", "description": "Cookbook featuring 100 vegan recipes for beginners."},
    {"product_id": "PROD-321", "category": "Garden", "description": "Automatic watering system for indoor plants."},
    {"product_id": "PROD-888", "category": "Electronics", "description": "Wireless noise-canceling headphones with long battery life."},
    {"product_id": "PROD-555", "category": "Automotive", "description": "All-weather car floor mats, durable rubber material."}
]

def ingest_vectors():
    """
    Generates embeddings for products and uploads them to Qdrant.
    """
    try:
        # Load Model
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
        
        # Connect to Qdrant
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Generate Embeddings
        descriptions = [p['description'] for p in SAMPLE_PRODUCTS]
        logger.info("Generating embeddings...")
        embeddings = model.encode(descriptions)
        
        # Prepare Points
        points = []
        for i, product in enumerate(SAMPLE_PRODUCTS):
            points.append(models.PointStruct(
                id=i + 1, # Simple integer ID for demo
                vector=embeddings[i].tolist(),
                payload=product
            ))
            
        # Upsert to Qdrant
        logger.info(f"Upserting {len(points)} vectors to '{COLLECTION_NAME}'...")
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points
        )
        
        logger.info("Vector ingestion completed successfully.")

    except Exception as e:
        logger.error(f"Vector ingestion failed: {e}")

if __name__ == "__main__":
    ingest_vectors()
