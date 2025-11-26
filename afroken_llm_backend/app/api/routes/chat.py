from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.utils.embeddings import get_embedding
from app.services.rag_service import vector_search
from app.config import settings

import httpx


router = APIRouter()


@router.post("/messages", response_model=ChatResponse)
async def post_message(req: ChatRequest):
    # 1. create embedding
    emb = await get_embedding(req.message)

    # 2. vector search
    docs = vector_search(emb, top_k=5)

    # 3. assemble context
    context = "\n\n".join(
        [f"{d['title']}\n{d['content'][:1500]}" for d in docs]  # truncate for prompt
    )

    # 4. send to LLM (RAG call)
    if settings.LLM_ENDPOINT:
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
            answer = data.get(
                "answer", "Samahani, sijaelewa. Tafadhali fafanua."
            )
    else:
        # fallback demo behaviour
        answer = f"(demo) Nimepata {len(docs)} vyanzo. Jibu: {req.message}"

    citations = [d.get("source_url") or d.get("title") for d in docs]
    return {"reply": answer, "citations": citations}



