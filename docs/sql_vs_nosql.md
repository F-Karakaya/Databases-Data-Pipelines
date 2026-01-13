# SQL vs NoSQL: Strategic Selection

## Philosophy
In this project, we demonstrate that SQL and NoSQL are not mutually exclusive but complimentary. The choice depends entirely on the nature of the data and the access patterns.

## PostgreSQL (SQL)
**Used for**: `sensors`, `sensor_readings`

**Why?**
1.  **Structure is Known**: A sensor reading always has a value, unit, and timestamp. It rarely changes.
2.  **Join Integrity**: We need to guarantee that every reading belongs to a valid sensor. Foreign Keys enforce this strictly.
3.  **Complex Analytics**: We perform window functions (moving averages) and CTEs which are native and highly optimized in SQL.

**Trade-off**: Schema changes (e.g., adding a new field for half the rows) require migrations (ALTER TABLE) which can be heavy.

## MongoDB (NoSQL)
**Used for**: `user_events`

**Why?**
1.  **Schema Evolution**: User events change often. Today we track 'clicks', tomorrow we might track 'hover_duration' or 'mouse_trajectory'. MongoDB allows us to dump this data without rewriting the schema.
2.  **High Write Throughput**: In a real scale scenario, ingestion of raw logs is write-heavy. MongoDB's document model allows for fast localized writes without complex relation checks.
3.  **Hierarchical Data**: Events often have nested metadata (device info, session context) which maps 1:1 to JSON documents.

**Trade-off**: Joins are expensive ($lookup). Complex aggregations can use more memory than SQL equivalents.

## Vector Database (Qdrant)
**Used for**: `product_embeddings`

**Why?**
*   Standard SQL/NoSQL cannot efficient calculate Cosine Similarity on arrays of 384 floats. Qdrant uses HNSW (Hierarchical Navigable Small World) graphs to index these vectors for millisecond-speed retrieval.
