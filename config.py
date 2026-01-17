import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_TEXT_MODEL = "gemini-2.0-flash-exp"
GEMINI_VISION_MODEL = "gemini-2.0-flash-exp"
GEMINI_AUDIO_MODEL = "gemini-2.0-flash-exp"

# Пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# RAG настройки
RAG_CHUNK_SIZE = 1000
RAG_CHUNK_OVERLAP = 200
RAG_TOP_K = 3
MAX_HISTORY_LENGTH = 20

# Создаем папки если их нет
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
