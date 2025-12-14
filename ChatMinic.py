# meta developer: @B_Mods
from .. import loader, utils
import random
import asyncio


def score(text, query_words):
    words = set(text.lower().split())
    return len(words & query_words)


def smart_pick(user_text, own_texts, foreign_texts):
    query_words = set(user_text.lower().split())

    ranked = []

    for msg in own_texts:
        s = score(msg, query_words)
        if s:
            ranked.append((s + 2, msg))  # приоритет своим

    for msg in foreign_texts:
        s = score(msg, query_words)
        if s:
            ranked.append((s, msg))

    if ranked:
        ranked.sort(reverse=True)
        return ranked[0][1]

    pool = own_texts or foreign_texts
    return random.choice(pool) if pool else None


@loader.tds
class ChatMimic(loader.Module):
    """
    Имитация живого диалога.
    Отвечает логично, подбирая фразы из чата и твоих сообщений.
    """
    strings = {"name": "ChatMimic"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}
        self.counters = {}

    @loader.command()
    async def mimic(self, m):
        """.mimic <user> — начать имитацию общения"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        if user.bot:
            return await m.edit("❌ Боты не поддерживаются")

        self.targets[user.id] = True
        self.counters[user.id] = 0
        await m.edit(f"🎭 ChatMimic активирован для **{user.first_name}**")

    @loader.command()
    async def mimicstop(self, m):
        """.mimicstop <user> — остановить"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        self.targets.pop(user.id, None)
        self.counters.pop(user.id, None)
        await m.edit(f"🛑 ChatMimic остановлен для **{user.first_name}**")

    async def watcher(self, m):
        if not m or not m.chat or not m.sender_id:
            return

        uid = m.sender_id
        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if not sender or sender.bot:
            return

        self.counters[uid] += 1

        must_reply = m.is_reply
        limit = random.randint(1, 3)

        if not must_reply and self.counters[uid] < limit:
            return

        self.counters[uid] = 0

        try:
            me = await self.client.get_me()
            msgs = await self.client.get_messages(m.chat_id, limit=120)

            own_texts = []
            foreign_texts = []

            for msg in msgs:
                if not msg.text or not msg.sender or msg.sender.bot:
                    continue

                if msg.sender_id == me.id:
                    own_texts.append(msg.text)
                elif msg.sender_id != uid:
                    foreign_texts.append(msg.text)

            reply_text = smart_pick(m.text, own_texts, foreign_texts)
            if not reply_text:
                return

            await asyncio.sleep(random.uniform(0.7, 2.0))
            await m.reply(reply_text)

        except:
            return
