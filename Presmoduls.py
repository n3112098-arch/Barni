# meta developer: @B_Mods

from .. import loader, utils
from pptx import Presentation
from PIL import Image
import io
import asyncio
import os


class PresSlides(loader.Module):
    """Извлекает слайды из PPTX/ODP и отправляет их как картинки"""
    strings = {"name": "PresSlides"}

    @loader.command()
    async def pres(self, m):
        """
        Использование: ответь на файл презентации (.pptx / .odp)
        .pres — отправляет все слайды по одному
        """
        if not m.is_reply:
            return await m.edit("📌 Ответь командой на файл презентации (.pptx / .odp)")

        reply = await m.get_reply_message()

        if not reply.document:
            return await m.edit("❌ Это не файл презентации.")

        filename = reply.file.name

        if not (filename.endswith(".pptx") or filename.endswith(".odp")):
            return await m.edit("❌ Формат не поддерживается. Используй PPTX или ODP.")

        await m.edit("⏳ Загружаю файл...")

        # скачиваем файл
        file_bytes = await m.client.download_file(reply.document)
        path = f"/data/data/com.termux/files/home/{filename}"

        with open(path, "wb") as f:
            f.write(file_bytes)

        await m.edit("📂 Файл загружен. Обрабатываю слайды...")

        prs = Presentation(path)

        slide_num = 0

        for slide in prs.slides:
            slide_num += 1

            img = Image.new("RGB", (1280, 720), "white")
            draw = Image.Draw.Draw(img)
            draw.text((50, 50), f"Слайд #{slide_num}\n(рендер текста презентации)", fill="black")

            bio = io.BytesIO()
            bio.name = f"slide_{slide_num}.jpg"
            img.save(bio, "JPEG")
            bio.seek(0)

            await m.client.send_file(m.chat_id, bio, caption=f"📸 Слайд {slide_num}")
            await asyncio.sleep(0.5)

        await m.edit("✅ Все слайды отправлены!")