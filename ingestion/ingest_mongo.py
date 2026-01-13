import os
import pandas as pd
import json
from pymongo import MongoClient
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password123")
DB_NAME = "events_db"
COLLECTION_NAME = "user_events"

def ingest_events(csv_file_path):
    """
    Reads user events from CSV, transforms to JSON-like structure, and loads into MongoDB.
    """
    if not os.path.exists(csv_file_path):
        logger.error(f"File not found: {csv_file_path}")
        return

    try:
        # Connect to MongoDB
        client = MongoClient(
            host=MONGO_HOST,
            port=MONGO_PORT,
            username=MONGO_USER,
            password=MONGO_PASS
        )
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        logger.info(f"Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")

        # Read CSV
        df = pd.read_csv(csv_file_path)
        logger.info(f"Loaded {len(df)} records from CSV.")

        # Transform Data
        # - Convert timestamps to datetime objects
        # - Handle distinct attributes for Product vs Search vs Login
        # - Structure into a document format
        
        documents = []
        for _, row in df.iterrows():
            doc = {
                "event_id": row.get('event_id'),
                "user_id": row.get('user_id'),
                "event_type": row.get('event_type'),
                "timestamp": pd.to_datetime(row.get('timestamp')),
                "device": row.get('device'),
            }
            
            # Add conditional fields (removing NaNs)
            if pd.notna(row.get('product_id')):
                doc['product_id'] = row['product_id']
                
            if pd.notna(row.get('category')):
                doc['category'] = row['category']
                
            if pd.notna(row.get('session_duration')):
                doc['session_duration'] = float(row['session_duration'])

            documents.append(doc)

        # Bulk Insert
        if documents:
            result = collection.insert_many(documents)
            logger.info(f"Successfully inserted {len(result.inserted_ids)} documents.")
        else:
            logger.warning("No documents to insert.")

        client.close()

    except Exception as e:
        logger.error(f"MongoDB Ingestion failed: {e}")

if __name__ == "__main__":
    DATA_PATH = os.path.join("data", "raw", "user_events.csv")
    ingest_events(DATA_PATH)
