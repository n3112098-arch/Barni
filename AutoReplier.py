
from .. import loader, utils
import random

class AutoReply(loader.Module):
    """Автоответчик: отвечает только тогда когда пользователь пишет 
    Разработчик:@B_Mods"""
    strings = {"name": "AutoReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}        # user_id -> True
        self.counters = {}       # user_id -> msg count

    async def repcmd(self, m):
        """ @user — включить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")

        self.targets[user.id] = True
        self.counters[user.id] = 0
        await m.edit(f"✅ Теперь отвечаю **{user.first_name}**")

    async def repstopcmd(self, m):
        """ @user — остановить"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        self.targets.pop(user.id, None)
        self.counters.pop(user.id, None)
        await m.edit(f"🛑 Остановлено для **{user.first_name}**")

    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return

        uid = m.sender_id

        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        # Если ответили реплаем — отвечаем всегда
        must_reply = m.is_reply

        # Счётчик сообщений
        self.counters[uid] += 1

        # Если не реплай — отвечаем через 1–3 сообщений
        limit = random.randint(1, 3)

        if not must_reply and self.counters[uid] < limit:
            return

        # Сброс счётчика
        self.counters[uid] = 0

        # Берём текст ТОЛЬКО от людей (не ботов)
        try:
            msgs = await self.client.get_messages(m.chat_id, limit=100)
            texts = []

            for msg in msgs:
                if (
                    msg.text
                    and msg.sender
                    and not msg.sender.bot
                    and msg.sender_id != uid
                ):
                    texts.append(msg.text)

            if not texts:
                return

            reply_text = random.choice(texts)

        except:
            return

        try:
            await m.reply(reply_text)
        except:
            pass
