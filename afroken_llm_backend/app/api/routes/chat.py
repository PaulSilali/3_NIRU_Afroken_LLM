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
    
    # Calculate backend root directory (go up from app/api/routes/chat.py to backend root)
    # chat.py is at: backend/app/api/routes/chat.py
    # So we need: backend/app/api/routes -> backend/app/api -> backend/app -> backend
    backend_dir = Path(__file__).parent.parent.parent.parent
    doc_map_file = backend_dir / 'doc_map.json'
    index_file = backend_dir / 'faiss_index.idx'
    embeddings_file = backend_dir / 'faiss_index.npy'
    
    # Debug: print paths (remove in production)
    import sys
    if sys.stdout.isatty():  # Only print if running in terminal
        print(f"Loading RAG resources from: {backend_dir}")
        print(f"  doc_map.json: {doc_map_file.exists()}")
        print(f"  faiss_index.idx: {index_file.exists()}")
        print(f"  faiss_index.npy: {embeddings_file.exists()}")
    
    # Load doc_map
    if doc_map_file.exists():
        with open(doc_map_file, 'r', encoding='utf-8') as f:
            DOC_MAP_CACHE = json.load(f)
        print(f"✓ Loaded doc_map with {len(DOC_MAP_CACHE)} documents")
    else:
        print(f"⚠ doc_map.json not found at: {doc_map_file}")
    
    # Load FAISS index or embeddings
    if FAISS_AVAILABLE and index_file.exists():
        FAISS_INDEX_CACHE = faiss.read_index(str(index_file))
        print(f"✓ Loaded FAISS index")
    elif embeddings_file.exists():
        EMBEDDINGS_CACHE = np.load(str(embeddings_file))
        print(f"✓ Loaded embeddings numpy array")
    else:
        print(f"⚠ No FAISS index or embeddings file found")

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
                
                # Clean markdown formatting from text
                import re
                cleaned_text = text
                # Remove markdown headers (# ## ###) - match at start of line
                cleaned_text = re.sub(r'^#{1,6}\s+', '', cleaned_text, flags=re.MULTILINE)
                # Remove markdown bold (**text**)
                cleaned_text = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned_text)
                # Remove markdown italic (*text*)
                cleaned_text = re.sub(r'\*(.+?)\*', r'\1', cleaned_text)
                # Remove markdown bullet lists (- item or * item)
                cleaned_text = re.sub(r'^\s*[-*]\s+', '', cleaned_text, flags=re.MULTILINE)
                # Remove numbered lists (1. 2. 3.)
                cleaned_text = re.sub(r'^\s*\d+\.\s+', '', cleaned_text, flags=re.MULTILINE)
                # Remove indentation from list items (   - item)
                cleaned_text = re.sub(r'^\s{2,}', '', cleaned_text, flags=re.MULTILINE)
                # Remove extra blank lines (more than 2 consecutive)
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
                # Strip leading/trailing whitespace
                cleaned_text = cleaned_text.strip()
                
                # Add excerpt (first 300 chars for better context)
                excerpt = cleaned_text[:300].strip()
                if len(cleaned_text) > 300:
                    # Try to cut at sentence boundary
                    last_period = excerpt.rfind('.')
                    if last_period > 150:
                        excerpt = excerpt[:last_period + 1]
                    else:
                        excerpt = excerpt + '...'
                
                # Only add if excerpt has meaningful content (more than just whitespace)
                if excerpt.strip() and len(excerpt.strip()) > 10:
                    answer_parts.append(f"{title}\n\n{excerpt}")
                
                # Format citation as string (schema expects List[str])
                # Use source URL if available, otherwise use title, fallback to filename
                if source and source.strip():
                    citation_str = source.strip()
                elif title and title.strip():
                    citation_str = title.strip()
                else:
                    citation_str = filename if filename else "Untitled"
                
                # Only add unique citations
                if citation_str not in citations:
                    citations.append(citation_str)
                
                # Add debug info if requested
                if debug:
                    debug_info.append({
                        "rank": i + 1,
                        "title": title,
                        "filename": filename,
                        "source": source,
                        "distance": float(top_distances[i]) if i < len(top_distances) else None,
                        "category": category,
                        "chunk_index": chunk_index
                    })
            
            # Combine answer (limit to 6000 chars)
            # Only include parts with meaningful content
            meaningful_parts = [p for p in answer_parts if p.strip() and len(p.strip()) > 20]
            
            if meaningful_parts:
                answer = "\n\n---\n\n".join(meaningful_parts)
                if len(answer) > 6000:
                    answer = answer[:6000] + "..."
            else:
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
    # Try to use database-based RAG, but fall back to FAISS if database unavailable
    try:
        from app.utils.embeddings import get_embedding
        from app.services.rag_service import vector_search
        
        emb = await get_embedding(req.message)
        docs = vector_search(emb, top_k=5)
    except Exception as db_error:
        # Database unavailable - use FAISS fallback instead
        _load_rag_resources()
        
        if DOC_MAP_CACHE is None:
            return {
                "reply": "RAG index not found. Please run the indexing pipeline first.",
                "citations": []
            }
        
        # Get query embedding
        query_emb = get_embedding_fallback(req.message)
        
        # Search using cached index
        if FAISS_INDEX_CACHE is not None:
            query_emb_32 = query_emb.astype('float32').reshape(1, -1)
            distances, indices = FAISS_INDEX_CACHE.search(query_emb_32, k=3)
            top_indices = indices[0]
        elif EMBEDDINGS_CACHE is not None:
            _, top_indices = py_cosine_search(EMBEDDINGS_CACHE, query_emb, topk=3)
        else:
            return {
                "reply": "RAG index not found. Please run the indexing pipeline first.",
                "citations": []
            }
        
        # Build answer from top-k documents
        answer_parts = []
        citations = []
        
        for i, idx in enumerate(top_indices):
            doc_key = str(int(idx))
            if doc_key not in DOC_MAP_CACHE:
                continue
                
            doc = DOC_MAP_CACHE[doc_key]
            title = doc.get('title', 'Untitled')
            text = doc.get('text', '')
            source = doc.get('source', '')
            filename = doc.get('filename', '')
            
            # Clean markdown from text (same as main FAISS fallback)
            import re
            cleaned_text = text
            cleaned_text = re.sub(r'^#{1,6}\s+', '', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\*\*(.+?)\*\*', r'\1', cleaned_text)
            cleaned_text = re.sub(r'^\s*[-*]\s+', '', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'^\s*\d+\.\s+', '', cleaned_text, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text).strip()
            
            excerpt = cleaned_text[:300].strip()
            if len(cleaned_text) > 300:
                last_period = excerpt.rfind('.')
                if last_period > 150:
                    excerpt = excerpt[:last_period + 1]
                else:
                    excerpt = excerpt + '...'
            
            if excerpt.strip() and len(excerpt.strip()) > 10:
                answer_parts.append(f"{title}\n\n{excerpt}")
            
            # Format citation as string (schema expects List[str])
            if source and source.strip():
                citation_str = source.strip()
            elif title and title.strip():
                citation_str = title.strip()
            else:
                citation_str = filename if filename else "Untitled"
            
            # Only add unique citations
            if citation_str not in citations:
                citations.append(citation_str)
        
        answer = "\n\n---\n\n".join(answer_parts)
        if len(answer) > 6000:
            answer = answer[:6000] + "..."
        
        if not answer:
            answer = "No relevant documents found. Please try rephrasing your question."
        
        return {
            "reply": answer,
            "citations": citations
        }
    
    # Prepare context from retrieved documents
    context_documents = [f"{d['title']}\n{d['content'][:1500]}" for d in docs]
    context = "\n\n".join(context_documents)
    
    # Try to use fine-tuned LLM service
    try:
        from app.services.llm_service import generate_response
        
        # Build messages for LLM
        messages = [{"role": "user", "content": req.message}]
        
        # System prompt based on language
        system_prompt = (
            "You are AfroKen LLM, a helpful assistant for Kenyan government services. "
            "Answer in simple Swahili unless requested otherwise. "
            "Ground your answers in the provided documents and always cite sources. "
            "If you don't know the answer, say so clearly."
        )
        
        # Generate response using fine-tuned LLM
        llm_result = await generate_response(
            messages=messages,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=1000,
            context_documents=context_documents
        )
        
        answer = llm_result["text"]
        tokens_used = llm_result.get("tokens_used", 0)
        
    except (ImportError, ValueError, Exception) as llm_error:
        # Fallback to generic LLM endpoint or document excerpts
        if settings.LLM_ENDPOINT:
            # Use generic LLM endpoint
            payload = {
                "system": "You are AfroKen LLM. Answer in simple Swahili unless requested otherwise. Ground answers in provided documents and add citations.",
                "documents": context,
                "user_message": req.message,
                "language": req.language,
            }
            async with httpx.AsyncClient(timeout=20) as client:
                res = await client.post(settings.LLM_ENDPOINT, json=payload)
                res.raise_for_status()
                data = res.json()
                answer = data.get("answer", "Samahani, sijaelewa. Tafadhali fafanua.")
        else:
            # Final fallback: return document excerpts
            answer = context[:6000] if context else "No relevant documents found. Please try rephrasing your question."
    
    # Build citations from documents
    citations = []
    for d in docs:
        citation = d.get("source_url") or d.get("title", "Untitled")
        if citation and citation not in citations:
            citations.append(citation)
    
    # Return ChatResponse
    return {"reply": answer, "citations": citations}
