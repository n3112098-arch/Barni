# meta developer: @B_Mods
from .. import loader, utils
import random
import asyncio

AI_BOT = "@jadvebot"

SYSTEM_PROMPT = (
    "Отвечай как живой человек. "
    "Можно быть язвительным, токсичным, саркастичным. "
    "Допускаются грубые выражения. "
    "Не упоминай, что ты ИИ или бот. "
    "Пиши коротко и естественно.\n\n"
    "Сообщение:"
)

@loader.tds
class GhostTalk(loader.Module):
    """Скрытая ИИ-общалка через Telegram-бота"""
    strings = {"name": "GhostTalk"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}     # user_id -> counter

    # ===== ВКЛЮЧИТЬ =====
    @loader.command()
    async def ai(self, m):
        """@user — включить ИИ-общение"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        if user.bot:
            return await m.edit("❌ Ботам не отвечаю")

        self.targets[user.id] = 0
        await m.edit(f"🧠 ИИ-общение включено для **{user.first_name}**")

    # ===== ВЫКЛЮЧИТЬ =====
    @loader.command()
    async def aistop(self, m):
        """@user — выключить ИИ"""
        user = await utils.get_user(m)
        if not user:
            return await m.edit("❌ Укажи пользователя")

        self.targets.pop(user.id, None)
        await m.edit(f"🛑 ИИ-общение остановлено для **{user.first_name}**")

    # ===== СТАТУС =====
    @loader.command()
    async def aistatus(self, m):
        """Показать активные диалоги"""
        if not self.targets:
            return await m.edit("❌ ИИ ни с кем не активен")

        txt = "🧠 **Активные диалоги:**\n"
        for uid in self.targets:
            txt += f"• `{uid}`\n"

        await m.edit(txt)

    # ===== ЛОВИМ СООБЩЕНИЯ =====
    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return

        uid = m.sender_id

        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        # увеличиваем счётчик
        self.targets[uid] += 1

        # не отвечаем на первое сообщение
        if self.targets[uid] == 1:
            return

        # если не реплай — отвечаем рандомно (2–3)
        if not m.is_reply:
            if random.randint(2, 3) != self.targets[uid]:
                return

        # сброс счётчика
        self.targets[uid] = 0

        # формируем запрос ИИ
        prompt = SYSTEM_PROMPT + "\n" + (m.text or "")

        try:
            # отправляем боту
            sent = await self.client.send_message(AI_BOT, prompt)

            # ждём ответ
            await asyncio.sleep(2)

            responses = await self.client.get_messages(
                AI_BOT,
                limit=1,
                min_id=sent.id
            )

            if not responses:
                return

            ai_text = responses[0].text
            if not ai_text:
                return

            # отвечаем РЕПЛАЕМ
            await m.reply(ai_text)

        except Exception:
            pass
