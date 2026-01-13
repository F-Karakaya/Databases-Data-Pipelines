import os
import pandas as pd
import logging
from sqlalchemy import create_engine
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipelines/pipeline_output.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("BatchPipeline")

# Configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "password123")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "pipeline_db")

DB_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

def extract_data(file_path):
    """
    EXTRACT: Read raw data from CSV files.
    """
    logger.info(f"Extracting data from {file_path}...")
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Extracted {len(df)} rows.")
        return df
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return None

def transform_data(df):
    """
    TRANSFORM: Clean and enrich data.
    - Filter invalid rows
    - Calculate derived metrics
    - Normalize text
    """
    logger.info("Transforming data...")
    try:
        # 1. Cleaning: Drop rows with missing critical IDs
        initial_count = len(df)
        df_clean = df.dropna(subset=['user_id', 'event_type'])
        logger.info(f"Dropped {initial_count - len(df_clean)} rows with missing IDs.")

        # 2. Enrichment: Flag high-value events
        df_clean['is_conversion'] = df_clean['event_type'].map(lambda x: 1 if x == 'purchase' else 0)

        # 3. Normalization: Lowercase category
        df_clean['category_normalized'] = df_clean['category'].str.lower()

        # 4. Feature Engineering: Interaction Score (heuristic)
        event_weights = {
            'view_item': 1,
            'add_to_cart': 5,
            'purchase': 10,
            'search': 2,
            'login': 0
        }
        df_clean['interaction_score'] = df_clean['event_type'].map(event_weights).fillna(1)
        
        logger.info("Transformation complete.")
        return df_clean
    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        return None

def load_data(df, table_name):
    """
    LOAD: Write processed data to PostgreSQL.
    """
    logger.info(f"Loading data into table '{table_name}'...")
    try:
        engine = create_engine(DB_URL)
        # Using 'replace' for demo purposes; 'append' is typical for production pipelines
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logger.info("Load complete.")
    except Exception as e:
        logger.error(f"Load failed: {e}")

def run_pipeline():
    """
    Orchestrates the ETL process.
    """
    logger.info("Starting Batch Pipeline...")
    
    # Define paths
    raw_data_path = os.path.join("data", "raw", "user_events.csv")
    processed_artifact_path = os.path.join("data", "processed", "cleaned_events.csv")
    
    # 1. Extract
    df_raw = extract_data(raw_data_path)
    if df_raw is None: return

    # 2. Transform
    df_transformed = transform_data(df_raw)
    if df_transformed is None: return

    # Save intermediate artifact
    os.makedirs(os.path.dirname(processed_artifact_path), exist_ok=True)
    df_transformed.to_csv(processed_artifact_path, index=False)
    logger.info(f"Saved processed data to {processed_artifact_path}")

    # 3. Load
    load_data(df_transformed, "processed_user_events")
    
    logger.info("Batch Pipeline finished successfully.")

if __name__ == "__main__":
    run_pipeline()
