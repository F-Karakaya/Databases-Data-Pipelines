-- Analytical SQL Queries
-- Purpose: Demonstrate complex SQL capabilities including Windows Functions, CTEs, and Aggregations.
-- Author: Furkan Karakaya

-- ==========================================
-- 1. Daily Average Reading per Sensor
-- ==========================================
-- Calculates the average reading for each sensor per day.
SELECT 
    sensor_id,
    DATE(timestamp) as reading_date,
    ROUND(AVG(reading)::numeric, 2) as avg_reading,
    unit
FROM sensor_readings
GROUP BY sensor_id, DATE(timestamp), unit
ORDER BY reading_date DESC, sensor_id;

-- ==========================================
-- 2. Window Function: Moving Average
-- ==========================================
-- Calculates a 3-period moving average for temperature sensors.
SELECT 
    sensor_id,
    timestamp,
    reading,
    ROUND(
        AVG(reading) OVER (
            PARTITION BY sensor_id 
            ORDER BY timestamp 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        )::numeric, 2
    ) as moving_avg_3_periods
FROM sensor_readings
WHERE unit = 'celcius'
ORDER BY sensor_id, timestamp;

-- ==========================================
-- 3. CTE: Sensors with Alerts
-- ==========================================
-- id sensors that have reported "warning" or "triggered" status in the last 24 hours.
WITH RecentAlerts AS (
    SELECT DISTINCT sensor_id
    FROM sensor_readings
    WHERE status IN ('warning', 'triggered')
      AND timestamp >= NOW() - INTERVAL '24 hours'
)
SELECT 
    s.sensor_id,
    s.location,
    s.model
FROM sensors s
JOIN RecentAlerts ra ON s.sensor_id = ra.sensor_id;

-- ==========================================
-- 4. Hourly Activity Heatmap
-- ==========================================
-- Counts number of readings per hour to identify peak activity times.
SELECT 
    EXTRACT(HOUR FROM timestamp) as hour_of_day,
    COUNT(*) as reading_count
FROM sensor_readings
GROUP BY 1
ORDER BY 1;
