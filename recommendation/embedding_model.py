import os
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - EMBEDDING - %(message)s')
logger = logging.getLogger(__name__)

class EmbeddingModel:
    """
    Singleton wrapper for the SentenceTransformer model to ensure efficient resource usage.
    """
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingModel, cls).__new__(cls)
            cls.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            try:
                logger.info(f"Loading embedding model: {cls.model_name}...")
                cls._model = SentenceTransformer(cls.model_name)
                logger.info("Model loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                cls._model = None
        return cls._instance

    def encode(self, text_or_list):
        """
        Generates embeddings for a string or list of strings.
        """
        if self._model is None:
            raise RuntimeError("Embedding model is not initialized.")
        
        # Check for CUDA availability (optional optimization)
        device = 'cuda' if os.environ.get('CUDA_VISIBLE_DEVICES') else 'cpu'
        
        return self._model.encode(text_or_list, device=device)

if __name__ == "__main__":
    # Test
    model = EmbeddingModel()
    vector = model.encode("Test sentence")
    print(f"Vector dimension: {len(vector)}")
