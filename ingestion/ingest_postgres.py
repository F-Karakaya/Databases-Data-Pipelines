import os
import pandas as pd
import json
import psycopg2
from psycopg2.extras import execute_values
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_NAME = os.getenv("POSTGRES_DB", "pipeline_db")
DB_USER = os.getenv("POSTGRES_USER", "admin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "password123")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_db_connection():
    """Establishes connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def ingest_sensor_data(json_file_path):
    """
    Reads sensor data from JSON and inserts into PostgreSQL.
    """
    if not os.path.exists(json_file_path):
        logger.error(f"File not found: {json_file_path}")
        return

    try:
        # Load JSON data
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} records from {json_file_path}")

        conn = get_db_connection()
        if not conn:
            return

        cursor = conn.cursor()

        # Prepare data for bulk insert
        # Assuming sensors already exist or we upsert. For simplicity, we insert readings.
        # We also need to ensure sensor IDs exist in 'sensors' table or insert them first.
        
        # 1. UPSERT Sensors
        sensors_seen = {}
        for record in data:
            s_id = record['sensor_id']
            if s_id not in sensors_seen:
                sensors_seen[s_id] = {
                   'sensor_id': s_id,
                   'location': record.get('location', 'Unknown'),
                   'model': record.get('metadata', {}).get('model', 'Unknown'),
                   'firmware': record.get('metadata', {}).get('firmware', 'v1.0')
                }
        
        sensor_values = [(v['sensor_id'], v['location'], v['model'], v['firmware']) for v in sensors_seen.values()]
        
        logger.info(f"Upserting {len(sensor_values)} sensors...")
        insert_sensor_query = """
            INSERT INTO sensors (sensor_id, location, model, firmware)
            VALUES %s
            ON CONFLICT (sensor_id) DO UPDATE 
            SET location = EXCLUDED.location,
                model = EXCLUDED.model,
                firmware = EXCLUDED.firmware;
        """
        execute_values(cursor, insert_sensor_query, sensor_values)
        conn.commit()

        # 2. INSERT Readings
        reading_values = [
            (
                r['sensor_id'],
                r['reading'],
                r['unit'],
                r['timestamp'],
                r.get('status', 'active')
            ) for r in data
        ]
        
        logger.info(f"Inserting {len(reading_values)} readings...")
        insert_reading_query = """
            INSERT INTO sensor_readings (sensor_id, reading, unit, timestamp, status)
            VALUES %s
        """
        execute_values(cursor, insert_reading_query, reading_values)
        conn.commit()
        
        logger.info("Ingestion to PostgreSQL completed successfully.")
        
        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")

if __name__ == "__main__":
    DATA_PATH = os.path.join("data", "raw", "sensor_stream.json")
    ingest_sensor_data(DATA_PATH)
