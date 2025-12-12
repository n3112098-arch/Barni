# Разработчик: @B_Mods
from .. import loader, utils
import asyncio
import random

class AutoReplyMod(loader.Module):
    """Авто-ответ человеку по тригеру
    """
    strings = {"name": "AutoReplyMod"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # user_id -> enabled

    async def repcmd(self, m):
        """Запуск: @user"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("Кого репать?")

        self.targets[user.id] = True
        return await m.edit(f"Теперь отвечаю {user.first_name}")

    async def repstopcmd(self, m):
        """Остановка: @user"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("Кого отключить?")

        self.targets.pop(user.id, None)
        return await m.edit(f"Остановил ответы {user.first_name}")

    async def watcher(self, m):
        # Проверяем что это сообщение от юзера на которого включён реп
        if not m.sender_id:
            return

        if m.sender_id not in self.targets:
            return

        # Берём 1 случайное сообщение из истории (100 назад)
        try:
            msgs = await self.client.get_messages(
                m.chat_id, limit=100, from_user="me"
            )
            if not msgs:
                return

            last_texts = [x.text for x in msgs if x.text]
            if not last_texts:
                return

            reply_text = random.choice(last_texts)
        except:
            return

        # Генерируем корректный random_id (int32)
        random_id = random.randint(-2**31 + 1, 2**31 - 1)

        # Отвечаем именно реплаем
        try:
            await self.client.send_message(
                m.chat_id,
                reply_text,
                reply_to=m.id,
                random_id=random_id
            )
        except Exception as e:
            print("Send error:", e)