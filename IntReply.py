# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class intReplayer(loader.Module):
    """Интеллектуальный автоответ через бота @gigachat_bot"""
    strings = {"name": "intReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # chat_id -> set(user_id)
        self.last_bot_msg = {}  # chat_id -> last processed bot msg id

    @loader.command()
    async def intstart(self, m):
        """.intstart <user_id> — включить автоответ для выбранного пользователя"""
        args = utils.get_args_raw(m)
        if not args.isdigit():
            return await m.edit("❌ Укажи ID пользователя")

        user_id = int(args)
        chat_id = m.chat_id

        self.targets.setdefault(chat_id, set()).add(user_id)
        await m.edit(f"✅ Интеллектуальный автоответ включён для {user_id}")

    @loader.command()
    async def intstop(self, m):
        """.intstop <user_id> — остановить автоответ"""
        args = utils.get_args_raw(m)
        if not args.isdigit():
            return await m.edit("❌ Укажи ID пользователя")

        user_id = int(args)
        chat_id = m.chat_id

        if chat_id in self.targets and user_id in self.targets[chat_id]:
            self.targets[chat_id].remove(user_id)
            return await m.edit(f"🛑 Автоответ остановлен для {user_id}")

        await m.edit("❌ Автоответ для этого пользователя не был включён")

    async def watcher(self, m):
        """Ловим новые сообщения выбранных пользователей"""
        if not m.sender_id or not m.chat:
            return

        chat_id = m.chat_id
        sender_id = m.sender_id

        if chat_id not in self.targets or sender_id not in self.targets[chat_id]:
            return

        if m.sender.bot:  # не отвечаем ботам
            return

        bot_username = "@gigachat_bot"

        try:
            # Пересылаем сообщение пользователя боту
            await asyncio.sleep(1)  # небольшая задержка для стабильности
            bot_msg = await m.forward_to(bot_username)

            # Ждём, чтобы бот успел ответить
            await asyncio.sleep(2)

            # Получаем последние сообщения бота
            msgs = await self.client.get_messages(bot_username, limit=10)
            last_id = self.last_bot_msg.get(chat_id, 0)
            new_texts = []

            for msg in reversed(msgs):
                if msg.id == last_id:
                    break
                if msg.text:
                    new_texts.append(msg.text)

            if not new_texts:
                return

            reply_text = "\n".join(new_texts)
            if reply_text.strip():
                await m.reply(reply_text)
                self.last_bot_msg[chat_id] = msgs[0].id

        except Exception as e:
            await m.edit(f"❌ Ошибка при взаимодействии с ботом: {e}")