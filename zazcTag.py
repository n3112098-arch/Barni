# meta developer: @B_Mods

from .. import loader, utils


class ZazcTag(loader.Module):
    """Скрытая отметка пользователя по приписке"""
    strings = {"name": "ZazcTag"}

    @loader.command()
    async def zazc(self, m):
        """
         @user Текст
        или ответом: .zazc Текст
        """

        args = utils.get_args_raw(m)

        # === ЕСЛИ ОТВЕТОМ ===
        if m.is_reply:
            reply = await m.get_reply_message()
            user = reply.sender
            text = args

        # === ЕСЛИ ЧЕРЕЗ @user ===
        else:
            if not args or len(args.split()) < 2:
                return await m.edit("❌ Использование:\n.zazc @user текст")

            user_arg, text = args.split(" ", 1)

            try:
                user = await m.client.get_entity(user_arg)
            except:
                return await m.edit("❌ Не удалось получить пользователя")

        if not user or not text:
            return await m.edit("❌ Ошибка данных")

        mention = (
            f'<a href="tg://user?id={user.id}">'
            f'{utils.escape_html(text)}'
            f'</a>'
        )

        await m.respond(mention, parse_mode="html")
        await m.delete()