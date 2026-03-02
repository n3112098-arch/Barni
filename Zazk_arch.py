# meta developer: @B_Mods
# scope: hikka_only
# scope: hikka_min 1.6.3

from .. import loader, utils


@loader.tds
class Zazc(loader.Module):
    """Отметка человека в ЛС своей припиской"""

    strings = {"name": "Zazc"}

    async def zazc(self, message):
        """.zazc <текст> — отметить человека в ЛС своей припиской"""

        text = utils.get_args_raw(message)

        if not text:
            return await utils.answer(message, "❌ Укажи текст")

        if not message.is_private:
            return await utils.answer(
                message,
                "❌ Команда работает только в личных сообщениях"
            )

        user_id = message.chat_id

        mention = f'<a href="tg://user?id={user_id}">{utils.escape_html(text)}</a>'

        await utils.answer(message, mention)
