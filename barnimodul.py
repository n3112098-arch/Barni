# meta developer: @yourusername

from .. import loader, utils

class MyModule(loader.Module):
    """Описание твоего модуля"""

    @loader.command()
    async def test(self, message):
        """Команда .test"""
        await message.edit("Модуль работает!")