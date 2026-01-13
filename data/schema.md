# Data & Database Schemas

## 1. PostgreSQL Schema (Structured Data)
Used for reliable, ACID-compliant storage of processed sensor data and core user/product entities.

### Table: `sensors`
Stores metadata about physical sensors.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| sensor_id | VARCHAR(50) | PRIMARY KEY | Unique identifier for sensor |
| location | VARCHAR(100) | NOT NULL | Physical location of sensor |
| model | VARCHAR(50) | | Model name |
| firmware | VARCHAR(50) | | Firmware version |
| install_date | TIMESTAMP | DEFAULT NOW() | Installation timestamp |

### Table: `sensor_readings`
Stores time-series data from sensors.
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | SERIAL | PRIMARY KEY | Auto-increment ID |
| sensor_id | VARCHAR(50) | FOREIGN KEY | Reference to sensors table |
| reading | FLOAT | NOT NULL | Numerical value of reading |
| unit | VARCHAR(20) | NOT NULL | Unit of measurement |
| timestamp | TIMESTAMP | NOT NULL | Time of reading (indexed) |
| status | VARCHAR(20) | | Sensor status flag |

---

## 2. MongoDB Schema (Semi-Structured Data)
Used for flexible storage of user interaction events which may have varying attributes.

### Collection: `user_events`
| Field | Type | Description |
|-------|------|-------------|
| _id | ObjectId | MongoDB unique ID |
| event_id | String | Original event ID |
| user_id | String | User identifier |
| event_type | String | e.g., 'view_item', 'purchase' |
| timestamp | ISODate | Event timestamp |
| metadata | Object | Flexible nested object (device, session_info, etc.) |
| product_details | Object | (Optional) Contains category, product_id |

---

## 3. Vector Database Schema (Qdrant)
Used for semantic search and recommendation engine embeddings.

### Collection: `product_embeddings`
- **Vector Size**: 384 (using `all-MiniLM-L6-v2`)
- **Distance Metric**: Cosine

| Payload Field | Type | Description |
|---------------|------|-------------|
| product_id | Keyword | Product identifier |
| description | Text | Text description used for embedding |
| category | Keyword | Product category for filtering |
| price | Float | Product price |

### Collection: `user_profiles`
- **Vector Size**: 384
- **Distance Metric**: Cosine
- **Description**: Aggregate vector representing user's history/preferences.
