# meta developer: @B_Mods
from .. import loader, utils
import asyncio

class JadveBotReply(loader.Module):
    """Автоответчик через @jadvebot
    Разработчик: @B_Mods
    """
    strings = {"name": "JadveReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # chat_id -> set(user_id)
        self.processing = {}  # chat_id -> bool, чтобы не гонять по нескольку раз

    @loader.command()
    async def jadstart(self, m):
        """.jadstart @user — активировать автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        self.targets.setdefault(m.chat_id, set()).add(user.id)
        await m.edit(f"✅ Автоответчик включен для {user.first_name}")

    @loader.command()
    async def jadstop(self, m):
        """.jadstop @user — выключить автоответ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        if m.chat_id in self.targets and user.id in self.targets[m.chat_id]:
            self.targets[m.chat_id].remove(user.id)
            await m.edit(f"🛑 Автоответчик выключен для {user.first_name}")
        else:
            await m.edit("Этот пользователь не был включён")

    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return
        if m.sender.bot:
            return
        chat_id = m.chat_id
        sender_id = m.sender_id

        # Проверяем включён ли автоответчик для этого юзера в этом чате
        if chat_id not in self.targets or sender_id not in self.targets[chat_id]:
            return

        # Проверка, чтобы не гонять параллельно одно и то же сообщение
        if self.processing.get((chat_id, m.id)):
            return
        self.processing[(chat_id, m.id)] = True

        try:
            # Пересылаем сообщение @jadvebot
            bot_msg = await self.client.send_message("@jadvebot", m.text or m.message)

            # Ждём ответ бота (можно настроить таймаут)
            await asyncio.sleep(1)
            msgs = await self.client.get_messages("@jadvebot", limit=1)
            if msgs:
                reply_text = msgs[0].text
                if reply_text:
                    # Ответ пользователю реплаем на его сообщение
                    await m.reply(reply_text)
        except:
            pass
        finally:
            # Снимаем блокировку
            self.processing.pop((chat_id, m.id), None)