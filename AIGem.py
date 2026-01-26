# meta developer: @you
# scope: hikka_only
# scope: hikka_min 1.6.3

import aiohttp
from .. import loader, utils


@loader.tds
class Ai(loader.Module):
    """GPT-модуль на Gemini (работает в Termux, без библиотек)"""

    strings = {
        "name": "Ai",
        "no_args": "❌ Укажи запрос",
        "api_error": "❌ Ошибка Gemini API",
    }

    # 🔑 ТВОЙ КЛЮЧ (УЖЕ ВСТАВЛЕН)
    GEMINI_API_KEY = "AIzaSyDSmD-JEfgWbIgYskz7vU0eYqIFRVcJRd4"

    GEMINI_URL = (
        "https://generativelanguage.googleapis.com/v1/models/"
        "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
    )

    async def ai(self, message):
        """.ai <запрос> — задать вопрос ИИ"""
        prompt = utils.get_args_raw(message)
        if not prompt:
            return await utils.answer(message, self.strings["no_args"])

        await utils.answer(message, "🧠 Думаю...")

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.GEMINI_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                ) as resp:
                    data = await resp.json()

            result = (
                data["candidates"][0]["content"]["parts"][0]["text"]
            )

            text = (
                f"📌 <b>Запрос:</b>\n<blockquote>{utils.escape_html(prompt)}</blockquote>\n\n"
                f"🤖 <b>Ответ AI:</b>\n<blockquote>{utils.escape_html(result)}</blockquote>"
            )

            await utils.answer(message, text)

        except Exception as e:
            await utils.answer(
                message,
                f"{self.strings['api_error']}\n<code>{e}</code>",
            )