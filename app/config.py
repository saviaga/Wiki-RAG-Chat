## Author: Claudia Flores-Saviaga
## GitHub: @saviaga

from pathlib import Path
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseModel):
    # Base paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    DATA_DIR: Path = BASE_DIR / "data"
    
    # Model settings
    MODEL_PATH: str = str(MODEL_DIR / "llama-2-7b-chat.ggmlv3.q4_0.bin")
    MODEL_N_CTX: int = 2048  # Context window size
    MODEL_N_BATCH: int = 8   # Batch size for processing
    MODEL_TEMPERATURE: float = 0.7
    MODEL_MAX_TOKENS: int = 512
    
    # Vector store settings
    VECTOR_STORE_PATH: str = str(DATA_DIR / "faiss_index")
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    
    # Embedding settings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Wikipedia API settings
    MAX_ARTICLES: int = 5
    MAX_ARTICLE_LENGTH: int = 20000
    WIKIPEDIA_USER_AGENT: str = os.getenv("WIKIPEDIA_USER_AGENT", "RAGApp/1.0")
    WIKIPEDIA_ACCESS_TOKEN: str = os.getenv("WIKIPEDIA_ACCESS_TOKEN")

# Create instance
settings = Settings()

# Ensure directories exist
settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True) 