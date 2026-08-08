import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("QDRANT_URL", "")
os.environ.setdefault("QDRANT_API_KEY", "")
os.environ.setdefault("LLAMA_CLOUD_API_KEY", "")
os.environ.setdefault("JWT_SECRET", "test-secret")
