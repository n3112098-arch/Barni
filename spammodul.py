from .. import loader, utils
import asyncio

class SpamTestMod(loader.Module):
    """Тестовый повтор сообщений"""

    @loader.command()
    async def spammy(self, m):
        """.spammy <count> <text> — повторить сообщение"""
        args = utils.get_args_raw(m).split(maxsplit=1)
        if len(args) < 2:
            return await m.edit("Использование: .spammy 20 Пример текста")

        count = int(args[0])
        text = args[1]

        await m.edit(f"Стартую повтор {count} раз...")

        for i in range(count):
            try:
                await m.client.send_message(m.chat_id, text)
                await asyncio.sleep(0.01)  # ~50 мс — самый минимум
            except Exception as e:
                await m.client.send_message(m.chat_id, f"Ошибка: {e}")
                break