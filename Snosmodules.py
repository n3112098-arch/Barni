# meta developer: @B_mods

from .. import loader, utils
import asyncio

class SnosMod(loader.Module):
    """модуль для сноса аккаунта"""

    strings = {
        "name": "Snos"
    }

    @loader.command()
    async def snos(self, message):
        """Запуск удаления аккаунта"""

        await message.edit("⛔ Инициализация процесса удаления аккаунта...")
        await asyncio.sleep(1.5)

        await message.edit("📡 Проверка данных пользователя...")
        await asyncio.sleep(1.5)

        await message.edit("🔐 Синхронизация с сервером Telegram...")
        await asyncio.sleep(1.5)

        # 15 секундный прогресс от 1 до 100%
        for i in range(1, 101):
            await message.edit(f"🗑 Удаление аккаунта...\n\nПрогресс: {i}%")
            await asyncio.sleep(0.15)  # 100 * 0.15 = 15 секунд

        await asyncio.sleep(1)

        await message.edit(
            "✅ Процесс успешно завершён.\n\n"
            "🧹 Аккаунт пользователя удалён."
        )