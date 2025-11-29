"""
LLM service for fine-tuned Mistral/LLaMA-3 models.

This module provides a unified interface for calling fine-tuned language models.
Supports both local fine-tuned models and remote endpoints.
"""

import os
import httpx
from typing import Optional, Dict, Any, List
from app.config import settings


async def generate_response(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000,
    context_documents: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a response using fine-tuned LLM (Mistral/LLaMA-3).
    
    Args:
        messages: List of message dicts with "role" and "content" keys
        system_prompt: Optional system prompt for the model
        temperature: Sampling temperature (0.0-1.0)
        max_tokens: Maximum tokens to generate
        context_documents: Optional list of retrieved document excerpts for RAG
    
    Returns:
        dict with keys:
            - text: Generated response text
            - tokens_used: Number of tokens consumed
            - model: Model identifier used
    """
    
    # Check for fine-tuned model endpoint
    fine_tuned_endpoint = os.getenv("FINE_TUNED_LLM_ENDPOINT")
    
    if fine_tuned_endpoint:
        # Use fine-tuned model endpoint (Mistral/LLaMA-3)
        return await _call_fine_tuned_endpoint(
            fine_tuned_endpoint,
            messages,
            system_prompt,
            temperature,
            max_tokens,
            context_documents
        )
    elif settings.LLM_ENDPOINT:
        # Fallback to generic LLM endpoint
        return await _call_generic_endpoint(
            settings.LLM_ENDPOINT,
            messages,
            system_prompt,
            temperature,
            max_tokens,
            context_documents
        )
    else:
        raise ValueError(
            "No LLM endpoint configured. Set FINE_TUNED_LLM_ENDPOINT or LLM_ENDPOINT."
        )


async def _call_fine_tuned_endpoint(
    endpoint: str,
    messages: List[Dict[str, str]],
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    context_documents: Optional[List[str]]
) -> Dict[str, Any]:
    """Call fine-tuned Mistral/LLaMA-3 endpoint."""
    
    # Build context from retrieved documents
    context = ""
    if context_documents:
        context = "\n\n".join([
            f"Document {i+1}:\n{doc}" 
            for i, doc in enumerate(context_documents)
        ])
    
    # Prepare messages with system prompt
    formatted_messages = []
    if system_prompt:
        formatted_messages.append({
            "role": "system",
            "content": system_prompt
        })
    
    # Add context as system message if available
    if context:
        formatted_messages.append({
            "role": "system",
            "content": f"Context from retrieved documents:\n{context}"
        })
    
    # Add user messages
    formatted_messages.extend(messages)
    
    # Payload for fine-tuned model (adjust based on your model's API)
    payload = {
        "model": "mistral-7b-afroken" or "llama-3-8b-afroken",  # Your fine-tuned model name
        "messages": formatted_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        
        return {
            "text": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
            "tokens_used": data.get("usage", {}).get("total_tokens", 0),
            "model": data.get("model", "fine-tuned-model")
        }


async def _call_generic_endpoint(
    endpoint: str,
    messages: List[Dict[str, str]],
    system_prompt: Optional[str],
    temperature: float,
    max_tokens: int,
    context_documents: Optional[List[str]]
) -> Dict[str, Any]:
    """Call generic LLM endpoint (fallback)."""
    
    context = ""
    if context_documents:
        context = "\n\n".join(context_documents)
    
    payload = {
        "system": system_prompt or "You are AfroKen LLM, a helpful assistant for Kenyan government services.",
        "documents": context,
        "user_message": messages[-1]["content"] if messages else "",
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(endpoint, json=payload)
        response.raise_for_status()
        data = response.json()
        
        return {
            "text": data.get("answer", data.get("text", "")),
            "tokens_used": data.get("tokens_used", 0),
            "model": data.get("model", "generic-llm")
        }

