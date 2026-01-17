# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class IntReplayer(loader.Module):
    """Интеллектуальный автоответчик через @gigachat_bot по ID"""
    strings = {"name": "IntReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}         # chat_id -> target user_id
        self.active = {}          # chat_id -> bool
        self.last_bot_msg = {}    # chat_id -> last bot message id
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
        self.last_bot_msg[m.chat_id] = None
        await m.edit(f"✅ Интеллектуальный автоответ включён для пользователя с ID: `{user_id}`")

    @loader.command()
    async def intstop(self, m):
        """Остановить автоответчик"""
        self.targets.pop(m.chat_id, None)
        self.active[m.chat_id] = False
        self.last_bot_msg.pop(m.chat_id, None)
        await m.edit("🛑 Автоответчик остановлен")

    async def watcher(self, m):
        if not m.sender_id or not self.active.get(m.chat_id):
            return
        if m.sender.bot or m.sender_id == self.me:
            return

        target_id = self.targets.get(m.chat_id)
        if not target_id or m.sender_id != target_id:
            return

        text_to_send = m.text or ""
        if not text_to_send:
            return

        try:
            bot = await self.client.get_entity("@gigachat_bot")
            await self.client.send_message(bot, text_to_send)
            await asyncio.sleep(2)  # задержка для ответа бота

            # Берём новые сообщения бота после последнего обработанного
            last_id = self.last_bot_msg.get(m.chat_id)
            msgs = await self.client.get_messages(bot, limit=10)
            new_texts = []
            for msg in reversed(msgs):
                if msg.id == last_id:
                    break
                if msg.text:
                    new_texts.append(msg.text)

            if not new_texts:
                return

            reply_text = "\n".join(new_texts)
            await m.reply(reply_text)

            # Обновляем ID последнего сообщения
            self.last_bot_msg[m.chat_id] = msgs[0].id

        except Exception as e:
            await m.reply(f"❌ Ошибка при взаимодействии с ботом: {e}")