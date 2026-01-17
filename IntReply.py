# meta developer: @B_Mods
from .. import loader, utils
import asyncio

@loader.tds
class IntReplayer(loader.Module):
    """Интеллектуальный автоответ через бота @gigachat_bot"""
    strings = {"name": "IntReplayer"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}  # chat_id -> target_user_id

    @loader.command()
    async def intstart(self, m):
        """.intstart <ID> — активировать автоответ для выбранного пользователя"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("❌ Укажи ID пользователя")
        try:
            user_id = int(args)
        except:
            return await m.edit("❌ Неверный ID")
        self.targets[m.chat_id] = user_id
        await m.edit(f"✅ Интеллектуальный автоответ включён для {user_id}")

    @loader.command()
    async def intstop(self, m):
        """.intstop — отключить автоответ"""
        if m.chat_id in self.targets:
            self.targets.pop(m.chat_id)
        await m.edit("🛑 Автоответчик отключён")

    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return

        chat_id = m.chat_id
        sender_id = m.sender_id

        if chat_id not in self.targets:
            return

        target_id = self.targets[chat_id]

        # Игнорируем все сообщения не от выбранного пользователя
        if sender_id != target_id:
            return

        # Игнорируем ботов (кроме нашего @gigachat_bot)
        sender = await m.get_sender()
        if sender.bot:
            return

        bot_username = "gigachat_bot"

        try:
            # Отправляем текст пользователя боту как обычное сообщение
            bot_msg = await self.client.send_message(bot_username, m.text or " ")
            await asyncio.sleep(2)  # ждём, пока бот обработает сообщение

            # Получаем последний ответ бота
            last = await self.client.get_messages(bot_username, limit=1)
            if last:
                reply_text = last[0].text or ""
                if reply_text:
                    await m.reply(reply_text)
        except Exception as e:
            await m.edit(f"❌ Ошибка при взаимодействии с ботом:\n{e}")