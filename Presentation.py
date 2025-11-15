from .. import loader, utils
import asyncio
from PIL import Image, ImageDraw, ImageFont
import io
import random

class PresMakerMod(loader.Module):
    """Генератор презентаций в стиле PowerPoint"""
    
    strings = {"name": "PresentationMaker"}

    @loader.command()
    async def pres(self, m):
        """.pres <slides 1-10> <topic> — создать презентацию"""
        args = utils.get_args_raw(m).split(maxsplit=1)
        if len(args) < 2:
            return await m.edit("Использование: .pres 5 История Украины")

        try:
            slides = int(args[0])
        except:
            return await m.edit("Первый аргумент должен быть числом.")

        if slides < 1 or slides > 10:
            return await m.edit("Количество слайдов: от 1 до 10.")

        topic = args[1]

        await m.edit(f"📘 Создаю презентацию на тему: **{topic}**…")

        images = []
        for i in range(slides):
            img = self.generate_slide(topic, i + 1)
            images.append(img)

        await m.edit("📤 Отправляю слайды…")

        for png in images:
            await m.client.send_file(m.chat_id, png)

        await m.respond("✔️ Презентация готова!")

    # ---------- Генерация одного слайда ----------
    def generate_slide(self, topic, number):
        width, height = 1280, 720
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # Верхний синий бар
        draw.rectangle((0, 0, width, 120), fill=(25, 85, 165))

        # Шрифты
        try:
            title_font = ImageFont.truetype("arial.ttf", 52)
            text_font = ImageFont.truetype("arial.ttf", 36)
        except:
            title_font = ImageFont.load_default()
            text_font = ImageFont.load_default()

        # Заголовок
        draw.text((40, 25), topic, fill="white", font=title_font)

        # Подзаголовок
        draw.text((40, 150), f"Слайд {number}", fill="black", font=title_font)

        # Автоматически генерируемый текст по теме
        body = self.generate_text(topic)
        draw.text((40, 260), body, fill="black", font=text_font)

        # Сохранение в PNG
        bio = io.BytesIO()
        bio.name = f"slide_{number}.png"
        img.save(bio, "PNG")
        bio.seek(0)

        return bio

    # ---------- Генератор текста (авто-подпункты) ----------
    def generate_text(self, topic):
        templates = [
            f"Основные аспекты по теме: {topic}.",
            f"Ключевые моменты и важные факты о {topic}.",
            f"Обзор главных идей, связанных с темой: {topic}.",
            f"Что важно знать о {topic}.",
            f"Краткое описание ключевых элементов {topic}.",
            f"Фундаментальные особенности темы {topic}."
        ]
        return random.choice(templates)