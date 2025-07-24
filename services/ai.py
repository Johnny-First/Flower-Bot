from openai import OpenAI
import os
import dotenv
from typing import List, Dict

dotenv.load_dotenv()

class AI_GPT:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url='https://bothub.chat/api/v2/openai/v1'
        )
        self.system_prompt = (
            "Ты консультант цветочного магазина 'Южные сады'."
            "Отвечай кратко и доброжелательно. "
            "Если вопрос не о цветах, скажи: 'Простите, с таким вопросом я не могу помочь!'"
        )

    def ask_gpt(self, messages: List[Dict]) -> str:
        """
        messages: список сообщений вида [{"role": ..., "content": ...}, ...]
        Возвращает ответ модели с учётом истории диалога.
        """
        # Добавляем system_prompt в начало истории
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages
        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                messages=full_messages,
                temperature=0.7,
                max_tokens=300
            )
            bot_reply = response.choices[0].message.content
            return bot_reply
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"