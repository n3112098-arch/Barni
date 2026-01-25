# meta developer: @B_Mods
# scope: hikka_only
# requires: aiohttp, base64

from .. import loader, utils
import aiohttp, base64

@loader.tds
class KissHF(loader.Module):
    """💋 Генерация поцелуя (HuggingFace img2img, бесплатно)
    
    Использование:
    Реплай на фото с двумя людьми + .kiss
    """

    strings = {"name": "KissHF"}

    SPACE = "stabilityai/stable-diffusion"  # Space на HuggingFace
    PROMPT = "Two people sharing a light kiss, realistic style, natural lighting, neutral background"

    async def kisscmd(self, m):
        if not m.is_reply:
            return await m.edit("❌ Реплай на фото!")

        reply = await m.get_reply_message()
        if not reply.photo:
            return await m.edit("❌ Реплай должен быть на фото!")

        await m.edit("🧠 Генерирую поцелуй... ⏳")

        try:
            img_bytes = await reply.download_media(bytes)
            result_bytes = await self.generate(img_bytes)

            if not result_bytes:
                return await m.edit("❌ HuggingFace не вернул изображение!")

            await m.client.send_file(
                m.chat_id,
                result_bytes,
                reply_to=reply.id
            )
            await m.delete()

        except Exception as e:
            await m.edit(f"❌ Ошибка:\n<code>{e}</code>")

    async def generate(self, image: bytes) -> bytes:
        """Генерация через HF Space img2img"""

        url = f"https://hf.space/embed/{self.SPACE}/+/api/predict/"

        payload = {
            "fn_index": 2,  # стабильный fn_index для img2img
            "data": [
                self.PROMPT,
                "data:image/jpeg;base64," + base64.b64encode(image).decode(),
                0.65,   # denoising strength
                7.5,    # guidance scale
                512,    # width
                512,    # height
                1       # number of images
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=180) as resp:
                # проверяем, что HF вернул JSON
                if resp.content_type != "application/json":
                    text = await resp.text()
                    raise Exception("HF вернул HTML или не JSON:\n" + text[:300])

                data = await resp.json()
                if not data.get("data"):
                    return None

                # base64 изображения
                img64 = data["data"][0].split(",")[-1]
                return base64.b64decode(img64)