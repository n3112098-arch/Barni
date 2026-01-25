# meta developer: @B_Mods
# meta desc: AI module (onlysq OpenAI compatible)
# meta version: 1.0

from openai import OpenAI
from .. import loader, utils


@loader.tds
class OnlySQAI(loader.Module):
    """AI через onlysq OpenAI API"""

    strings = {
        "name": "OnlySQAI",
        "no_text": "❌ Введите текст после команды",
        "error": "⚠️ Ошибка:\n{}",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "API_KEY",
                "",
                "API ключ (любой, если onlysq не проверяет)",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "BASE_URL",
                "https://api.onlysq.ru/ai/openai",
                "Base URL API",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "MODEL",
                "gpt-4o-mini",
                "Модель",
                validator=loader.validators.String(),
            ),
        )

    @loader.command()
    async def ai(self, message):
        """Использование: .ai <вопрос>"""
        text = utils.get_args_raw(message)
        if not text:
            return await message.edit(self.strings["no_text"])

        await message.edit("🤖 Думаю...")

        try:
            client = OpenAI(
                api_key=self.config["API_KEY"],
                base_url=self.config["BASE_URL"],
            )

            response = client.responses.create(
                model=self.config["MODEL"],
                input=text,
            )

            await message.edit(response.output_text)

        except Exception as e:
            await message.edit(self.strings["error"].format(e))