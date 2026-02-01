from .. import loader, utils
import asyncio
import time
import re  # Добавили для очистки текста

@loader.tds
class intReplayer(loader.Module):
    """
    GPT-модуль через @ZettaGPT4o_bot
    Использование: .zai <запрос> или реплай + .zai

    ⚠️ Бота нужно предварительно настроить вручную
    @B_Mods
    """
    strings = {"name": "zaiGpt"}

    async def client_ready(self, client, db):
        self.client = client
        self.bot = "ZettaGPT4o_bot"

    async def zaicmd(self, m):
        query = utils.get_args_raw(m)

        if not query and m.is_reply:
            r = await m.get_reply_message()
            query = r.text or ""

        if not query:
            return await m.edit("❌ Укажи запрос")

        # 1️⃣ Публикуем сообщение-заглушку
        status_msg = await m.respond(
            "📌 <b>Запрос:</b>\n"
            f"<blockquote>{utils.escape_html(query)}</blockquote>\n\n"
            "🤖 <b>Ответ AI:</b>\n"
            "<blockquote>Обрабатываю ваш запрос… ⏳</blockquote>"
        )

        # 2️⃣ Запоминаем последнее сообщение бота ДО запроса
        old = await self.client.get_messages(self.bot, limit=1)
        last_id = old[0].id if old else 0

        # 3️⃣ Отправляем запрос боту
        await self.client.send_message(self.bot, query)

        last_text = None
        last_time = None

        # 4️⃣ Ждём ответы бота
        for _ in range(20):  # ~20 секунд максимум
            await asyncio.sleep(1)

            msgs = await self.client.get_messages(self.bot, limit=5)

            new = [
                msg for msg in msgs
                if msg.id > last_id and msg.text
            ]

            if new:
                last_text = new[0].text
                last_time = time.time()

            # 🛑 КЛЮЧЕВАЯ ЛОГИКА ОСТАНОВКИ
            if last_text and time.time() - last_time >= 2.5:
                break

        if not last_text:
            return await status_msg.edit(
                "❌ Бот не прислал ответ"
            )

        # Убираем теги <b> и </b> из текста ответа бота
        last_text = re.sub(r'<(/?)(b|strong)>', '', last_text)

        # 5️⃣ РЕДАКТИРУЕМ сообщение
        final_text = (
            "📌 <b>Запрос:</b>\n"
            f"<blockquote>{utils.escape_html(query)}</blockquote>\n\n"
            "🤖 <b>Ответ AI:</b>\n"
            f"<blockquote>{utils.escape_html(last_text)}</blockquote>"
        )

        await status_msg.edit(final_text)
        await m.delete()
          
