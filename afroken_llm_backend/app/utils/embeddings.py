"""
Utility for generating text embeddings either via an external service or a
local deterministic fallback (for demos and offline use).
"""

import httpx

from app.config import settings


async def get_embedding(text: str) -> list[float]:
    """
    Obtain a numeric embedding vector for the given text.

    Behaviour:
    - If `settings.EMBEDDING_ENDPOINT` is not set, generate a pseudo-embedding
      deterministically from character codes (sufficient for hackathon demos).
    - Otherwise, POST the text to the configured embedding service and parse
      the returned JSON `{"embedding": [float, ...]}`.
    """

    if not settings.EMBEDDING_ENDPOINT:
        # Simple deterministic pseudo-embedding (hackathon/demo only).
        # Each character contributes a value derived from its Unicode code point.
        vec = [float((ord(c) % 100) / 100.0) for c in text[: settings.EMBEDDING_DIM]]
        # Pad or truncate to exactly EMBEDDING_DIM dimensions.
        vec = (vec + [0.0] * settings.EMBEDDING_DIM)[: settings.EMBEDDING_DIM]
        return vec

    # When an embedding endpoint is configured, call it over HTTP.
    async with httpx.AsyncClient(timeout=30) as client:
        # Send the text as JSON payload; adjust the key to match your service.
        resp = await client.post(settings.EMBEDDING_ENDPOINT, json={"input": text})
        # Raise an exception if we did not get a 2xx response code.
        resp.raise_for_status()
        # Parse the JSON body.
        data = resp.json()
        # Extract and return the "embedding" field (or None if missing).
        return data.get("embedding")
