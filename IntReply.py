# meta developer: @B_Mods
from .. import loader, utils
import asyncio
from collections import defaultdict

@loader.tds
class IntReply(loader.Module):
    """Интеллектуальный автоответчик через внешнего бота"""
    strings = {"name": "IntReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.active_users = {}  # user_id -> True
        self.queues = defaultdict(asyncio.Queue)  # user_id -> очередь сообщений
        self.bot_id = None

    @loader.command()
    async def intstart(self, m):
        """@user — включить автоответ для выбранного пользователя и задать бота"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Использование:\n.intstart @user @bot")

        parts = args.split()
        if len(parts) != 2:
            return await m.edit("Укажи пользователя и бота: `.intstart @user @bot`")

        user_entity = await utils.get_user(m, parts[0])
        bot_entity = await utils.get_user(m, parts[1])

        if not user_entity or not bot_entity:
            return await m.edit("❌ Не удалось получить пользователя или бота")

        self.active_users[user_entity.id] = True
        self.bot_id = bot_entity.id
        await m.edit(f"✅ Интеллектуальный автоответ включён для **{user_entity.first_name}** через бота **{bot_entity.first_name}**")

    @loader.command()
    async def intstop(self, m):
        """Остановить автоответ"""
        self.active_users.clear()
        self.queues.clear()
        await m.edit("🛑 Интеллектуальный автоответ отключён")

    async def watcher(self, m):
        """Следим за сообщениями выбранного пользователя и пересылаем боту"""
        if not m.sender_id or not m.chat:
            return

        uid = m.sender_id

        if uid not in self.active_users:
            return

        # Игнорируем ботов кроме выбранного
        sender = await m.get_sender()
        if sender.bot and uid != self.bot_id:
            return

        # Пересылаем сообщение боту
        try:
            # Отправляем полный текст
            sent_msg = await self.client.send_message(self.bot_id, m.text or "")
            # Сохраняем, чтобы потом отправить ответ в очередь
            self.queues[uid].put_nowait((m.chat_id, m.id, sent_msg.id))
        except:
            return

        # Ждём ответа от бота в отдельном таске
        asyncio.create_task(self.handle_bot_response(uid))

    async def handle_bot_response(self, user_id):
        """Получаем ответ от бота и отправляем пользователю реплаем"""
        queue = self.queues[user_id]
        if queue.empty():
            return

        chat_id, reply_to_id, bot_msg_id = await queue.get()

        # Ждём появления нового сообщения от бота
        while True:
            async for msg in self.client.iter_messages(self.bot_id, limit=5):
                if msg.id == bot_msg_id:
                    continue
                if msg.text:
                    # Отправляем обратно пользователю
                    try:
                        await self.client.send_message(chat_id, msg.text, reply_to=reply_to_id)
                    except:
                        pass
                    return
            await asyncio.sleep(0.5)