from .. import loader, utils
import asyncio
import random

class StableDigiRainMod(loader.Module):
    """Бесконечный цифровой дождь / эффект глитча, стабильная версия"""

    def __init__(self):
        self.running = False

    @loader.command()
    async def digirain(self, m):
        """.digirain — начать стабильный цифровой поток"""
        if self.running:
            return await m.edit("⚠️ Поток уже запущен!")

        self.running = True
        width = 12  # ширина "экрана"
        height = 8  # высота "экрана"
        symbols = "0123456789ABCDEF!@#$%^&*()"

        await m.edit("💻 Запускаю стабильный цифровой дождь...")

        screen = [" " * width for _ in range(height)]
        previous_msg = None

        try:
            while self.running:
                screen.pop()
                new_line = "".join(random.choice(symbols) for _ in range(width))
                screen.insert(0, new_line)
                text = "\n".join(screen)

                if previous_msg:
                    await previous_msg.delete()  # удаляем предыдущий поток

                previous_msg = await m.client.send_message(
                    m.chat_id, text, parse_mode=None
                )

                await asyncio.sleep(0.15)  # скорость падения

        except Exception as e:
            await m.client.send_message(m.chat_id, f"Ошибка: {e}")

    @loader.command()
    async def digistop(self, m):
        """.digistop — остановить цифровой поток"""
        if not self.running:
            return await m.edit("❌ Поток не запущен.")
        self.running = False
        await m.edit("🛑 Цифровой дождь остановлен!")