from typing import Dict, List

class BotMessage:
    def __init__(self, message_id: int, text: str):
        self.message_id = message_id
        self.text = text  


class DialogManager:
    def __init__(self, max_history_length: int = 6):
        self.histories: Dict[int, List[Dict]] = {}  # {chat_id: [{"role": ..., "content": ...}]}
        self.last_bot_messages: Dict[int, BotMessage] = {}  # {chat_id: BotMessage}
        self.max_history_length = max_history_length  # Макс. длина истории (в сообщениях)

    def add_user_message(self, chat_id: int, text: str):
        """Добавляет сообщение пользователя в историю."""
        if chat_id not in self.histories:
            self.histories[chat_id] = []
        self.histories[chat_id].append({"role": "user", "content": text})

    def add_bot_message(self, chat_id: int, message_id: int, text: str):
        """Добавляет ответ бота в историю и сохраняет его message_id."""
        if chat_id not in self.histories:
            self.histories[chat_id] = []
        self.histories[chat_id].append({"role": "assistant", "content": text})
        
        self.last_bot_messages[chat_id] = BotMessage(message_id, text)

        self.histories[chat_id] = self.histories[chat_id][-self.max_history_length:]

    def get_history(self, chat_id: int) -> List[Dict]:
        """Возвращает историю диалога для chat_id."""
        return self.histories.get(chat_id, [])

    def get_last_bot_message(self, chat_id: int) -> Optional[BotMessage]:
        """Возвращает последнее сообщение бота (или None)."""
        return self.last_bot_messages.get(chat_id)

    def reset_history(self, chat_id: int):
        """Сбрасывает историю диалога."""
        self.histories[chat_id] = []
        self.last_bot_messages.pop(chat_id, None)