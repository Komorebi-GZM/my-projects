import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")


def api_url(path: str) -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{BACKEND_URL}{normalized_path}"
