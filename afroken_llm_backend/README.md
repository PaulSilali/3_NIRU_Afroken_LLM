## AfroKen LLM – Backend (Monolith)

### Quick start (dev)

1. Create a `.env` file in `afroken_llm_backend` based on the environment variables described in `app/config.py` (DATABASE_URL, REDIS_URL, MINIO_*, JWT_*, LLM_/EMBEDDING_* and ENV).
2. From the `afroken_llm_backend` folder, run:
   - `docker compose up --build`
3. Run the DB init script once (from a container or environment that can reach Postgres):
   - `python scripts/init_db.py`
4. Open `http://localhost:8000/docs` to explore the API.

### Notes

- This is a hackathon-ready starter for AfroKen LLM – Citizen Service Copilot.
- Replace the demo OTP and LLM/embedding endpoints with real services before production.
- Ensure PostgreSQL has the `vector` extension installed to support pgvector features.


