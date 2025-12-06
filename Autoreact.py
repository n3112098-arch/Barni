# meta developer: @B_Mods
from .. import loader, utils

@loader.tds
class AutoReactMod(loader.Module):
    """Автоматические реакции на сообщения пользователей"""

    strings = {"name": "AutoReact"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # chat_id -> {user_id: emoji}
        self.db.setdefault("AutoReact", {})

    @loader.command()
    async def reak(self, m):
        """<юзер> <эмодзи> — ставить авто-реакцию """
        args = utils.get_args_raw(m).split(" ")
        if len(args) < 2:
            return await m.edit("Использование: `@user ❤️`")

        user = args[0]
        emoji = args[1]

        try:
            ent = await m.client.get_entity(user)
        except:
            return await m.edit("❌ Не удалось получить пользователя")

        chat_id = str(m.chat_id)
        uid = ent.id

        data = self.db.get("AutoReact", {})
        data.setdefault(chat_id, {})
        data[chat_id][uid] = emoji
        self.db.set("AutoReact", data)

        await m.edit(f"✅ Теперь сообщения от {ent.first_name} будут автоматически получать реакцию {emoji}")

    @loader.command()
    async def reaoff(self, m):
        """ <юзер> — отключить авто-реакции """
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Укажи пользователя: `@user`")

        try:
            ent = await m.client.get_entity(args)
        except:
            return await m.edit("❌ Не удалось получить пользователя")

        chat_id = str(m.chat_id)
        uid = ent.id

        data = self.db.get("AutoReact", {})

        if chat_id in data and uid in data[chat_id]:
            del data[chat_id][uid]
            self.db.set("AutoReact", data)
            return await m.edit(f"🟩 Авто-реакции для {ent.first_name} отключены.")

        await m.edit("Этот пользователь не был включён.")

    @loader.command()
    async def arlist(self, m):
        """Показать список авто-реакций"""
        data = self.db.get("AutoReact", {})
        chat_id = str(m.chat_id)

        if chat_id not in data or not data[chat_id]:
            return await m.edit("📭 Нет активных авто-реакций.")

        text = "📌 ктивные авто-реакции:\n\n"
        for uid, emoji in data[chat_id].items():
            try:
                user = await m.client.get_entity(uid)
                name = user.first_name
            except:
                name = "Unknown"

            text += f"• {name} — {emoji}\n"

        await m.edit(text)

    async def watcher(self, m):
        """Следит за сообщениями"""
        if not m or not m.sender_id:
            return

        data = self.db.get("AutoReact", {})
        chat_id = str(getattr(m, "chat_id", None))

        if chat_id in data and m.sender_id in data[chat_id]:
            emoji = data[chat_id][m.sender_id]

            try:
                await m.react(emoji)
            except:
                pass