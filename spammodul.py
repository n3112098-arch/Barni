from .. import loader, utils
import asyncio

class SpamTestMod(loader.Module):
    """Спам сообщений в чат"""

strings = {"name": "Spammy"}

    def __init__(self):
        self.spam_running = False  # флаг, идёт ли спам

    @loader.command()
    async def spammy(self, m):
        """.spammy <count> <text> — начать повтор"""
        if self.spam_running:
            return await m.edit("⚠️ Спам уже запущен! Останови его через .spammyoff")

        args = utils.get_args_raw(m).split(maxsplit=1)
        if len(args) < 2:
            return await m.edit("Использование: .spammy 20 Привет")

        count = int(args[0])
        text = args[1]

        self.spam_running = True
        await m.edit(f"🚀 Запускаю повтор {count} раз...")

        for i in range(count):
            if not self.spam_running:
                await m.client.send_message(m.chat_id, "⛔ Спам остановлен!")
                return

            await m.client.send_message(m.chat_id, text)
            await asyncio.sleep(0.05)  # минимум, чтобы не словить FloodWait

        self.spam_running = False
        await m.client.send_message(m.chat_id, "✔️ Спам завершён!")

    @loader.command()
    async def spammyoff(self, m):
        """.spammyoff — остановить спам"""
        if not self.spam_running:
            return await m.edit("❌ Спам сейчас не запущен.")

        self.spam_running = False
        await m.edit("🛑 Останавливаю спам...")