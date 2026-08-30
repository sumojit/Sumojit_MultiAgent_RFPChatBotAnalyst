import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "rfp_evaluator.db"))
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-a-plus")

if not COHERE_API_KEY:
    raise RuntimeError(
        "COHERE_API_KEY is not set. Create a .env file from .env.example "
        "and add your Cohere API key."
    )
