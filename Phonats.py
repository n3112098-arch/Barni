from .. import loader, utils
import asyncio
import random

class DigitalRainMod(loader.Module):
    """Цифровой дождь / эффект глитча"""

    def __init__(self):
        self.running = False

    @loader.command()
    async def digirain(self, m):
        """.digirain — начать цифровой поток"""
        if self.running:
            return await m.edit("⚠️ Поток уже запущен!")

        self.running = True
        width = 20  # ширина “экрана”
        height = 10  # высота “экрана”
        symbols = "0123456789ABCDEF!@#$%^&*()"

        await m.edit("💻 Запускаю цифровой дождь...")

        # текущие строки
        screen = [" " * width for _ in range(height)]

        while self.running:
            # сдвигаем экран вниз
            screen.pop()
            # новая строка
            new_line = "".join(random.choice(symbols) for _ in range(width))
            screen.insert(0, new_line)
            # собираем текст для отправки
            text = "\n".join(screen)
            await m.edit(text)
            await asyncio.sleep(0.15)  # скорость падения

    @loader.command()
    async def digistop(self, m):
        """.digistop — остановить цифровой поток"""
        if not self.running:
            return await m.edit("❌ Поток не запущен.")
        self.running = False
        await m.edit("🛑 Цифровой дождь остановлен!")