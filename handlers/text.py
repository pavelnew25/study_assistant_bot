import io
from telegram import Update
from telegram.ext import ContextTypes
from utils.session import user_sessions
from utils.logger import logger
from services.gemini_client import gemini_client
from rag.query import query_knowledge_base

async def split_and_send_message(update: Update, text: str, max_length: int = 4000):
    """Разбивает длинное сообщение на части и отправляет"""
    if len(text) <= max_length:
        await update.message.reply_text(text)
        return
    
    # Разбиваем по параграфам
    parts = []
    current_part = ""
    
    for paragraph in text.split('\n\n'):
        if len(current_part) + len(paragraph) + 2 <= max_length:
            current_part += paragraph + "\n\n"
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = paragraph + "\n\n"
    
    if current_part:
        parts.append(current_part.strip())
    
    # Отправляем части
    for i, part in enumerate(parts, 1):
        if len(parts) > 1:
            await update.message.reply_text(f"📄 Часть {i}/{len(parts)}:\n\n{part}")
        else:
            await update.message.reply_text(part)

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"Текст от {user_id}: {user_message[:50]}...")
    
    # Получаем режим работы
    mode = user_sessions.get_mode(user_id)
    
    # Добавляем сообщение в историю
    user_sessions.add_message(user_id, "user", user_message)
    history = user_sessions.get_history(user_id)
    
    # Отправляем статус "печатает..."
    await update.message.chat.send_action("typing")
    
    try:
        # Выбираем способ обработки в зависимости от режима
        if mode == "rag":
            # RAG режим - поиск в базе знаний
            response = await query_knowledge_base(user_message, history[:-1])
        else:
            # Обычный текстовый режим
            system_prompt = """Ты - опытный Python-наставник и код-ревьюер с 10+ летним опытом.

🎯 ТВОЯ РОЛЬ:
Помогай изучать Python через практику, понятные объяснения и best practices.

📋 ПРАВИЛА ОТВЕТОВ:

1. **Структура:**
   - Сначала краткий ответ (1-2 предложения)
   - Затем детальное объяснение с примерами
   - В конце - совет или следующий шаг

2. **Объяснения:**
   - Используй простой язык без сложных терминов
   - Объясняй "почему", а не только "как"
   - Приводи реальные примеры использования
   - Указывай на типичные ошибки

3. **Код:**
   - Давай рабочие примеры кода
   - Комментируй ключевые моменты
   - Показывай несколько вариантов решения (если уместно)
   - Указывай на производительность и читаемость

4. **Стиль:**
   - Будь дружелюбным и мотивирующим
   - Используй эмодзи для структуры: 📌 ✅ ❌ 💡 ⚠️
   - Избегай излишней сложности
   - Длина ответа: 3-7 абзацев (если не попросили кратко)

5. **Ревью кода:**
   - Сначала похвали что хорошо
   - Укажи на ошибки и проблемы
   - Предложи улучшенную версию
   - Объясни почему так лучше

❌ НЕ ДЕЛАЙ:
- Не давай слишком сложные решения новичкам
- Не используй устаревший синтаксис (Python 2)
- Не пиши код без объяснений
- Не перегружай ответ теорией

✅ ВСЕГДА:
- Адаптируй уровень сложности под собеседника
- Предлагай дальнейшие шаги для изучения
- Ссылайся на официальную документацию когда нужно
- Показывай примеры из реальной разработки"""

            
            response = gemini_client.generate_text(history, system_prompt=system_prompt)
        
        # Добавляем ответ в историю
        user_sessions.add_message(user_id, "assistant", response)
        
        # Отправляем ответ (текст или голос в зависимости от режима)
        if mode == "voice":
            # Отправляем текстовую версию (с разбивкой если длинная)
            await split_and_send_message(update, response)
            
            # Генерируем и отправляем аудио
            try:
                await update.message.chat.send_action("record_voice")
                audio_data = gemini_client.generate_audio(response)
                
                if audio_data and len(audio_data) > 1000:
                    logger.info(f"Отправка аудио: {len(audio_data)} байт")
                    await update.message.reply_voice(voice=audio_data)
                else:
                    logger.warning(f"Аудио слишком маленькое: {len(audio_data) if audio_data else 0} байт")
                    await update.message.reply_text("⚠️ Не удалось озвучить (файл поврежден)")
            except Exception as e:
                logger.error(f"Ошибка отправки аудио: {e}")
                import traceback
                traceback.print_exc()
                await update.message.reply_text(f"⚠️ Ошибка озвучки: {str(e)}")
        else:
            # Обычный текстовый режим - разбиваем если нужно
            await split_and_send_message(update, response)
        
        logger.info(f"Ответ отправлен пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка обработки текста: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка: {str(e)}")
