import httpx

from app.config import settings


async def get_embedding(text: str) -> list[float]:
    """
    Call EMBEDDING_ENDPOINT to get an embedding vector.
    Expected response JSON: {"embedding": [float, ...]}.

    Falls back to a deterministic pseudo-embedding for demo use.
    """
    if not settings.EMBEDDING_ENDPOINT:
        # Simple deterministic pseudo-embedding (hackathon/demo only)
        vec = [float((ord(c) % 100) / 100.0) for c in text[: settings.EMBEDDING_DIM]]
        vec = (vec + [0.0] * settings.EMBEDDING_DIM)[: settings.EMBEDDING_DIM]
        return vec

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(settings.EMBEDDING_ENDPOINT, json={"input": text})
        resp.raise_for_status()
        data = resp.json()
        return data.get("embedding")



