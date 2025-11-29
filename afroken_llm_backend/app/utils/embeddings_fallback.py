"""
Embedding helper with fallback to local sentence-transformers model.

This module provides a unified interface for generating text embeddings:
- If EMBEDDING_ENDPOINT environment variable is set, calls HTTP endpoint
- Otherwise, uses local 'all-MiniLM-L6-v2' model (384-dimensional embeddings)

The local model is cached using @lru_cache to avoid reloading on every call.
This significantly improves performance (model loading takes ~1-2 seconds).

If EMBEDDING_ENDPOINT is set, uses HTTP endpoint.
Otherwise uses local 'all-MiniLM-L6-v2' model.
"""

# Standard library imports
import os  # For reading environment variables
from functools import lru_cache  # For caching the model (avoid reloading)
from typing import Optional  # For type hints

# Third-party imports
import httpx  # HTTP client for calling embedding endpoint (sync version)
import numpy as np  # For array operations and type hints
from sentence_transformers import SentenceTransformer  # Local embedding model

# ===== GLOBAL MODEL INSTANCE =====
# Global variable to store the loaded SentenceTransformer model
# Lazy loading: model is only loaded when first needed (not at import time)
# Optional type hint: None initially, SentenceTransformer after first load
_model: Optional[SentenceTransformer] = None

@lru_cache(maxsize=1)
def _load_model():
    """
    Load and cache SentenceTransformer model using LRU cache.
    
    @lru_cache decorator ensures the model is only loaded once:
    - First call: loads model from disk (~1-2 seconds)
    - Subsequent calls: returns cached model (instant)
    
    maxsize=1 means only one model is cached (we only use one model)
    
    Returns:
        SentenceTransformer model instance (all-MiniLM-L6-v2)
    
    Note:
        Model is downloaded automatically on first use if not present.
        Saves to ~/.cache/torch/sentence_transformers/ by default.
    """
    # Load the 'all-MiniLM-L6-v2' model
    # This is a lightweight, fast model that produces 384-dimensional embeddings
    # Good balance between quality and speed for RAG applications
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> np.ndarray:
    """
    Get embedding vector for input text (synchronous version).
    
    This function provides a unified interface for embeddings:
    1. Checks if EMBEDDING_ENDPOINT environment variable is set
    2. If set: calls HTTP endpoint (for remote embedding services)
    3. If not set: uses local sentence-transformers model (offline capable)
    
    The function includes shape validation to ensure embeddings are correct
    dimension (384 for all-MiniLM-L6-v2). This prevents downstream errors.
    
    Args:
        text: Input text to embed (any length, will be truncated by model if needed)
    
    Returns:
        numpy array of shape (384,) containing the embedding vector
        dtype: float32 (required for FAISS compatibility)
    
    Raises:
        ValueError: If embedding shape is not (384,) after generation
    
    Example:
        embedding = get_embedding("How do I register for NHIF?")
        # Returns: array([0.123, -0.456, ..., 0.789], dtype=float32)
        # Shape: (384,)
    """
    # ===== CHECK FOR REMOTE EMBEDDING ENDPOINT =====
    # Read EMBEDDING_ENDPOINT from environment variables
    # If set, use remote service; if None, use local model
    embedding_endpoint = os.getenv('EMBEDDING_ENDPOINT')
    
    if embedding_endpoint:
        # ===== USE HTTP ENDPOINT =====
        # Call remote embedding service via HTTP
        try:
            # Create HTTP client with 30-second timeout
            # Context manager (with) ensures connection is closed after use
            with httpx.Client(timeout=30) as client:
                # POST request to embedding endpoint
                # Expected payload: {"input": "text to embed"}
                # Expected response: {"embedding": [0.1, 0.2, ..., 0.9]}
                response = client.post(
                    embedding_endpoint,  # URL from environment variable
                    json={'input': text}  # Request body with text to embed
                )
                
                # Raise exception if HTTP status code indicates error (4xx, 5xx)
                # This catches 404, 500, etc. and triggers fallback
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Extract embedding array from response
                # data.get('embedding', []) returns empty list if 'embedding' key missing
                # Convert to numpy array with float32 dtype (required for FAISS)
                embedding = np.array(data.get('embedding', []), dtype=np.float32)
                
                # ===== VALIDATE EMBEDDING SHAPE =====
                # Ensure embedding has correct dimensions
                # all-MiniLM-L6-v2 produces 384-dimensional vectors
                # Wrong shape would cause FAISS index errors
                if embedding.shape != (384,):
                    raise ValueError(f"Embedding shape mismatch: expected (384,), got {embedding.shape}")
                
                # Return validated embedding
                return embedding
                
        except Exception as e:
            # If endpoint call fails (network error, timeout, wrong shape, etc.)
            # Log warning and fall through to local model fallback
            print(f"Warning: Embedding endpoint failed: {e}. Falling back to local model.")
    
    # ===== USE LOCAL MODEL (FALLBACK OR DEFAULT) =====
    # Access global model variable
    # 'global' keyword is needed to modify global variable from within function
    global _model
    
    # Lazy loading: only load model on first call
    # Subsequent calls reuse the same model instance (faster)
    if _model is None:
        # Load model using cached loader function
        # @lru_cache ensures this only happens once
        _model = _load_model()
    
    # Generate embedding using the local model
    # encode() converts text to embedding vector
    # convert_to_numpy=True: return as numpy array (not PyTorch tensor)
    embedding = _model.encode(text, convert_to_numpy=True)
    
    # Convert to float32 dtype (required for FAISS)
    # Model might return float64, but FAISS expects float32
    embedding = embedding.astype(np.float32)
    
    # ===== VALIDATE EMBEDDING SHAPE =====
    # Double-check shape is correct (defensive programming)
    # This catches any unexpected model behavior
    if embedding.shape != (384,):
        raise ValueError(f"Embedding shape mismatch: expected (384,), got {embedding.shape}")
    
    # Return validated embedding
    return embedding

