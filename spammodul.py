# meta developer: @yourusername

from .. import loader, utils
import asyncio


class SpammyProMod(loader.Module):
    """Продвинутый модуль для повторения сообщений"""

    strings = {
        "name": "Spammy Pro",
        "already_running": "⚠️ Спам уже выполняется! Останови через .spammyoff",
        "usage": "Использование: .spammy <кол-во> <текст>",
        "starting": "🚀 Запускаю спам на {count} сообщений...",
        "stopped": "🛑 Спам остановлен!",
        "finished": "✔️ Спам завершён!"
    }

    def __init__(self):
        self.running = False  # флаг, идёт ли спам

    @loader.command()
    async def spammy(self, message):
        """
        .spammy <кол-во> <текст>
        — запускает повтор сообщения
        """
        if self.running:
            return await message.edit(self.strings["already_running"])

        args = utils.get_args_raw(message).split(maxsplit=1)
        if len(args) < 2:
            return await message.edit(self.strings["usage"])

        count = args[0]
        text = args[1]

        if not count.isdigit():
            return await message.edit("❌ Количество должно быть числом.")

        count = int(count)
        self.running = True

        await message.edit(self.strings["starting"].format(count=count))

        for _ in range(count):
            if not self.running:
                return await message.client.send_message(
                    message.chat_id,
                    self.strings["stopped"]
                )

            await message.client.send_message(message.chat_id, text)
            await asyncio.sleep(0.05)  # минимальная пауза, чтобы избежать флада

        self.running = False
        await message.client.send_message(message.chat_id, self.strings["finished"])

    @loader.command()
    async def spammyoff(self, message):
        """
        .spammyoff
        — останавливает спам
        """
        if not self.running:
            return await message.edit("❌ Спам сейчас не запущен.")

        self.running = False
        await message.edit(self.strings["stopped"])