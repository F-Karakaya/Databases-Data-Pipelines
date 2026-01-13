# Data Pipeline Architecture

## Overview
This document explains the end-to-end data flow within the repository, describing how data moves from ingestion to storage and finally to consumption by downstream applications.

## High-Level Data Flow

1.  **Ingestion Layer**
    *   **Sources**: IoT Sensors (JSON stream) and User Events (CSV logs).
    *   **Mechanism**: Python scripts in `ingestion/` parse raw files, validation schemas, and normalize data.
    *   **Routing**:
        *   Structured sensor readings -> **PostgreSQL**.
        *   Semi-structured user events -> **MongoDB**.
        *   Unstructured product descriptions -> **Vector DB (Qdrant)** via Embedding Model.

2.  **Storage Layer**
    *   **PostgreSQL**: Serves as the primary data warehouse for time-series sensor data and relational entities (Sensors).
    *   **MongoDB**: Acts as a Data Lake for flexible user event logs, allowing for schema evolution without downtime.
    *   **Qdrant**: Stores high-dimensional vector embeddings (384-dim) for semantic search.

3.  **Processing Layer**
    *   **Batch Pipeline**: Run nightly (simulated). Extracts raw logs, performs data cleaning (removal of nulls), enrichment (interaction scoring), and loads into a processed table/collection.
    *   **Streaming Pipeline**: Simulates real-time ingestion. Generates synthetic sensor readings and pushes them immediately to the database to test write throughput and latency.

4.  **Consumption Layer**
    *   **Analytics**: SQL queries and Mongo aggregations provide insights into system health and user behavior.
    *   **Recommendation Engine**: Utilizes Qdrant to find similar products based on content (descriptions) or user history (profile vectors).

## Key Architectural Decisions

*   **Hybrid Database Approach**: We strictly adhere to the "polyglot persistence" pattern. We do not force JSON logs into SQL tables, nor do we put strict relational sensor configurations into NoSQL. This optimizes for both write performance (Mongo) and analytical query power (Postgres).
*   **Vector Search**: Instead of simple keyword matching, we use semantic search. A query for "running shoes" finds "marathon footwear" because they are close in vector space, even if they share no words.
*   **Dockerized Infrastructure**: All services run in isolated containers, ensuring reproducibility across environments (Dev/Test/Prod).
