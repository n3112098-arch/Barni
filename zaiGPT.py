from .. import loader, utils
import asyncio
import time

@loader.tds
class intReplayer(loader.Module):
    """
    GPT-модуль через @ZettaGPT4o_bot (без цитирования запроса)
    Использование: .zai <запрос> или реплай + .zai
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

        # 1️⃣ Сообщение о начале обработки
        status_msg = await m.respond("🤖 <b>AI обрабатывает запрос...</b> ⏳")

        # 2️⃣ Запоминаем ID последнего сообщения
        old = await self.client.get_messages(self.bot, limit=1)
        last_id = old[0].id if old else 0

        # 3️⃣ Отправляем запрос
        await self.client.send_message(self.bot, query)

        last_text = None
        last_time = None

        # 4️⃣ Ожидание ответа
        for _ in range(20):
            await asyncio.sleep(1)
            msgs = await self.client.get_messages(self.bot, limit=5)

            new = [msg for msg in msgs if msg.id > last_id and msg.text]

            if new:
                last_text = new[0].text
                last_time = time.time()

            if last_text and time.time() - last_time >= 2.5:
                break

        if not last_text:
            return await status_msg.edit("❌ Бот не прислал ответ")

        # 5️⃣ Выводим только ответ нейросети без цитирования вопроса
        await status_msg.edit(f"🤖 <b>Ответ AI:</b>\n\n{utils.escape_html(last_text)}")
        await m.delete()
      
