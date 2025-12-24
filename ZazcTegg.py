# meta developer: @B_Mods

from .. import loader, utils
from telethon.tl.types import MessageEntityMentionName


class ZazcTag(loader.Module):
    """Скрытая отметка пользователя по своей приписке
    разработчик:@B_Mods"""
    strings = {"name": "ZazcTag"}

    @loader.command()
    async def zazc(self, m):
        """
         @user Текст — отметить человека по своей приписке
        Можно ответом на сообщение
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

        entity = MessageEntityMentionName(
            offset=0,
            length=len(text),
            user_id=user.id
        )

        await m.respond(
            text,
            entities=[entity]
        )

        await m.delete()