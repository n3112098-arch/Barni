# meta developer: @B_Mods
# scope: hikka_only
# requires: aiohttp

from .. import loader, utils
import aiohttp
import asyncio
import base64

@loader.tds
class KissGenFree(loader.Module):
    """💋 Генерация поцелуя из двух фото (бесплатно через HuggingFace).
    Использование:
    1) Реплай на первое фото
    2) Реплай на второе фото + .kiss
    """

    strings = {"name": "KissGenFree"}

    def __init__(self):
        self.buffer = {}

        # 🔧 МОЖНО ПОМЕНЯТЬ SPACE ЕСЛИ УПАДЁТ
        self.space_api = "https://hf.space/embed/fffiloni/facefusion-romantic/+/api/predict"

        self.prompt = (
            "Two people sharing a light kiss, realistic style, "
            "natural lighting, neutral background"
        )

    async def kisscmd(self, m):
        if not m.is_reply:
            return await m.edit("❌ Ответь реплаем на фото")

        reply = await m.get_reply_message()
        if not reply.photo:
            return await m.edit("❌ Это не фото")

        chat = m.chat_id

        # 1️⃣ первое фото
        if chat not in self.buffer:
            self.buffer[chat] = reply
            return await m.edit("📸 Первое фото сохранено. Теперь второе + `.kiss`")

        # 2️⃣ второе фото
        photo1 = self.buffer.pop(chat)
        photo2 = reply

        await m.edit("🧠 Генерирую поцелуй... (может занять до 1 минуты)")

        try:
            img1 = await photo1.download_media(bytes)
            img2 = await photo2.download_media(bytes)

            result = await self._send_to_hf(img1, img2)

            if not result:
                return await m.edit("❌ HuggingFace не ответил")

            await m.client.send_file(chat, result, reply_to=m.reply_to_msg_id)
            await m.delete()

        except Exception as e:
            await m.edit(f"❌ Ошибка генерации:\n<code>{e}</code>")

    async def _send_to_hf(self, img1: bytes, img2: bytes) -> bytes:
        payload = {
            "data": [
                "data:image/jpeg;base64," + base64.b64encode(img1).decode(),
                "data:image/jpeg;base64," + base64.b64encode(img2).decode(),
                self.prompt
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.space_api, json=payload, timeout=120) as r:
                data = await r.json()

                # Gradio обычно возвращает base64 картинки
                if "data" not in data or not data["data"]:
                    return None

                img_b64 = data["data"][0].split(",")[-1]
                return base64.b64decode(img_b64)