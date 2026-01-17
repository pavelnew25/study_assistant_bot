from telegram import Update
from telegram.ext import ContextTypes
from utils.session import user_sessions
from utils.logger import logger
from services.gemini_client import gemini_client
import io

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка изображений"""
    user_id = update.effective_user.id
    caption = update.message.caption or "Проанализируй это изображение"
    
    logger.info(f"Изображение от {user_id}: {caption[:50]}...")
    
    # Обновляем статистику
    user_sessions.update_stats(user_id, 'images')
    
    # Отправляем статус
    await update.message.chat.send_action("typing")
    
    try:
        # Получаем самое большое фото
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        
        # Скачиваем изображение в память
        photo_bytes_io = io.BytesIO()
        await photo_file.download_to_memory(photo_bytes_io)
        photo_bytes = photo_bytes_io.getvalue()
        
        # Получаем историю
        history = user_sessions.get_history(user_id)
        
        # Анализируем изображение
        response = gemini_client.analyze_image(photo_bytes, caption, history)
        
        # Добавляем в историю
        user_sessions.add_message(user_id, "user", f"[Изображение]: {caption}")
        user_sessions.add_message(user_id, "assistant", response)
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
        logger.info(f"Анализ изображения завершен для {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки изображения: {e}")
        await update.message.reply_text(f"❌ Ошибка при анализе изображения: {str(e)}")
