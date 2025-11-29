#!/usr/bin/env python3
"""
Build FAISS index from Markdown files in data/docs/.

This script:
1. Reads all .md files from data/docs/ directory
2. Extracts YAML front-matter and content from each file
3. Generates embeddings using sentence-transformers (all-MiniLM-L6-v2)
4. Builds FAISS vector index for fast similarity search
5. Creates doc_map.json mapping document IDs to metadata
6. Saves index and map files to afroken_llm_backend/

Creates faiss_index.idx and doc_map.json in afroken_llm_backend/
"""

# Standard library imports
import json      # For reading/writing doc_map.json
import re        # For removing Sources section from Markdown
from functools import lru_cache  # For caching the embedding model
from pathlib import Path  # For cross-platform file path handling

# Third-party imports
import numpy as np  # For array operations and FAISS compatibility
import yaml  # For parsing YAML front-matter from Markdown files
from sentence_transformers import SentenceTransformer  # For generating embeddings

# ===== FAISS AVAILABILITY CHECK =====
# Try to import FAISS library (fast vector search)
# FAISS is optional - if not available, we use pure Python cosine similarity
try:
    import faiss  # Facebook AI Similarity Search library
    FAISS_AVAILABLE = True  # Flag indicating FAISS is installed
except ImportError:
    # FAISS not available (common on Windows or if not installed)
    FAISS_AVAILABLE = False
    # Print warning but continue - Python fallback will be used
    print("Warning: faiss-cpu not available. Will use pure Python cosine similarity.")

@lru_cache(maxsize=1)
def load_model():
    """
    Load and cache SentenceTransformer model using LRU cache.
    
    This function is decorated with @lru_cache to ensure the model is only
    loaded once, even if called multiple times. This significantly improves
    performance when re-indexing or processing multiple files.
    
    Returns:
        SentenceTransformer model instance (all-MiniLM-L6-v2)
    
    Note:
        Model is downloaded on first use if not present locally.
        Subsequent calls return the cached model instance.
    """
    # Load the all-MiniLM-L6-v2 model
    # This is a lightweight, fast model producing 384-dimensional embeddings
    # Good balance between quality and speed for RAG applications
    return SentenceTransformer('all-MiniLM-L6-v2')

def extract_content_from_md(md_file: Path) -> tuple[str, dict]:
    """
    Extract YAML front-matter and content from Markdown file.
    
    Markdown files created by chunk_and_write_md.py have this structure:
    ---
    title: "..."
    category: "..."
    ...
    ---
    
    Content here...
    
    Sources:
    - https://...
    
    This function separates the YAML metadata from the actual content.
    
    Args:
        md_file: Path to the Markdown file
    
    Returns:
        Tuple of (content_text, metadata_dict) where:
        - content_text: The actual Markdown content (YAML and Sources removed)
        - metadata_dict: Dictionary of YAML front-matter fields
    
    Example:
        extract_content_from_md(Path("001_kra_pin.md"))
        # Returns: ("Register for KRA PIN...", {"title": "KRA PIN", "category": "service_workflow"})
    """
    # Read entire file content
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ===== PARSE YAML FRONT-MATTER =====
    # Check if file starts with YAML front-matter delimiter
    # Standard Markdown front-matter format: --- ... ---
    if content.startswith('---'):
        # Split on '---' delimiter (max 3 parts: before, YAML, after)
        # Example: "---\ntitle: X\n---\nContent" -> ["", "\ntitle: X\n", "\nContent"]
        parts = content.split('---', 2)
        
        # Check if we got all 3 parts (before, YAML, content)
        if len(parts) >= 3:
            # parts[1] is the YAML content (between the two '---' delimiters)
            yaml_str = parts[1]
            
            # parts[2] is everything after the closing '---' (the Markdown content)
            md_content = parts[2].strip()  # Remove leading/trailing whitespace
            
            # Parse YAML string into Python dictionary
            try:
                # yaml.safe_load() parses YAML safely (prevents code execution)
                # Returns dict like {"title": "...", "category": "...", ...}
                metadata = yaml.safe_load(yaml_str)
            except:
                # If YAML parsing fails (malformed YAML), use empty dict
                # This allows script to continue even with bad YAML
                metadata = {}
        else:
            # If split didn't work as expected, treat entire file as content
            metadata = {}
            md_content = content
    else:
        # If file doesn't start with '---', assume no front-matter
        # Treat entire file as content
        metadata = {}
        md_content = content
    
    # ===== REMOVE SOURCES SECTION =====
    # Remove "Sources:\n- https://..." section from end of content
    # This section is for citation but not needed in embeddings
    # re.DOTALL flag makes . match newlines too
    # Pattern matches from "\nSources:" to end of string
    md_content = re.sub(r'\nSources:.*$', '', md_content, flags=re.DOTALL)
    
    # Return content and metadata
    return md_content, metadata

