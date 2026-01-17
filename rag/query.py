from rag.index import vector_index
from services.gemini_client import gemini_client
from config import RAG_TOP_K
from utils.logger import logger

def prepare_context(search_results) -> str:
    """Подготовить контекст из результатов поиска"""
    context_parts = []
    
    for i, (doc, score) in enumerate(search_results, 1):
        source = doc.metadata.get('source', 'Unknown')
        content = doc.page_content
        context_parts.append(f"[Источник {i}: {source}]\n{content}\n")
    
    return "\n".join(context_parts)

async def query_knowledge_base(query: str, history: list) -> str:
    """Запрос к базе знаний с RAG"""
    try:
        # Проверяем есть ли документы в базе
        collection_size = vector_index.get_collection_size()
        
        if collection_size == 0:
            return "❌ База знаний пуста. Загрузите документы командой /upload или отправив PDF/TXT файл."
        
        # Ищем релевантные документы
        search_results = vector_index.similarity_search(query, k=RAG_TOP_K)
        
        if not search_results:
            return "❌ Не найдено релевантных документов по вашему запросу."
        
        # Подготавливаем контекст
        context = prepare_context(search_results)
        
        # Формируем system prompt с контекстом
        system_prompt = f"""Ты - персональный ассистент для изучения Python.
У тебя есть доступ к базе знаний пользователя.

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ИНСТРУКЦИИ:
- Отвечай на основе предоставленного контекста
- Если информации недостаточно, скажи об этом
- Указывай источники при ответе
- Будь конкретным и структурируй ответ"""

        # Добавляем текущий запрос в историю
        messages = history + [{"role": "user", "content": query}]
        
        # Генерируем ответ
        response = gemini_client.generate_text(messages, system_prompt=system_prompt)
        
        logger.info(f"RAG запрос обработан, найдено {len(search_results)} документов")
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка RAG запроса: {e}")
        return f"❌ Ошибка при обработке запроса: {str(e)}"

async def add_document_to_knowledge_base(file_path: str) -> dict:
    """Добавить документ в базу знаний"""
    try:
        from rag.loader import document_loader
        
        # Загружаем и разбиваем документ
        chunks = document_loader.load_document(file_path)
        
        # Добавляем в векторное хранилище
        vector_index.add_documents(chunks)
        
        logger.info(f"Документ {file_path} добавлен в базу знаний")
        
        return {
            'success': True,
            'file': file_path,
            'chunks': len(chunks)
        }
        
    except Exception as e:
        logger.error(f"Ошибка добавления документа: {e}")
        return {
            'success': False,
            'error': str(e)
        }
