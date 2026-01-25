# meta developer: @B_Mods
# scope: hikka_only
# requires: aiohttp

from .. import loader, utils
import aiohttp, base64

@loader.tds
class KissHF(loader.Module):
    """💋 Генерация поцелуя (HuggingFace img2img, без ключей)
    
    Использование:
    Реплай на фото с двумя людьми + .kiss
    """

    strings = {"name": "KissHF"}

    SPACE = "stabilityai/stable-diffusion"
    PROMPT = "Two people sharing a light kiss, realistic style, neutral background"

    async def kisscmd(self, m):
        if not m.is_reply:
            return await m.edit("❌ Реплай на фото")

        r = await m.get_reply_message()
        if not r.photo:
            return await m.edit("❌ Это не фото")

        await m.edit("🧠 Генерация поцелуя...")

        try:
            img = await r.download_media(bytes)
            result = await self.generate(img)

            if not result:
                return await m.edit("❌ HF не вернул изображение")

            await m.client.send_file(m.chat_id, result, reply_to=r.id)
            await m.delete()

        except Exception as e:
            await m.edit(f"❌ Ошибка:\n<code>{e}</code>")

    async def get_fn_index(self):
        url = f"https://hf.space/embed/{self.SPACE}/+/config"
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                cfg = await r.json()
                return cfg["dependencies"][-1]["fn_index"]

    async def generate(self, image: bytes):
        fn_index = await self.get_fn_index()

        payload = {
            "fn_index": fn_index,
            "data": [
                self.PROMPT,
                "data:image/jpeg;base64," + base64.b64encode(image).decode(),
                0.65,
                7.5,
                512,
                512,
                1
            ]
        }

        url = f"https://hf.space/embed/{self.SPACE}/+/api/predict/"

        async with aiohttp.ClientSession() as s:
            async with s.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=180
            ) as r:

                if r.content_type != "application/json":
                    text = await r.text()
                    raise Exception("HF вернул HTML:\n" + text[:300])

                data = await r.json()

                if not data.get("data"):
                    return None

                img64 = data["data"][0].split(",")[-1]
                return base64.b64decode(img64)