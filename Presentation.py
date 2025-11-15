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
            return await m.edit("Использование: .pres 5 История")

        # Количество
        try:
            slides = int(args[0])
        except:
            return await m.edit("Первый аргумент должен быть числом.")

        if not 1 <= slides <= 10:
            return await m.edit("Количество должно быть от 1 до 10.")

        # Тема
        topic = args[1]

        await m.edit(f"📘 Создаю презентацию на тему: **{topic}**…")

        files = []
        for i in range(slides):
            img = self.make_slide(topic, i+1)
            files.append(img)

        await m.edit("📤 Отправляю слайды…")

        for file in files:
            await m.client.send_file(m.chat_id, file)

        await m.respond("✔️ Презентация готова!")

    # Генерируем PNG-слайд
    def make_slide(self, topic, num):
        W, H = 1280, 720
        img = Image.new("RGB", (W, H), "white")
        drw = ImageDraw.Draw(img)

        # Встроенный шрифт (работает на всех системах)
        font_big = ImageFont.load_default()
        font_mid = ImageFont.load_default()
        font_small = ImageFont.load_default()

        # Верхний синий бар
        drw.rectangle([0, 0, W, 120], fill=(25, 85, 165))

        # Заголовок в синей полосе
        drw.text((40, 40), topic, fill="white", font=font_big)

        # Подзаголовок
        drw.text((40, 160), f"Слайд {num}", fill="black", font=font_big)

        # Сгенерированный текст
        body = self.gen(topic)
        drw.text((40, 260), body, fill="black", font=font_mid)

        # сохраняем в память
        bio = io.BytesIO()
        bio.name = f"slide_{num}.png"
        img.save(bio, "PNG")
        bio.seek(0)
        return bio

    # Генератор текста по теме
    def gen(self, topic):
        templates = [
            f"Основные сведения по теме: {topic}.",
            f"Краткое описание ключевых идей {topic}.",
            f"Факты и важные элементы темы: {topic}.",
            f"Что нужно знать о {topic}.",
            f"Введение в концепцию {topic}.",
        ]
        return random.choice(templates)