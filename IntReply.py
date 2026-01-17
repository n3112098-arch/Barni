# meta developer: @B_Mods
from .. import loader, utils
import asyncio

class IntelligentReply(loader.Module):
    """Интеллектуальный автоответ через @jadvebot
    Разработчик: @B_Mods"""
    strings = {"name": "IntReply"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}        # chat_id -> set(user_id)
        self.processing = {}     # chat_id,message_id -> bool

    @loader.command()
    async def intstart(self, m):
        """ .intstart @user — включить автоответ для пользователя """
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")
        self.targets.setdefault(m.chat_id, set()).add(user.id)
        await m.edit(f"✅ Интеллектуальный автоответ включён для {user.first_name}")

    @loader.command()
    async def intstop(self, m):
        """ .intstop @user — выключить автоответ """
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

        # Проверяем, включён ли автоответчик для этого пользователя
        if chat_id not in self.targets or sender_id not in self.targets[chat_id]:
            return

        # Блокировка одного сообщения
        key = (chat_id, m.id)
        if self.processing.get(key):
            return
        self.processing[key] = True

        try:
            # Берём полный текст сообщения
            full_text = m.text or m.message
            if not full_text:
                return

            # Пересылаем полный текст @jadvebot
            bot_msg = await self.client.send_message("@jadvebot", full_text)

            # Ждём ответа, можно увеличить если бот медленный
            await asyncio.sleep(1)
            # Берём последнее сообщение от бота
            bot_msgs = await self.client.get_messages("@jadvebot", limit=1)
            if bot_msgs and bot_msgs[0].text:
                reply_text = bot_msgs[0].text
                # Ответ пользователю реплаем на его сообщение
                await m.reply(reply_text)

        except Exception as e:
            print(f"[IntReply ERROR] {e}")
        finally:
            # Снимаем блокировку
            self.processing.pop(key, None)