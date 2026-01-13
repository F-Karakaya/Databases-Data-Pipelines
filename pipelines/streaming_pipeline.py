import time
import json
import random
import logging
import datetime
from ingestion.ingest_postgres import ingest_sensor_data
# We will simulate generating a file and calling the ingest function, 
# or directly calling DB insertion logic if we refactored. 
# For this demo, we'll generate small batches of JSON and call the existing ingest util.

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - STREAM - %(message)s')
logger = logging.getLogger("StreamingPipeline")

def generate_sensor_reading():
    """Generates a single synthetic sensor reading."""
    sensors = ["SN-001", "SN-002", "SN-003", "SN-004"]
    units = {"SN-001": "celcius", "SN-002": "humidity_percent", "SN-003": "hpa", "SN-004": "motion_binary"}
    
    sensor_id = random.choice(sensors)
    base_val = {"SN-001": 22.0, "SN-002": 45.0, "SN-003": 1013.0, "SN-004": 0}[sensor_id]
    
    # Add random noise
    if sensor_id == "SN-004":
        val = float(random.choice([0, 1]))
    else:
        val = round(base_val + random.uniform(-2.0, 2.0), 2)
        
    return {
        "sensor_id": sensor_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "reading": val,
        "unit": units[sensor_id],
        "status": "active"
    }

def run_stream_simulation(iterations=5, delay=2):
    """
    Simulates a streaming source by generating micro-batches and processing them.
    
    Args:
        iterations: Number of batches to generate.
        delay: Seconds between batches.
    """
    logger.info("Starting Streaming Pipeline Simulation...")
    
    temp_file = "data/raw/temp_stream_batch.json"
    
    try:
        for i in range(iterations):
            logger.info(f"Processing Batch {i+1}/{iterations}...")
            
            # 1. Generate Micro-batch
            batch_size = random.randint(1, 3)
            batch_data = [generate_sensor_reading() for _ in range(batch_size)]
            
            # Write to temp file (simulating arrival)
            with open(temp_file, 'w') as f:
                json.dump(batch_data, f)
            
            # 2. Ingest (Consume)
            ingest_sensor_data(temp_file)
            
            time.sleep(delay)
            
        logger.info("Streaming simulation completed.")
        
    except KeyboardInterrupt:
        logger.info("Streaming stopped by user.")
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)

import os
if __name__ == "__main__":
    # Ensure dependencies from parent dir can be imported if running direct
    # In production, this would be a proper module or kafka consumer
    import sys
    sys.path.append(os.getcwd())
    
    run_stream_simulation()
