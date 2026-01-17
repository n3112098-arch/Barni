# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class IntReplayer(loader.Module):
    """Интеллектуальный автоответчик через @gigachat_bot"""
    strings = {"name": "IntReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # chat_id -> user_id
        self.active = {}   # chat_id -> True
        self.me = (await client.get_me()).id  # сохраняем свой ID

    @loader.command()
    async def intstart(self, m):
        """Запуск автоответчика для выбранного пользователя: .intstart @user"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя.")

        if user.bot:
            return await m.edit("❌ Ботам не отвечаю.")

        if user.id == self.me:
            return await m.edit("❌ Я не могу включить автоответ себе!")

        self.targets[m.chat_id] = user.id
        self.active[m.chat_id] = True
        await m.edit(f"✅ Интеллектуальный автоответ включён для **{user.first_name}**")

    @loader.command()
    async def intstop(self, m):
        """Остановить автоответчик в этом чате"""
        self.targets.pop(m.chat_id, None)
        self.active[m.chat_id] = False
        await m.edit("🛑 Автоответчик остановлен")

    async def watcher(self, m):
        # Игнорируем свои сообщения и ботов
        if not m.sender_id or not self.active.get(m.chat_id):
            return
        if m.sender.bot or m.sender_id == self.me:
            return

        target_id = self.targets.get(m.chat_id)
        # Отвечаем только выбранному пользователю
        if not target_id or m.sender_id != target_id:
            return

        # Сообщение для пересылки
        text_to_send = m.text or ""
        if not text_to_send:
            return

        try:
            bot_entity = await self.client.get_entity("@gigachat_bot")
            await self.client.send_message(bot_entity, text_to_send)
            # Ждём пока бот напишет ответ (2 сек)
            await asyncio.sleep(2)
            history = await self.client.get_messages(bot_entity, limit=1)
            bot_response = history[0].text if history else "❌ Бот не ответил."
            # Отправляем реплаем
            await m.reply(bot_response)
        except Exception as e:
            await m.reply(f"❌ Ошибка при взаимодействии с ботом: {e}")
