from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
PARSED_DIR = DATA_DIR / "parsed"
SAMPLE_DOCS_DIR = BASE_DIR / "sample_docs"

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}

MIN_PDF_TEXT_LENGTH = 30

# GLM OCR
OCR_TASK = "text"  # "text" veya "table"
GLM_MODEL_DIR = "models\GLM-OCR"

# Chunking
TARGET_CHUNK_SIZE = 1200
MAX_CHUNK_SIZE = 1600
CHUNK_OVERLAP = 200
MIN_CHUNK_SIZE = 150

# Retrieval / Embedding
EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
RETRIEVAL_TOP_K = 10

# LLM / Ollama
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL_NAME = "qwen2.5:7b"

for directory in [DATA_DIR, UPLOAD_DIR, PARSED_DIR]:
    directory.mkdir(parents=True, exist_ok=True)