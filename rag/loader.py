from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from pathlib import Path
from config import RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP
from utils.logger import logger

class DocumentLoader:
    """Загрузчик документов для RAG"""
    
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=RAG_CHUNK_SIZE,
            chunk_overlap=RAG_CHUNK_OVERLAP,
            length_function=len,
        )
    
    def load_document(self, file_path: str):
        """Загрузить и разбить документ на чанки"""
        try:
            file_path = Path(file_path)
            
            # Выбираем loader в зависимости от расширения
            if file_path.suffix.lower() == '.pdf':
                loader = PyPDFLoader(str(file_path))
            elif file_path.suffix.lower() in ['.txt', '.md']:
                loader = TextLoader(str(file_path), encoding='utf-8')
            else:
                raise ValueError(f"Неподдерживаемый формат файла: {file_path.suffix}")
            
            # Загружаем документ
            documents = loader.load()
            
            # Разбиваем на чанки
            chunks = self.text_splitter.split_documents(documents)
            
            logger.info(f"Загружен документ {file_path.name}: {len(chunks)} чанков")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Ошибка загрузки документа {file_path}: {e}")
            raise

# Глобальный экземпляр
document_loader = DocumentLoader()
