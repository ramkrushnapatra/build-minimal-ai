import os
from pathlib import Path

from pydantic_settings import BaseSettings

_DEFAULT_DATA = Path(__file__).resolve().parent.parent.parent / "data"


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 800
    chunk_overlap: int = 150
    top_k: int = 4
    data_dir: Path = Path(os.getenv("DATA_DIR", str(_DEFAULT_DATA)))
    chroma_dir: Path = data_dir / "chroma"
    cors_origins: list = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
