from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import GEMINI_API_KEY, CHROMA_DB_DIR
from utils.logger import logger

class VectorIndex:
    """Векторное хранилище для RAG"""
    
    def __init__(self):
        try:
            # Инициализируем embeddings через Gemini
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=GEMINI_API_KEY
            )
            
            # Инициализируем ChromaDB
            self.vectorstore = Chroma(
                persist_directory=str(CHROMA_DB_DIR),
                embedding_function=self.embeddings
            )
            
            logger.info("Векторное хранилище инициализировано")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации векторного хранилища: {e}")
            raise
    
    def add_documents(self, documents):
        """Добавить документы в хранилище"""
        try:
            self.vectorstore.add_documents(documents)
            logger.info(f"Добавлено {len(documents)} документов в векторное хранилище")
        except Exception as e:
            logger.error(f"Ошибка добавления документов: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = 3):
        """Поиск похожих документов"""
        try:
            results = self.vectorstore.similarity_search_with_score(query, k=k)
            logger.debug(f"Найдено {len(results)} релевантных документов")
            return results
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []
    
    def get_collection_size(self) -> int:
        """Получить количество документов в хранилище"""
        try:
            return self.vectorstore._collection.count()
        except:
            return 0

# Глобальный экземпляр
vector_index = VectorIndex()
