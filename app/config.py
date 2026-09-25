import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.1:8b",
)
DATABASE_PATH = os.getenv("DATABASE_PATH", "ticketiq.db")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2",
)

DEFAULT_TOP_K = 3
MAX_TOP_K = 5

EPSILON = 0.10
REWARD_SCALE = 10.0
