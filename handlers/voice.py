from telegram import Update
from telegram.ext import ContextTypes
from utils.session import user_sessions
from utils.logger import logger
from services.gemini_client import gemini_client
import io

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка голосовых сообщений"""
    user_id = update.effective_user.id
    
    logger.info(f"Голосовое сообщение от {user_id}")
    
    # Обновляем статистику
    user_sessions.update_stats(user_id, 'voice')
    
    # Отправляем статус
    await update.message.chat.send_action("typing")
    
    try:
        # Получаем голосовое сообщение
        voice = update.message.voice
        voice_file = await context.bot.get_file(voice.file_id)
        
        # Скачиваем в память
        voice_bytes_io = io.BytesIO()
        await voice_file.download_to_memory(voice_bytes_io)
        voice_bytes = voice_bytes_io.getvalue()
        
        # Получаем историю
        history = user_sessions.get_history(user_id)
        
        # Обрабатываем аудио (Gemini распознает и отвечает)
        response = gemini_client.process_audio(voice_bytes, history)
        
        # Добавляем в историю
        user_sessions.add_message(user_id, "user", "[Голосовое сообщение]")
        user_sessions.add_message(user_id, "assistant", response)
        
        # Отправляем ответ
        await update.message.reply_text(response)
        
        logger.info(f"Голосовое обработано для {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки голоса: {e}")
        await update.message.reply_text(f"❌ Ошибка при обработке голоса: {str(e)}")
