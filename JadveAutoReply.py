# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class JadveAutoReply(loader.Module):
    """Автоответчик через @jadvebot для реальных диалогов"""
    strings = {"name": "JadveAutoReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # user_id -> True
        self.counters = {}  # user_id -> msg count

    @loader.command()
    async def jadstart(self, m):
        """ @user — включить автоответчик через JadveBot """
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")

        self.targets[user.id] = True
        self.counters[user.id] = 0
        await m.edit(f"✅ Теперь автоответчик работает для {user.first_name}")

    @loader.command()
    async def jadstop(self, m):
        """ @user — остановить автоответчик """
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        self.targets.pop(user.id, None)
        self.counters.pop(user.id, None)
        await m.edit(f"🛑 Автоответчик остановлен для {user.first_name}")

    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return

        uid = m.sender_id

        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        # Ответ через @jadvebot
        try:
            # Пересылаем сообщение боту
            forwarded = await self.client.send_message("@jadvebot", m.text or "...")
            await asyncio.sleep(2)  # небольшая пауза для обработки
            # Берём последний ответ бота
            msgs = await self.client.get_messages("@jadvebot", limit=1)
            if not msgs:
                return
            reply_text = msgs[0].text or "🤖"

            # Отправляем ответ человеку реплаем
            await m.reply(reply_text)

        except Exception as e:
            await m.edit(f"❌ Ошибка: {e}")