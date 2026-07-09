import os

from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app

# Directory containing this file — ADK looks here for agent packages
# (it expects to find ecommerce_agent/ as a subfolder of this dir)
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Local SQLite for session persistence. Fine for a portfolio demo — swap
# for a hosted Postgres URI if you need durable sessions across restarts.
SESSION_SERVICE_URI = "sqlite:///./sessions.db"

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=["*"],
    web=True,  # serves the ADK dev UI at "/" in addition to the API routes
)

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)