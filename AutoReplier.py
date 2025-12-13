# meta developer: @B_Mods
from .. import loader, utils
import random


@loader.tds
class AutoReply(loader.Module):
    """Автоответчик — отвечает только когда пользователь пишет"""
    strings = {"name": "AutoReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}    # user_id -> counter

    # ========= ВКЛЮЧИТЬ =========
    @loader.command()
    async def rep(self, m):
        """ .rep <@user | reply> — включить автоответ """
        user = None

        if m.is_reply:
            reply = await m.get_reply_message()
            user = await reply.get_sender()
        else:
            args = utils.get_args_raw(m)
            if not args:
                return await m.edit("❌ Укажи пользователя или ответь на сообщение")
            try:
                user = await m.client.get_entity(args)
            except:
                return await m.edit("❌ Пользователь не найден")

        if not user or user.bot:
            return await m.edit("❌ Ботам нельзя")

        if user.id == (await m.client.get_me()).id:
            return await m.edit("❌ Нельзя отвечать самому себе")

        self.targets[user.id] = 0
        await m.edit(f"✅ Автоответ включён для **{user.first_name}**")

    # ========= ВЫКЛЮЧИТЬ =========
    @loader.command()
    async def repstop(self, m):
        """ .repstop <@user | reply> — выключить автоответ """
        user = None

        if m.is_reply:
            reply = await m.get_reply_message()
            user = await reply.get_sender()
        else:
            args = utils.get_args_raw(m)
            if not args:
                return await m.edit("❌ Укажи пользователя или ответь на сообщение")
            try:
                user = await m.client.get_entity(args)
            except:
                return await m.edit("❌ Пользователь не найден")

        if user and user.id in self.targets:
            self.targets.pop(user.id)
            return await m.edit(f"🛑 Автоответ отключён для **{user.first_name}**")

        await m.edit("ℹ️ Для этого пользователя автоответ не был включён")

    # ========= ЛОВИМ СООБЩЕНИЯ =========
    async def watcher(self, m):
        if not m or not m.sender_id or not m.chat:
            return

        uid = m.sender_id

        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if not sender or sender.bot:
            return

        # если пользователь ответил тебе — отвечаем всегда
        must_reply = m.is_reply

        self.targets[uid] += 1
        limit = random.randint(1, 3)

        if not must_reply and self.targets[uid] < limit:
            return

        self.targets[uid] = 0

        # Берём старые сообщения ТОЛЬКО от людей
        try:
            msgs = await m.client.get_messages(m.chat_id, limit=100)
            texts = [
                msg.text for msg in msgs
                if msg.text
                and msg.sender
                and not msg.sender.bot
                and msg.sender_id != uid
            ]

            if not texts:
                return

            await m.reply(random.choice(texts))

        except:
            pass