def py_cosine_search(embeddings: np.ndarray, query_emb: np.ndarray, topk: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """
    Pure Python cosine similarity search (fallback if FAISS unavailable).
    
    This function implements cosine similarity search using only NumPy.
    Used when FAISS library is not available (e.g., on Windows without proper installation).
    
    Cosine similarity measures the angle between vectors (not magnitude):
    - 1.0 = identical direction (most similar)
    - 0.0 = perpendicular (unrelated)
    - -1.0 = opposite direction (least similar)
    
    Args:
        embeddings: 2D numpy array of shape (N, 384) where N is number of documents
                    Each row is an embedding vector for one document
        query_emb: 1D numpy array of shape (384,) - the query embedding
        topk: Number of top results to return (default 3)
    
    Returns:
        Tuple of (distances, indices) where:
        - distances: 1D array of shape (topk,) - cosine distances (lower = more similar)
        - indices: 1D array of shape (topk,) - indices of top-k documents in embeddings array
    
    Example:
        embeddings = np.array([[0.1, 0.2, ...], [0.3, 0.4, ...]])  # 2 docs, 384 dims each
        query = np.array([0.1, 0.2, ...])  # 1 query, 384 dims
        distances, indices = py_cosine_search(embeddings, query, topk=2)
        # Returns: (array([0.05, 0.12]), array([0, 1]))
        # Document 0 is most similar (distance 0.05), document 1 is second (distance 0.12)
    """
    # ===== NORMALIZE EMBEDDINGS =====
    # Normalize query embedding to unit length
    # np.linalg.norm() computes Euclidean norm (vector length)
    # + 1e-8 prevents division by zero (tiny epsilon)
    # Result: query_norm has length 1.0
    query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
    
    # Normalize all document embeddings to unit length
    # axis=1 means normalize each row (each document) independently
    # keepdims=True preserves 2D shape for broadcasting
    # Result: each row in emb_norms has length 1.0
    emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
    
    # ===== COMPUTE COSINE SIMILARITY =====
    # Cosine similarity = dot product of normalized vectors
    # np.dot() computes matrix-vector product: emb_norms (N x 384) @ query_norm (384,)
    # Result: similarities is 1D array of shape (N,) with similarity scores
    # Higher value = more similar (closer angle between vectors)
    similarities = np.dot(emb_norms, query_norm)
    
    # ===== GET TOP-K RESULTS =====
    # np.argsort(-similarities) sorts indices by similarity (descending, highest first)
    # Negative sign because argsort sorts ascending, we want descending
    # [:topk] takes only the top k indices
    # Result: top_indices contains indices of most similar documents
    top_indices = np.argsort(-similarities)[:topk]
    
    # Convert similarity to distance (for consistency with FAISS)
    # Distance = 1 - similarity
    # Lower distance = more similar (matches FAISS convention)
    # similarities[top_indices] gets similarity scores for top-k documents
    top_distances = 1 - similarities[top_indices]  # Convert to distance
    
    # Return distances and indices
    return top_distances, top_indices

def main():
    """
    Main function: Builds FAISS vector index from Markdown corpus.
    
    This function:
    1. Finds all .md files in data/docs/
    2. Extracts content and metadata from each file
    3. Generates embeddings using sentence-transformers
    4. Builds FAISS index (or saves NumPy array for Python fallback)
    5. Creates doc_map.json with document metadata
    6. Saves index and map files for use by chat endpoint
    """
    # Import argparse here (only used in main)
    import argparse
    
    # ===== COMMAND-LINE ARGUMENT PARSING =====
    parser = argparse.ArgumentParser(description='Build FAISS index from Markdown files')
    
    # Optional flag: Validate that all embeddings have consistent shape
    # Useful for debugging if some documents produce wrong-sized embeddings
    parser.add_argument('--validate-shapes', action='store_true',
                       help='Validate embedding shapes are consistent')
    args = parser.parse_args()
    
    # ===== PATH SETUP =====
    # Get the directory where this script is located (scripts/rag/)
    script_dir = Path(__file__).parent
    
    # Get backend root (two levels up from scripts/rag/)
    backend_dir = script_dir.parent.parent
    
    # Path to data/docs/ directory (where Markdown files are stored)
    docs_dir = backend_dir / 'data' / 'docs'
    
    # Check if docs directory exists
    if not docs_dir.exists():
        print(f"Error: {docs_dir} not found. Run chunk_and_write_md.py first.")
        return  # Exit if directory doesn't exist
    
    # Ensure directory exists (defensive - shouldn't be needed if chunk script ran)
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # ===== FIND ALL MARKDOWN FILES =====
    # Use glob pattern to find all .md files in docs directory
    # sorted() ensures consistent ordering (alphabetical by filename)
    md_files = sorted(docs_dir.glob('*.md'))
    
    # Check if any files were found
    if not md_files:
        print(f"Error: No .md files found in {docs_dir}")
        return  # Exit if no files found
    
    # Log how many files we'll process
    print(f"Found {len(md_files)} Markdown files")
    
    # ===== LOAD EMBEDDING MODEL =====
    # Load sentence transformer model (cached via @lru_cache)
    # This only loads once, even if called multiple times
    print("Loading sentence transformer model...")
    model = load_model()  # Uses cached model if already loaded
    
    # ===== PROCESS FILES AND EXTRACT CONTENT =====
    # Dictionary mapping document index to metadata
    # Key: integer index (0, 1, 2, ...), Value: dict with title, filename, etc.
    doc_map = {}
    
    # List to store text content for each document (for batch embedding)
    texts = []
    
    # Loop through each Markdown file
    for idx, md_file in enumerate(md_files):
        # Log progress: [1/50] Processing 001_kra_pin.md
        print(f"Processing [{idx+1}/{len(md_files)}] {md_file.name}")
        
        # Extract content and metadata from Markdown file
        # content: Clean text (YAML and Sources removed)
        # metadata: Dictionary of YAML front-matter fields
        content, metadata = extract_content_from_md(md_file)
        
        # ===== BUILD DOCUMENT MAP ENTRY =====
        # Store metadata for this document in doc_map
        # This will be saved as doc_map.json and used by chat endpoint
        doc_map[idx] = {
            # Title from YAML, or use filename stem if not found
            'title': metadata.get('title', md_file.stem),
            
            # Filename for reference (e.g., "001_kra_pin_registration.md")
            'filename': md_file.name,
            
            # First 1000 characters of content (for excerpt display in chat)
            # Full content is in the .md file, this is just for quick reference
            'text': content[:1000],  # Store first 1000 chars for reference
            
            # Source URL from YAML metadata
            'source': metadata.get('source', ''),
            
            # Category from YAML (service_workflow, ministry_faq, etc.)
            'category': metadata.get('category', 'service_workflow'),
            
            # Word count (useful for analytics)
            'word_count': len(content.split()),
            
            # Index position (0, 1, 2, ...) - matches array index in embeddings
            'chunk_index': idx,
            
            # Last updated date from YAML
            'last_scraped': metadata.get('last_updated', ''),
            
            # Last component of URL path (e.g., "pin" from "https://kra.go.ke/services/pin")
            # Useful for quick URL identification
            'url_path': metadata.get('source', '').split('/')[-1] if metadata.get('source') else ''
        }
        
        # Add full content to texts list for batch embedding
        # model.encode() can process multiple texts at once (faster)
        texts.append(content)
    
    # ===== COMPUTE EMBEDDINGS =====
    # Generate embeddings for all documents in batch
    print("Computing embeddings...")
    
    # model.encode() processes all texts at once
    # show_progress_bar=True: Shows progress bar for large batches
    # convert_to_numpy=True: Returns numpy array (not PyTorch tensor)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Convert to float32 dtype (required for FAISS)
    # Model might return float64, but FAISS requires float32
    embeddings = embeddings.astype('float32')  # Ensure float32 for FAISS
    
    # Log embeddings shape for verification
    # Expected: (N, 384) where N is number of documents, 384 is embedding dimension
    print(f"Embeddings shape: {embeddings.shape}")
    
    # ===== VALIDATE SHAPES (IF REQUESTED) =====
    # Optional validation to ensure all embeddings have correct dimension
    if args.validate_shapes:
        expected_dim = 384  # all-MiniLM-L6-v2 produces 384-dimensional embeddings
        
        # Check if embedding dimension matches expected
        # embeddings.shape[1] is the dimension (second axis)
        if embeddings.shape[1] != expected_dim:
            # Raise error if dimension mismatch (would cause FAISS errors)
            raise ValueError(f"Embedding dimension mismatch: expected {expected_dim}, got {embeddings.shape[1]}")
        
        # Log success if validation passed
        print(f"✓ All embeddings have consistent shape: {embeddings.shape}")
    
    # ===== BUILD AND SAVE INDEX =====
    # Paths for output files
    index_file = backend_dir / 'faiss_index.idx'  # FAISS index file
    doc_map_file = backend_dir / 'doc_map.json'  # Document metadata map
    
    if FAISS_AVAILABLE:
        # ===== BUILD FAISS INDEX =====
        # FAISS is available, use it for fast vector search
        print("Building FAISS index...")
        
        # Get embedding dimension (should be 384)
        dimension = embeddings.shape[1]
        
        # Create FAISS index using L2 (Euclidean) distance
        # IndexFlatL2 is simplest index type (exact search, no approximation)
        # Good for small-medium datasets (< 1M vectors)
        index = faiss.IndexFlatL2(dimension)
        
        # Add all embeddings to the index
        # embeddings.astype('float32') ensures correct dtype (FAISS requirement)
        index.add(embeddings.astype('float32'))
        
        # Save index to disk
        # faiss.write_index() saves the index structure for later loading
        faiss.write_index(index, str(index_file))
        print(f"FAISS index saved to {index_file}")
        
    else:
        # ===== SAVE NUMPY ARRAY (PYTHON FALLBACK) =====
        # FAISS not available, save embeddings as NumPy array
        # chat.py will use py_cosine_search() for similarity search
        print("FAISS not available. Saving embeddings as numpy array for Python fallback...")
        
        # Save embeddings array to .npy file
        # np.save() saves numpy array in binary format (efficient, fast loading)
        # .with_suffix('.npy') changes .idx to .npy extension
        np.save(str(index_file.with_suffix('.npy')), embeddings)
        print(f"Embeddings saved to {index_file.with_suffix('.npy')}")
    
    # ===== SAVE DOCUMENT MAP =====
    # Save doc_map as JSON file
    # This file maps document indices to metadata (used by chat endpoint)
    with open(doc_map_file, 'w', encoding='utf-8') as f:
        # json.dump() writes Python dict to JSON file
        # indent=2: Pretty-print with 2-space indentation (readable)
        # ensure_ascii=False: Allow Unicode characters (important for international content)
        json.dump(doc_map, f, indent=2, ensure_ascii=False)
    
    # Log completion
    print(f"Document map saved to {doc_map_file}")
    
    # ===== SUMMARY =====
    # Print final statistics
    print(f"\nIndex complete:")
    print(f"  - Documents: {len(doc_map)}")  # Number of documents indexed
    print(f"  - Embedding dimension: {embeddings.shape[1]}")  # Should be 384
    print(f"  - Index type: {'FAISS' if FAISS_AVAILABLE else 'NumPy (Python fallback)'}")  # Which index type was used

if __name__ == '__main__':
    main()

