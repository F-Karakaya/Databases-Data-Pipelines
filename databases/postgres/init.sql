-- PostgreSQL Initialization Script
-- Purpose: Sets up the schema for sensor data and core business entities.
-- Author: Furkan Karakaya

-- Create extension for UUIDs if needed, though we use VARCHAR for simplicity here
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==========================================
-- 1. Sensors Table
-- ==========================================
DROP TABLE IF EXISTS sensor_readings;
DROP TABLE IF EXISTS sensors;

CREATE TABLE sensors (
    sensor_id VARCHAR(50) PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    model VARCHAR(50),
    firmware VARCHAR(50),
    install_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE sensors IS 'Stores metadata for all IoT sensors.';

-- ==========================================
-- 2. Sensor Readings Table (Time-Series)
-- ==========================================
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50) REFERENCES sensors(sensor_id),
    reading FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'active'
);

COMMENT ON TABLE sensor_readings IS 'High-volume table containing individual sensor measurements.';

-- Index for faster time-range queries
CREATE INDEX idx_readings_timestamp ON sensor_readings(timestamp);
CREATE INDEX idx_readings_sensor_id ON sensor_readings(sensor_id);

-- ==========================================
-- 3. Initial Sample Data (Seed)
-- ==========================================
INSERT INTO sensors (sensor_id, location, model, firmware) VALUES
('SN-001', 'Warehouse-A', 'TempX-2000', 'v1.2'),
('SN-002', 'Warehouse-A', 'HumidY-500', 'v1.2'),
('SN-003', 'Warehouse-B', 'BaroZ-100', 'v1.0'),
('SN-004', 'Entrance-Main', 'MotionSense-Pro', 'v2.0');

INSERT INTO sensor_readings (sensor_id, reading, unit, timestamp, status) VALUES
('SN-001', 22.1, 'celcius', NOW() - INTERVAL '1 hour', 'active'),
('SN-001', 22.3, 'celcius', NOW() - INTERVAL '30 minutes', 'active'),
('SN-002', 45.0, 'humidity_percent', NOW() - INTERVAL '1 hour', 'active'),
('SN-004', 1.0, 'motion_binary', NOW() - INTERVAL '15 minutes', 'triggered');

-- Validation Query
SELECT count(*) as initial_sensor_count FROM sensors;
