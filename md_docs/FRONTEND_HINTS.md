# Frontend Integration Hints

## Chat API Endpoint Location

The frontend chat functionality is likely located in:
- `afroken_llm_frontend/src/lib/api.ts` - This file contains the API client functions
- `afroken_llm_frontend/src/hooks/useChat.ts` - Custom hook for chat functionality
- `afroken_llm_frontend/src/components/Chat/ChatWindow.tsx` - Chat UI component

## Endpoint Configuration

The backend chat endpoint is:
- **Path:** `/api/v1/chat/messages`
- **Method:** POST
- **Request Body:** `{ "message": "...", "language": "en" }`
- **Response:** `{ "reply": "...", "citations": [...] }`

## Verify Frontend Endpoint

1. Search for `fetch(` or `axios` in `afroken_llm_frontend/src/lib/api.ts`
2. Check the `postChat` function to confirm it calls the correct endpoint
3. Update the base URL if needed:
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
   ```

## CORS Configuration

Ensure the backend allows your frontend origin. In `afroken_llm_backend/app/main.py`, update CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",   # Alternative port
        "http://localhost:5174",   # Vite alternative
    ] if settings.ENV == "development" else ["https://your.production.domain"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Testing Frontend Connection

1. Start backend: `uvicorn app.main:app --reload --port 8000`
2. Start frontend: `cd afroken_llm_frontend && npm run dev`
3. Open browser console and check for CORS errors
4. Test chat functionality and verify API calls in Network tab

