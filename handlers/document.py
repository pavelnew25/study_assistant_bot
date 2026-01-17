from telegram import Update
from telegram.ext import ContextTypes
from utils.session import user_sessions
from utils.logger import logger
from rag.query import add_document_to_knowledge_base
from pathlib import Path
import tempfile

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка документов (PDF, TXT)"""
    user_id = update.effective_user.id
    document = update.message.document
    
    logger.info(f"Документ от {user_id}: {document.file_name}")
    
    # Проверяем формат файла
    file_ext = Path(document.file_name).suffix.lower()
    
    if file_ext not in ['.pdf', '.txt', '.md']:
        await update.message.reply_text(
            "❌ Поддерживаются только форматы: PDF, TXT, MD"
        )
        return
    
    # Проверяем размер (макс 20MB)
    if document.file_size > 20 * 1024 * 1024:
        await update.message.reply_text(
            "❌ Размер файла превышает 20 МБ"
        )
        return
    
    # Обновляем статистику
    user_sessions.update_stats(user_id, 'documents')
    
    # Отправляем статус
    await update.message.reply_text("⏳ Загружаю документ в базу знаний...")
    
    try:
        # Скачиваем файл во временную папку
        doc_file = await context.bot.get_file(document.file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            temp_path = tmp_file.name
            await doc_file.download_to_drive(temp_path)
        
        # Добавляем в базу знаний
        result = await add_document_to_knowledge_base(temp_path)
        
        # Удаляем временный файл
        Path(temp_path).unlink()
        
        if result['success']:
            await update.message.reply_text(
                f"✅ Документ успешно добавлен!\n\n"
                f"📄 Файл: {document.file_name}\n"
                f"📊 Фрагментов: {result['chunks']}\n\n"
                f"Переключитесь в режим RAG командой `/mode rag` для поиска по документам."
            )
            logger.info(f"Документ {document.file_name} добавлен пользователем {user_id}")
        else:
            await update.message.reply_text(
                f"❌ Ошибка при добавлении документа:\n{result['error']}"
            )
        
    except Exception as e:
        logger.error(f"Ошибка обработки документа: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка: {str(e)}")
