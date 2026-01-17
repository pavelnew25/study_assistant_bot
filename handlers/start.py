from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.session import user_sessions
from utils.logger import logger

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    logger.info(f"Пользователь {user_id} ({user_name}) запустил бота")
    
    welcome_text = f"""👋 Привет, {user_name}!

Я твой персональный Python-ассистент для обучения.

🔹 **Возможности:**
• 💬 Ответы на вопросы по Python
• 🖼 Анализ изображений и кода на скриншотах
• 🎤 Распознавание голосовых сообщений
• 📄 Работа с PDF документами
• 📚 RAG - поиск по твоим учебным материалам
• 🔊 Озвучивание ответов

🔹 **Команды:**
/mode - Переключить режим (text/voice/rag)
/reset - Очистить историю диалога
/stats - Показать статистику
/help - Помощь

🔹 **Режимы работы:**
• **text** - обычный диалог с ассистентом
• **voice** - диалог с озвучиванием ответов
• **rag** - поиск ответов в загруженных документах

📤 Отправь мне PDF или TXT файл, и я добавлю его в базу знаний!

Текущий режим: **{user_sessions.get_mode(user_id)}**"""
    
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    help_text = """📖 **Инструкция по использованию**

**Текстовые запросы:**
Просто отправь сообщение - я отвечу с учетом контекста диалога.

**Изображения:**
Отправь фото с подписью или без - я проанализирую изображение.

**Голосовые сообщения:**
Отправь голосовое - я распознаю речь и отвечу.

**Документы:**
Отправь PDF/TXT файл - я добавлю его в базу знаний для RAG.

**Режимы:**
• `/mode` - выбор режима кнопками

**Другие команды:**
• `/reset` - очистить историю
• `/stats` - статистика использования
• `/start` - показать приветствие"""
    
    await update.message.reply_text(help_text)

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /reset"""
    user_id = update.effective_user.id
    user_sessions.clear_history(user_id)
    logger.info(f"Пользователь {user_id} очистил историю")
    
    await update.message.reply_text("✅ История диалога очищена!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /stats"""
    user_id = update.effective_user.id
    stats = user_sessions.get_stats(user_id)
    mode = user_sessions.get_mode(user_id)
    
    from rag.index import vector_index
    kb_size = vector_index.get_collection_size()
    
    stats_text = f"""📊 **Статистика**

💬 Текстовых сообщений: {stats['messages']}
🎤 Голосовых сообщений: {stats['voice']}
🖼 Изображений: {stats['images']}
📄 Документов загружено: {stats['documents']}
📚 Документов в базе знаний: {kb_size}
🔧 Текущий режим: **{mode}**"""
    
    await update.message.reply_text(stats_text)

async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /mode - выбор режима с кнопками"""
    user_id = update.effective_user.id
    current_mode = user_sessions.get_mode(user_id)
    
    # Создаем кнопки
    keyboard = [
        [
            InlineKeyboardButton("📝 Text", callback_data="mode_text"),
            InlineKeyboardButton("🔊 Voice", callback_data="mode_voice"),
        ],
        [
            InlineKeyboardButton("🗂 RAG", callback_data="mode_rag"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Текущий режим: **{current_mode}**\n\nВыбери новый режим:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    logger.info(f"Пользователь {user_id} открыл меню выбора режима")

async def mode_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатия на кнопку режима"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    mode = query.data.replace("mode_", "")  # mode_text -> text
    
    # Устанавливаем режим
    user_sessions.set_mode(user_id, mode)
    
    mode_names = {
        "text": "📝 Текстовый",
        "voice": "🔊 Голосовой",
        "rag": "🗂 RAG"
    }
    
    await query.edit_message_text(
        f"✅ Режим изменен на: **{mode_names[mode]}**",
        parse_mode="Markdown"
    )
    logger.info(f"Пользователь {user_id} выбрал режим: {mode}")
