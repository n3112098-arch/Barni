# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class IntReplayer(loader.Module):
    """Интеллектуальный автоответчик через @gigachat_bot по ID"""
    strings = {"name": "IntReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # chat_id -> target user_id
        self.active = {}   # chat_id -> bool
        me = await client.get_me()
        self.me = me.id

    @loader.command()
    async def intstart(self, m):
        """Запуск автоответчика по ID: .intstart <id>"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("❌ Укажи ID пользователя: `.intstart 123456789`")

        try:
            user_id = int(args)
        except ValueError:
            return await m.edit("❌ ID должен быть числом.")

        if user_id == self.me:
            return await m.edit("❌ Я не могу включить автоответ себе!")

        self.targets[m.chat_id] = user_id
        self.active[m.chat_id] = True
        await m.edit(f"✅ Интеллектуальный автоответ включён для пользователя с ID: `{user_id}`")

    @loader.command()
    async def intstop(self, m):
        """Остановить автоответчик"""
        self.targets.pop(m.chat_id, None)
        self.active[m.chat_id] = False
        await m.edit("🛑 Автоответчик остановлен")

    async def watcher(self, m):
        if not m.sender_id or not self.active.get(m.chat_id):
            return
        if m.sender.bot or m.sender_id == self.me:
            return

        target_id = self.targets.get(m.chat_id)
        if not target_id or m.sender_id != target_id:
            return

        # Берём текст сообщения пользователя
        text_to_send = m.text or ""
        if not text_to_send:
            return

        try:
            # Пересылаем сообщение боту
            bot = await self.client.get_entity("@gigachat_bot")
            sent_msg = await self.client.send_message(bot, text_to_send)

            # Ждём, пока бот ответит (можно подстроить задержку)
            await asyncio.sleep(2)  # задержка 2 секунды

            # Берём последнее сообщение бота
            history = await self.client.get_messages(bot, limit=1)
            bot_response = history[0].text if history else "❌ Бот не ответил."

            # Отправляем ответ бота пользователю
            await m.reply(bot_response)

        except Exception as e:
            await m.reply(f"❌ Ошибка при взаимодействии с ботом: {e}")