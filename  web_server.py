# web_server.py
from fastapi import FastAPI
import asyncio
from main import main  # import your CLI orchestrator if needed

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Optional: Endpoint to manually trigger your main loop (for debug only)
@app.get("/")
async def run_main():
    # Optionally run the main Finara loop (not for Cloud Run use)
    asyncio.create_task(main())  # non-blocking fire-and-forget
    return {"message": "Finara main loop triggered"}