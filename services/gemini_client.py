import base64
import wave
import io
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, GEMINI_TEXT_MODEL, GEMINI_VISION_MODEL, GEMINI_AUDIO_MODEL
from utils.logger import logger

class GeminiClient:
    """Клиент для работы с Gemini API"""
    
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini клиент инициализирован")
    
    def generate_text(self, messages: list, system_prompt: str = None) -> str:
        """Генерация текстового ответа"""
        try:
            contents = []
            
            # Добавляем system prompt если есть
            if system_prompt:
                contents.append({
                    "role": "user",
                    "parts": [{"text": system_prompt}]
                })
                contents.append({
                    "role": "model",
                    "parts": [{"text": "Понял, буду следовать инструкциям."}]
                })
            
            # Добавляем историю
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            response = self.client.models.generate_content(
                model=GEMINI_TEXT_MODEL,
                contents=contents
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка генерации текста: {e}")
            return f"Ошибка: {str(e)}"
    
    def analyze_image(self, image_bytes: bytes, caption: str, history: list) -> str:
        """Анализ изображения"""
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            contents = []
            
            # Добавляем историю
            for msg in history[-5:]:  # Последние 5 сообщений
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Добавляем текущее изображение
            parts = [{"text": caption}] if caption else [{"text": "Проанализируй это изображение"}]
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_base64
                }
            })
            
            contents.append({
                "role": "user",
                "parts": parts
            })
            
            response = self.client.models.generate_content(
                model=GEMINI_VISION_MODEL,
                contents=contents
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка анализа изображения: {e}")
            return f"Ошибка: {str(e)}"
    
    def process_audio(self, audio_bytes: bytes, history: list) -> str:
        """Обработка голосового сообщения"""
        try:
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            contents = []
            
            # Добавляем историю
            for msg in history[-5:]:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })
            
            # Добавляем аудио
            contents.append({
                "role": "user",
                "parts": [{
                    "inline_data": {
                        "mime_type": "audio/ogg",
                        "data": audio_base64
                    }
                }]
            })
            
            response = self.client.models.generate_content(
                model=GEMINI_AUDIO_MODEL,
                contents=contents
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка обработки аудио: {e}")
            return f"Ошибка: {str(e)}"
    
    def analyze_document(self, file_path: str, query: str = None) -> str:
        """Анализ документа через File API"""
        try:
            # Загружаем файл в Gemini
            file_ref = self.client.files.upload(file=file_path)
            
            # Ждем обработки
            import time
            while file_ref.state.name == "PROCESSING":
                time.sleep(1)
                file_ref = self.client.files.get(name=file_ref.name)
            
            if file_ref.state.name == "FAILED":
                return "Ошибка обработки файла"
            
            # Анализируем
            prompt = query if query else "Проанализируй этот документ и дай краткое описание содержимого"
            
            response = self.client.models.generate_content(
                model=GEMINI_TEXT_MODEL,
                contents=[file_ref, prompt]
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Ошибка анализа документа: {e}")
            return f"Ошибка: {str(e)}"
    
    def generate_audio(self, text: str) -> bytes:
        """Генерация аудио через Gemini TTS"""
        try:
            # Ограничиваем длину текста для TTS (макс 500 символов)
            if len(text) > 500:
                text = text[:500] + "..."
            
            logger.info(f"Генерация аудио для текста: {text[:50]}...")
            
            response = self.client.models.generate_content(
                model="models/gemini-2.5-flash-preview-tts",
                contents=f"Прочитай этот текст естественно на русском языке: {text}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name="Fenrir"
                            )
                        )
                    )
                )
            )
            
            # Извлекаем аудио из ответа
            audio_data = None
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        audio_data = part.inline_data.data
                        break
            
            if audio_data:
                # Декодируем байты
                audio_bytes = base64.b64decode(audio_data) if isinstance(audio_data, str) else audio_data
                
                logger.info(f"Получено PCM данных: {len(audio_bytes)} bytes")
                
                # Создаем правильную структуру WAV файла
                wav_buffer = io.BytesIO()
                with wave.open(wav_buffer, 'wb') as wav_file:
                    wav_file.setnchannels(1)      # 1 канал (моно)
                    wav_file.setsampwidth(2)      # 2 байта (16 бит)
                    wav_file.setframerate(24000)  # Частота 24kHz
                    wav_file.writeframes(audio_bytes)
                
                wav_bytes = wav_buffer.getvalue()
                logger.info(f"WAV файл создан: {len(wav_bytes)} bytes")
                return wav_bytes
            
            logger.warning("Не найдено audio_data в ответе")
            return None
            
        except Exception as e:
            logger.error(f"Ошибка генерации аудио: {e}")
            import traceback
            traceback.print_exc()
            return None

# Глобальный экземпляр
gemini_client = GeminiClient()
