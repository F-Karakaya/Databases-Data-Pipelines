# Recommendation Logic & Algorithms

## Content-Based Filtering
Our system implements a **Content-Based Filtering** approach. This means we recommend items similar to those a user liked, based on the item's intrinsic features (in our case, the text description).

### 1. Vectorization (Embedding)
We use the **Sentence Transformers** library (specifically `all-MiniLM-L6-v2`) to convert text descriptions into mathematical vectors.

*   **Input**: "Wireless noise-canceling headphones"
*   **Process**: Passed through a Deep Learning Transformer model.
*   **Output**: A list of 384 floating-point numbers (The Embedding).

This vector represents the "meaning" of the sentence in a high-dimensional space.

### 2. Similarity Metric (Cosine)
To determine if two products are similar, we calculate the **Cosine Similarity** between their vectors.

$$ \text{similarity} = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|} $$

*   If vectors point in the same direction, similarity is 1 (Identical meaning).
*   If orthogonal, similarity is 0 (Unrelated).

### 3. User Profiling
Users are profiled not by their explicit demographics, but by their history.

*   **User History**: [Product A, Product B, Product C]
*   **User Vector**: Average(Vector(A), Vector(B), Vector(C))

We search the Vector Database using this *Average User Vector* as the query. The results are products that are semantically close to the *center* of the user's interests.

## Hybrid Possibilities
While this project focuses on content-based, a production system would combine this with Collaborative Filtering (Matrix Factorization) to account for popularity bias and serendipity.
