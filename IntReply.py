# meta developer: @B_Mods
from .. import loader, utils
import asyncio
import time

@loader.tds
class IntReplayer(loader.Module):
    """Интеллектуальный автоответ через @gigachat_bot без копирования"""
    strings = {"name": "IntReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}          # chat_id -> target_user_id
        self.last_bot_reply = {}   # chat_id -> text

    @loader.command()
    async def intstart(self, m):
        """.intstart <id> — включить автоответ"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("❌ Укажи ID пользователя")

        try:
            uid = int(args)
        except:
            return await m.edit("❌ ID должен быть числом")

        self.targets[m.chat_id] = uid
        await m.edit(f"✅ Автоответ включён для ID {uid}")

    @loader.command()
    async def intstop(self, m):
        """.intstop — отключить"""
        self.targets.pop(m.chat_id, None)
        self.last_bot_reply.pop(m.chat_id, None)
        await m.edit("🛑 Автоответ отключён")

    async def watcher(self, m):
        if not m.text or not m.chat or not m.sender_id:
            return

        chat_id = m.chat_id
        if chat_id not in self.targets:
            return

        target_id = self.targets[chat_id]

        # ❌ НИКОГДА не отвечаем себе
        if m.sender_id != target_id:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        bot = "gigachat_bot"
        user_text = m.text.strip()

        # отправляем текст боту
        start_time = time.time()
        await self.client.send_message(bot, user_text)

        # ждём 3.5 сек
        await asyncio.sleep(8.5)

        # читаем несколько сообщений, а не одно
        msgs = await self.client.get_messages(bot, limit=5)

        for msg in msgs:
            if not msg.text:
                continue

            # ❌ если это копия нашего текста — СКИП
            if msg.text.strip() == user_text:
                continue

            # ❌ если бот уже это писал — СКИП
            if self.last_bot_reply.get(chat_id) == msg.text:
                continue

            # ✅ нашли нормальный ответ
            self.last_bot_reply[chat_id] = msg.text
            await m.reply(msg.text)
            return
