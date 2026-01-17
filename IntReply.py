# meta developer: @B_Mods
from .. import loader, utils
import asyncio
import random

class IntReply(loader.Module):
    """Интеллектуальный автоответчик через ИИ
    Отвечает только выбранному пользователю и берёт полный текст ответа"""
    
    strings = {"name": "IntReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # user_id -> True
        self.processing = {}  # user_id -> флаг ожидания ответа

    @loader.command()
    async def intstart(self, m):
        """Использование: .intstart @user — включить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")
        
        self.targets[user.id] = True
        self.processing[user.id] = False
        await m.edit(f"✅ Интеллектуальный автоответ включён для **{user.first_name}**")

    @loader.command()
    async def intstop(self, m):
        """Использование: .intstop @user — отключить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        
        self.targets.pop(user.id, None)
        self.processing.pop(user.id, None)
        await m.edit(f"🛑 Автоответчик выключен для **{user.first_name}**")

    async def watcher(self, m):
        if not m.sender_id or not m.chat or not m.text:
            return
        
        uid = m.sender_id
        
        # Отслеживаем только выбранных пользователей
        if uid not in self.targets:
            return
        
        # Игнорируем свои сообщения
        me = await self.client.get_me()
        if uid == me.id:
            return
        
        # Если автоответчик уже обрабатывает сообщение, не отвечаем
        if self.processing.get(uid):
            return
        
        self.processing[uid] = True

        # Логика рандомной задержки (чтобы не спамить)
        await asyncio.sleep(random.uniform(1, 3))

        # Берём полный текст сообщения
        user_message = m.text

        # Здесь вызываем ИИ для генерации ответа
        # Для примера: просто делаем реверс текста (заменить на реальный бот)
        # В реальном использовании нужно пересылать `user_message` боту и брать его ответ
        response_text = f"Ответ ИИ на сообщение:\n{user_message}"  # <-- заменить на вызов ИИ

        # Отправляем ответ реплаем
        try:
            await m.reply(response_text)
        except:
            pass
        
        # Сбрасываем флаг обработки
        self.processing[uid] = False