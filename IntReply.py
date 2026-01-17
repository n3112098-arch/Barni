# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class IntReply(loader.Module):
    """Интеллектуальный автоответ через фиксированного бота"""
    strings = {"name": "IntReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.active_user = None
        self.bot_username = "jadvebot"  # фиксированный бот
        self.queue = asyncio.Queue()

    @loader.command()
    async def intstart(self, m):
        """.intstart @user — включить автоответ для пользователя"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя: `.intstart @username`")

        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")

        self.active_user = user
        await m.edit(f"✅ Интеллектуальный автоответ включён для **{user.first_name}**")

    @loader.command()
    async def intstop(self, m):
        """.intstop — отключить автоответ"""
        self.active_user = None
        while not self.queue.empty():
            self.queue.get_nowait()
        await m.edit("🛑 Автоответ отключён")

    async def watcher(self, m):
        if not self.active_user:
            return
        if not m.sender_id or not m.chat:
            return

        # Только выбранный пользователь
        if m.sender_id != self.active_user.id:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        # Пересылаем сообщение боту
        try:
            bot_msg = await self.client.send_message(self.bot_username, m.text or "")
            await self.queue.put((m.chat_id, m.id, bot_msg.id))
        except:
            return

        # Делаем задержку, чтобы бот успел ответить
        await asyncio.sleep(1.0)

        # Получаем ответ от бота
        try:
            bot_messages = await self.client.get_messages(self.bot_username, limit=5)
            for msg in bot_messages:
                if msg.id == bot_msg.id:
                    continue
                if msg.text:
                    # Реплай на сообщение выбранного пользователя
                    await self.client.send_message(m.chat_id, msg.text, reply_to=m.id)
                    break
        except:
            return