"""
Chat endpoints for interacting with the AfroKen LLM using RAG.
"""

import os
import json
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Query

from app.schemas import ChatRequest, ChatResponse
from app.config import settings
from app.utils.embeddings_fallback import get_embedding as get_embedding_fallback

import httpx

# FAISS imports with fallback
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False


# Router to be mounted under `/api/v1/chat`.
router = APIRouter()

# Cache for doc_map and index (loaded once at startup)
DOC_MAP_CACHE = None
FAISS_INDEX_CACHE = None
EMBEDDINGS_CACHE = None

def _load_rag_resources():
    """Load RAG resources once and cache them."""
    global DOC_MAP_CACHE, FAISS_INDEX_CACHE, EMBEDDINGS_CACHE
    
    if DOC_MAP_CACHE is not None:
        return  # Already loaded
    
    backend_dir = Path(__file__).parent.parent.parent
    doc_map_file = backend_dir / 'doc_map.json'
    index_file = backend_dir / 'faiss_index.idx'
    embeddings_file = backend_dir / 'faiss_index.npy'
    
    # Load doc_map
    if doc_map_file.exists():
        with open(doc_map_file, 'r', encoding='utf-8') as f:
            DOC_MAP_CACHE = json.load(f)
    
    # Load FAISS index or embeddings
    if FAISS_AVAILABLE and index_file.exists():
        FAISS_INDEX_CACHE = faiss.read_index(str(index_file))
    elif embeddings_file.exists():
        EMBEDDINGS_CACHE = np.load(str(embeddings_file))

def py_cosine_search(embeddings: np.ndarray, query_emb: np.ndarray, topk: int = 3):
    """Pure Python cosine similarity search (fallback if FAISS unavailable)."""
    query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
    emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
    similarities = np.dot(emb_norms, query_norm)
    top_indices = np.argsort(-similarities)[:topk]
    top_distances = 1 - similarities[top_indices]
    return top_distances, top_indices


@router.post("/messages", response_model=ChatResponse)
async def post_message(req: ChatRequest, debug: bool = Query(False, description="Include debug information in response")):
    """
    Accept a user message, retrieve relevant documents, and generate an answer.
    
    If LLM_ENDPOINT and OPENAI_API_KEY are not set, returns top-k retrieved
    documents with excerpts instead of LLM-generated response.
    """
    
    # Check if we should use FAISS fallback
    use_faiss_fallback = not settings.LLM_ENDPOINT and not os.getenv('OPENAI_API_KEY')
    
    if use_faiss_fallback:
        # FAISS fallback: return top-k documents
        try:
            # Load resources (cached after first call)
            _load_rag_resources()
            
            if DOC_MAP_CACHE is None:
                return {
                    "reply": "RAG index not found. Please run the indexing pipeline first. See README_RAG_SETUP.md",
                    "citations": []
                }
            
            # Get query embedding (use fallback helper)
            query_emb = get_embedding_fallback(req.message)
            
            # Search using cached index
            if FAISS_INDEX_CACHE is not None:
                query_emb_32 = query_emb.astype('float32').reshape(1, -1)
                distances, indices = FAISS_INDEX_CACHE.search(query_emb_32, k=3)
                top_indices = indices[0]
                top_distances = distances[0]
            elif EMBEDDINGS_CACHE is not None:
                top_distances, top_indices = py_cosine_search(EMBEDDINGS_CACHE, query_emb, topk=3)
            else:
                return {
                    "reply": "RAG index not found. Please run the indexing pipeline first.",
                    "citations": []
                }
            
            # Build answer from top-k documents
            answer_parts = []
            citations = []
            debug_info = [] if debug else None
            
            for i, idx in enumerate(top_indices):
                doc_key = str(int(idx))
                if doc_key not in DOC_MAP_CACHE:
                    continue
                    
                doc = DOC_MAP_CACHE[doc_key]
                title = doc.get('title', 'Untitled')
                text = doc.get('text', '')
                source = doc.get('source', '')
                filename = doc.get('filename', '')
                category = doc.get('category', 'unknown')
                chunk_index = doc.get('chunk_index', '')
                
                # Add excerpt (first 200 chars)
                excerpt = text[:200] + '...' if len(text) > 200 else text
                answer_parts.append(f"**{title}**\n{excerpt}")
                
                citation = {
                    "title": title,
                    "filename": filename,
                    "source": source
                }
                
                # Add debug info if requested
                if debug:
                    citation.update({
                        "distance": float(top_distances[i]) if i < len(top_distances) else None,
                        "category": category,
                        "chunk_index": chunk_index
                    })
                    debug_info.append({
                        "rank": i + 1,
                        "distance": float(top_distances[i]) if i < len(top_distances) else None,
                        "category": category,
                        "chunk_index": chunk_index
                    })
                
                citations.append(citation)
            
            # Combine answer (limit to 6000 chars)
            answer = "\n\n---\n\n".join(answer_parts)
            if len(answer) > 6000:
                answer = answer[:6000] + "..."
            
            if not answer:
                answer = "No relevant documents found. Please try rephrasing your question."
            
            response = {
                "reply": answer,
                "citations": citations
            }
            
            if debug and debug_info:
                response["debug"] = {
                    "query_embedding_shape": list(query_emb.shape),
                    "top_k_results": debug_info
                }
            
            return response
            
        except Exception as e:
            import traceback
            return {
                "reply": f"Error retrieving documents: {str(e)}",
                "citations": []
            }
    
    # Original LLM flow (existing code) - only if not using FAISS fallback
    from app.utils.embeddings import get_embedding
    from app.services.rag_service import vector_search
    
    emb = await get_embedding(req.message)
    docs = vector_search(emb, top_k=5)
    
    context = "\n\n".join(
        [f"{d['title']}\n{d['content'][:1500]}" for d in docs]  # truncate for prompt
    )
    
    if settings.LLM_ENDPOINT:
        # Prompt payload the external LLM expects (adjust fields as needed).
        payload = {
            "system": "You are AfroKen LLM. Answer in simple Swahili unless requested otherwise. Ground answers in provided documents and add citations.",
            "documents": context,
            "user_message": req.message,
            "language": req.language,
        }
        # Use an async HTTP client so the FastAPI endpoint stays non-blocking.
        async with httpx.AsyncClient(timeout=20) as client:
            res = await client.post(settings.LLM_ENDPOINT, json=payload)
            # Raise an exception on non-success status codes.
            res.raise_for_status()
            # Parse the JSON response from the LLM service.
            data = res.json()
            # Safely retrieve the "answer" field, falling back to a friendly Swahili message.
            answer = data.get(
                "answer", "Samahani, sijaelewa. Tafadhali fafanua."
            )
    else:
        # Fallback behaviour when no LLM endpoint is configured:
        # simply echo the message and mention how many sources were found.
        answer = f"(demo) Nimepata {len(docs)} vyanzo. Jibu: {req.message}"

    # Build a list of citations from each document's source URL or title.
    citations = [d.get("source_url") or d.get("title") for d in docs]
    # Return a ChatResponse-compatible dict.
    return {"reply": answer, "citations": citations}
