# meta developer: @B_Mods
# meta desc: Gemini 3 Pro via onlysq (Termux compatible)
# meta version: 1.0

import aiohttp
from .. import loader, utils


API_KEY = "openai"  # ← вставь ключ (или любой, если onlysq не проверяет)
API_URL = "https://api.onlysq.ru/ai/openai/v1/chat/completions"
MODEL = "gemini-3-pro-preview"


@loader.tds
class GeminiTermux(loader.Module):
    """Gemini 3 Pro (onlysq, Termux)"""

    strings = {
        "name": "GeminiTermux",
        "no_text": "❌ Напиши текст после команды",
        "error": "⚠️ Ошибка:\n{}",
    }

    @loader.command()
    async def gemini(self, message):
        text = utils.get_args_raw(message)
        if not text:
            return await message.edit(self.strings["no_text"])

        await message.edit("🧠 Gemini думает...")

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "user", "content": text}
            ],
            "temperature": 0.7,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, json=payload, headers=headers) as r:
                    data = await r.json()

            answer = data["choices"][0]["message"]["content"]
            await message.edit(answer)

        except Exception as e:
            await message.edit(self.strings["error"].format(e))