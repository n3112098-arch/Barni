# meta developer: @B_Mods
# scope: hikka_only
# requires: aiohttp

from .. import loader, utils
import aiohttp
import base64

@loader.tds
class KissGen(loader.Module):
    """💋 Генерация поцелуя (бесплатно через HuggingFace, img2img)
    
    Использование:
    Реплай на фото с двумя людьми + .kiss
    """

    strings = {"name": "KissGen"}

    def __init__(self):
        self.api = "https://hf.space/embed/stabilityai/stable-diffusion/+/api/predict"
        self.prompt = (
            "Two people sharing a light kiss, realistic style, "
            "natural lighting, neutral background"
        )

    async def kisscmd(self, m):
        if not m.is_reply:
            return await m.edit("❌ Реплай на фото")

        reply = await m.get_reply_message()
        if not reply.photo:
            return await m.edit("❌ Это не фото")

        await m.edit("🧠 Генерирую поцелуй...")

        try:
            img = await reply.download_media(bytes)
            result = await self._img2img(img)

            if not result:
                return await m.edit("❌ Генерация не удалась")

            await m.client.send_file(
                m.chat_id,
                result,
                reply_to=reply.id
            )
            await m.delete()

        except Exception as e:
            await m.edit(f"❌ Ошибка:\n<code>{e}</code>")

    async def _img2img(self, image: bytes) -> bytes:
        payload = {
            "data": [
                self.prompt,
                "data:image/jpeg;base64," + base64.b64encode(image).decode(),
                0.65
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.api, json=payload, timeout=120) as r:
                data = await r.json()

                if "data" not in data or not data["data"]:
                    return None

                img_b64 = data["data"][0].split(",")[-1]
                return base64.b64decode(img_b64)