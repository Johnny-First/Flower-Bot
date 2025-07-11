from openai import OpenAI
import os
import dotenv
from typing import Dict, List

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
        self.chat_histories: Dict[int, List[Dict]] = {}  

    def ask_gpt(self, message: str) -> str: #chat_id: int, message: str) -> str:
        """Запрос к GPT с учётом истории диалога"""
        # Инициализируем историю для нового чата
        # if chat_id not in self.chat_histories:
            # self.chat_histories[chat_id] = [
                # {"role": "system", "content": self.system_prompt}
            # ]

        # Добавляем сообщение пользователя в историю
        # self.chat_histories[chat_id].append({"role": "user", "content": message})

        try:
            # Отправляем ВСЮ историю диалога
            response = self.client.chat.completions.create(
                model="gpt-4.1",
                # messages=self.chat_histories[chat_id],
                messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            bot_reply = response.choices[0].message.content

            # Добавляем ответ бота в историю
            # self.chat_histories[chat_id].append(
                # {"role": "assistant", "content": bot_reply}
            # )

            # Ограничиваем длину истории (последние 6 сообщений)
            # self.chat_histories[chat_id] = self.chat_histories[chat_id][-6:]

            return bot_reply

        except Exception as e:
            return f"❌ Ошибка: {str(e)}"

    def reset_history(self, chat_id: int):
  
        self.chat_histories[chat_id] = [
            {"role": "system", "content": self.system_prompt}
        ]