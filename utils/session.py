from collections import defaultdict
from typing import Dict, List, Any
from config import MAX_HISTORY_LENGTH

class UserSession:
    """Управление сессиями пользователей"""
    
    def __init__(self):
        self.history: Dict[int, List[Dict[str, str]]] = defaultdict(list)
        self.mode: Dict[int, str] = defaultdict(lambda: "text")  # text, rag, voice
        self.stats: Dict[int, Dict[str, int]] = defaultdict(lambda: {
            'messages': 0,
            'voice': 0,
            'images': 0,
            'documents': 0
        })
    
    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Получить историю пользователя"""
        return self.history[user_id]
    
    def add_message(self, user_id: int, role: str, content: str):
        """Добавить сообщение в историю"""
        self.history[user_id].append({"role": role, "content": content})
        
        # Обрезаем историю если слишком длинная
        if len(self.history[user_id]) > MAX_HISTORY_LENGTH:
            self.history[user_id] = self.history[user_id][-MAX_HISTORY_LENGTH:]
        
        # Обновляем статистику
        if role == "user":
            self.stats[user_id]['messages'] += 1
    
    def clear_history(self, user_id: int):
        """Очистить историю пользователя"""
        self.history[user_id].clear()
    
    def get_mode(self, user_id: int) -> str:
        """Получить текущий режим"""
        return self.mode[user_id]
    
    def set_mode(self, user_id: int, mode: str):
        """Установить режим работы"""
        self.mode[user_id] = mode
    
    def update_stats(self, user_id: int, stat_type: str):
        """Обновить статистику"""
        if stat_type in self.stats[user_id]:
            self.stats[user_id][stat_type] += 1
    
    def get_stats(self, user_id: int) -> Dict[str, int]:
        """Получить статистику пользователя"""
        return self.stats[user_id]

# Глобальный экземпляр
user_sessions = UserSession()
