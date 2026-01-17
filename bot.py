from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TELEGRAM_BOT_TOKEN
from utils.logger import logger

# Импортируем хендлеры
from handlers.start import start_command, help_command, reset_command, stats_command, mode_command, mode_callback
from handlers.text import handle_text_message
from handlers.voice import handle_voice
from handlers.image import handle_photo
from handlers.document import handle_document

def setup_handlers(app: Application):
    """Регистрация всех обработчиков"""
    # Команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("mode", mode_command))
    
    # Callback для кнопок режима
    app.add_handler(CallbackQueryHandler(mode_callback, pattern="^mode_"))
    
    # Голосовые сообщения
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    # Изображения
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Документы
    app.add_handler(MessageHandler(filters.Document.PDF | filters.Document.TXT, handle_document))
    
    # Текстовые сообщения (должны быть последними)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    logger.info("Все обработчики зарегистрированы")

def create_bot() -> Application:
    """Создание и настройка бота"""
    logger.info("Инициализация бота...")
    
    # Создаем приложение
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Регистрируем обработчики
    setup_handlers(app)
    
    logger.info("Бот готов к работе!")
    return app

def start_bot():
    """Запуск бота"""
    app = create_bot()
    logger.info("Запуск polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    start_bot()
