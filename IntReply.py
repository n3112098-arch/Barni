# meta developer: @B_Mods
from .. import loader, utils
import asyncio

class IntReply(loader.Module):
    """Интеллектуальный автоответчик через @jadvebot для выбранного юзера"""
    strings = {"name": "IntReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}      # username -> entity
        self.processing = {}   # username -> bool (чтобы не спамить)

    @loader.command()
    async def intstart(self, m):
        """Использование: .intstart @username — включить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")

        key = user.username or str(user.id)
        self.targets[key] = user
        self.processing[key] = False
        await m.edit(f"✅ Интеллектуальный автоответ включён для **{user.first_name}**")

    @loader.command()
    async def intstop(self, m):
        """Использование: .intstop @username — отключить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        key = user.username or str(user.id)
        self.targets.pop(key, None)
        self.processing.pop(key, None)
        await m.edit(f"🛑 Автоответчик выключен для **{user.first_name}**")

    async def watcher(self, m):
        # Проверяем сообщение
        if not m.sender or not m.chat or not m.text:
            return

        # Определяем ключ пользователя
        uid_key = m.sender.username or str(m.sender_id)

        # Сообщение не от выбранного пользователя
        if uid_key not in self.targets:
            return

        # Игнорируем свои сообщения
        me = await self.client.get_me()
        if m.sender_id == me.id:
            return

        # Если уже обрабатывается — пропускаем
        if self.processing.get(uid_key):
            return

        self.processing[uid_key] = True

        # Делаем небольшую задержку, чтобы ответ выглядел естественно
        await asyncio.sleep(1.5)

        user_message = m.text

        # Пересылаем сообщение боту @jadvebot
        try:
            # Пересылка пользователю
            bot = "@jadvebot"
            bot_msg = await self.client.send_message(bot, user_message)
            
            # Ждём ответа бота
            async for resp in self.client.iter_messages(bot, reply_to=bot_msg.id, limit=1):
                bot_response = resp.text or "Бот ничего не ответил"
                break
        except:
            bot_response = "Ошибка при связи с ботом"

        # Отправляем ответ пользователю реплаем на его сообщение
        try:
            await m.reply(bot_response)
        except:
            pass

        self.processing[uid_key] = False