# meta developer: @B_Mods

from .. import loader, utils


class ZazcTag(loader.Module):
    """Скрытая отметка пользователя по своей приписке"""
    strings = {"name": "ZazcTag"}

    @loader.command()
    async def zazc(self, m):
        """
        @user Текст
        или ответом на сообщение: .zazc Текст
        """

        args = utils.get_args_raw(m)

        # Если ответом
        if m.is_reply:
            reply = await m.get_reply_message()
            user = reply.sender
            text = args
        else:
            if not args or len(args.split()) < 2:
                return await m.edit("❌ Использование:\n.zazc @user текст")

            user = await utils.get_user(m)
            text = args.split(" ", 1)[1]

        if not user or not text:
            return await m.edit("❌ Ошибка получения данных")

        mention = f'<a href="tg://user?id={user.id}">{utils.escape_html(text)}</a>'

        await m.respond(
            mention,
            parse_mode="html"
        )

        await m.delete()