# meta developer: @B_Mods

from .. import loader, utils
from telethon.tl.types import MessageEntityMentionName


class ZazcTag(loader.Module):
    """Отметка человека по своей приписке
    разработчик:@B_Mods"""
    strings = {"name": "ZazcTag"}

    @loader.command()
    async def zazc(self, m):
        """
        .zazc @user Текст — отметить человека по своей приписке
        Можно отвечать на сообщение без @user
        """

        args = utils.get_args_raw(m)

        # Если ответом
        if m.is_reply:
            user = (await m.get_reply_message()).sender
            text = args
        else:
            if not args or len(args.split()) < 2:
                return await m.edit("❌ Использование:\n.zazc @user текст")

            user = await utils.get_user(m)
            text = args.split(" ", 1)[1]

        if not user:
            return await m.edit("❌ Не удалось получить пользователя")

        entity = MessageEntityMentionName(
            offset=0,
            length=len(text),
            user_id=user.id
        )

        await m.client.send_message(
            m.chat_id,
            text,
            entities=[entity]
        )

        await m.delete()