from .. import loader, utils
import asyncio

@loader.tds
class ZaiGPT(loader.Module):
    """GPT через @ZettaGPT4o_bot
    ⚠️ Перед использованием ОБЯЗАТЕЛЬНО запусти и настрой бота вручную
    Использование: .zai <текст> или реплай + .zai
    @B_Mods
    """
    strings = {"name": "ZaiGPT"}

    async def client_ready(self, client, db):
        self.client = client
        self.bot = "ZettaGPT4o_bot"

    async def zaicmd(self, m):
        """<запрос> — отправить запрос GPT"""
        query = utils.get_args_raw(m)

        if not query and m.is_reply:
            r = await m.get_reply_message()
            query = r.text or ""

        if not query:
            return await m.edit("❌ Укажи запрос или ответь на сообщение")

        await m.edit("🤖 Запрос отправлен GPT…")

        # отправляем запрос боту
        await self.client.send_message(self.bot, query)

        # ждём, пока бот ответит полностью
        await asyncio.sleep(4)

        # берём ПОСЛЕДНЕЕ сообщение от бота
        msgs = await self.client.get_messages(self.bot, limit=5)
        bot_reply = None

        for msg in msgs:
            if msg.sender and msg.sender.username == self.bot and msg.text:
                bot_reply = msg.text
                break

        if not bot_reply:
            return await m.edit("❌ Не удалось получить ответ от GPT")

        text = (
            "📌 <b>Запрос:</b>\n"
            f"<blockquote>{utils.escape_html(query)}</blockquote>\n\n"
            "🤖 <b>Ответ AI:</b>\n"
            f"<blockquote>{utils.escape_html(bot_reply)}</blockquote>"
        )

        await m.respond(text)
        await m.delete()