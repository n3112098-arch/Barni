# Developed by @B_Mods
from .. import loader, utils
import random

class AutoReplyPro2(loader.Module):
    """Автоответчик: отвечает только когда пользователь пишет"""

    strings = {"name": "AutoReplyPro2"}

    def __init__(self):
        self.targets = {}  # chat_id: set(user_ids)

    @loader.command()
    async def rep(self, m):
        """
        @user — включить автоответ пользователю
        """
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Укажи пользователя: `@username`")

        try:
            user = await m.client.get_entity(args)
        except:
            return await m.edit("❌ Не удалось получить пользователя")

        chat = m.chat_id

        if chat not in self.targets:
            self.targets[chat] = set()

        if user.id in self.targets[chat]:
            return await m.edit("⚠️ Уже включено для этого пользователя.")

        self.targets[chat].add(user.id)
        await m.edit(f"🤖 Теперь я буду отвечать {user.first_name} когда он пишет.")

    @loader.command()
    async def repstop(self, m):
        """
        @user — выключить автоответчик
        """
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Укажи пользователя: ` @username`")

        try:
            user = await m.client.get_entity(args)
        except:
            return await m.edit("❌ Не удалось получить пользователя")

        chat = m.chat_id

        if chat in self.targets and user.id in self.targets[chat]:
            self.targets[chat].remove(user.id)
            return await m.edit(f"🛑 Больше не отвечаю {user.first_name}")

        await m.edit("⚠️ Этот пользователь не был активирован.")

    async def watcher(self, m):
        """
        Срабатывает каждый раз когда кто-то пишет сообщение
        """
        if not m or not m.chat or not m.sender_id:
            return

        chat = m.chat_id
        uid = m.sender_id

        if chat not in self.targets:
            return

        if uid not in self.targets[chat]:
            return

        # Берём 150 прошлых сообщений и выбираем текст
        texts = []
        async for msg in m.client.iter_messages(chat, limit=150):
            if msg.text:
                texts.append(msg.text)

        if not texts:
            return

        reply_text = random.choice(texts)

        try:
            await m.respond(reply_text)
        except:
            pass