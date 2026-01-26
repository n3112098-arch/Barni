# meta developer: @B_Mods
# meta name: AiGem
# meta description: GPT-модуль на Gemini (REST API, Termux compatible)

import aiohttp
import json
from .. import loader, utils


GEMINI_API_KEY = "AIzaSyDSmD-JEfgWbIgYskz7vU0eYqIFRVcJRd4"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/models/"
    "gemini-pro:generateContent?key=" + GEMINI_API_KEY
)


@loader.tds
class AiGem(loader.Module):
    """Gemini GPT модуль (работает в Termux)"""

    strings = {
        "name": "AiGem",
        "no_text": "❌ Нет запроса",
        "error": "❌ Ошибка Gemini API",
    }

    async def _ask_gemini(self, prompt: str) -> str:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                GEMINI_URL,
                headers=headers,
                json=payload,
                timeout=60
            ) as resp:

                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")

                data = await resp.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise Exception("Bad response format")

    @loader.command()
    async def ai(self, message):
        """<текст или реплай> — запрос к Gemini"""

        text = utils.get_args_raw(message)

        if not text and message.is_reply:
            reply = await message.get_reply_message()
            text = reply.text

        if not text:
            return await utils.answer(message, self.strings["no_text"])

        wait = await utils.answer(
            message,
            "🤖 <i>Gemini думает...</i>"
        )

        try:
            answer = await self._ask_gemini(text)
        except Exception:
            return await utils.answer(wait, self.strings["error"])

        result = (
            "📌 <b>Запрос:</b>\n"
            f"<blockquote>{utils.escape_html(text)}</blockquote>\n\n"
            "🤖 <b>Ответ AI:</b>\n"
            f"<blockquote>{utils.escape_html(answer)}</blockquote>"
        )

        await utils.answer(wait, result)