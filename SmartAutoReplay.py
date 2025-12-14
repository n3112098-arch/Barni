# meta developer: @B_Mods
from .. import loader, utils
import random
import re


@loader.tds
class DialogGhost(loader.Module):
    """Умный авто-ответчик 
    Разработчик:@B_Mods"""
    strings = {"name": "SmartReplay"}

    async def client_ready(self, client, db):
        self.client = client
        self.targets = {}     # user_id -> True
        self.counters = {}    # user_id -> msg count

        # ❌ чёрный список
        self.blacklist = {
            "Го", "spam", "http", "https"
        }

        # 🤖 собственные фразы
        self.self_phrases = {
            "hi": ["привет", "хай", "здарова"],
            "bye": ["пока", "давай", "Ебал", "Шлюха", "Мать", "Твоя", "Убил", "увидимся"],
            "question": [
                "хз если честно",
                "сложно сказать",
                "а ты как думаешь?",
                "не уверен"
                "Дочь шлбхи"
                "Сын хуйни"
                "Сын шлюхи"
                "Ебал твою мать"
                "Твоя мать шлюха"
            ],
            "short": ["ага", "понял", "ясно", "ок"],
            "long": [
                "ну тут всё не так просто",
                "думаю зависит от ситуации",
                "есть разные варианты"
            ]
        }

    # ========= КОМАНДЫ =========

    @loader.command()
    async def reps(self, m):
        """ <user> — начать имитацию"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("❌ Укажи пользователя: @username")

        try:
            user = await m.client.get_entity(args)
        except:
            return await m.edit("❌ Пользователь не найден")

        if user.bot:
            return await m.edit("❌ Боты не поддерживаются")

        self.targets[user.id] = True
        self.counters[user.id] = 0

        await m.edit(f"SmartAutoReplay активирован для {user.first_name}")

    @loader.command()
    async def repsstop(self, m):
        """ <user> — остановить"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("❌ Укажи пользователя: @username")

        try:
            user = await m.client.get_entity(args)
        except:
            return await m.edit("❌ Пользователь не найден")

        self.targets.pop(user.id, None)
        self.counters.pop(user.id, None)

        await m.edit(f"🛑 DialogGhost остановлен для {user.first_name}")

    # ========= WATCHER =========

    async def watcher(self, m):
        if not m.sender_id or not m.text:
            return

        uid = m.sender_id
        if uid not in self.targets:
            return

        sender = await m.get_sender()
        if sender.bot:
            return

        text = m.text.lower()

        # ❌ чёрный список
        for bad in self.blacklist:
            if bad in text:
                return

        # считаем сообщения
        self.counters[uid] += 1

        # ❗ НЕ отвечаем на первое
        min_limit = 2
        max_limit = 4
        limit = random.randint(min_limit, max_limit)

        if self.counters[uid] < limit:
            return

        # сбрасываем счётчик
        self.counters[uid] = 0

        reply = await self.pick_reply(m, text)
        if not reply:
            return

        try:
            await m.reply(reply)
        except:
            pass

    # ========= ЛОГИКА =========

    async def pick_reply(self, m, text):
        # вопрос
        if "?" in text:
            return self.smart_mix("question")

        # привет
        if re.search(r"\b(привет|хай|hello|hi)\b", text):
            return self.smart_mix("hi")

        # короткое
        if len(text.split()) <= 2:
            return self.smart_mix("short")

        # длинное
        if len(text.split()) >= 6:
            return self.smart_mix("long")

        # берём из чата
        try:
            msgs = await self.client.get_messages(m.chat_id, limit=50)
            candidates = [
                msg.text for msg in msgs
                if msg.text
                and msg.sender_id != m.sender_id
                and not any(b in msg.text.lower() for b in self.blacklist)
            ]
            if candidates:
                return random.choice(candidates)
        except:
            pass

        return None

    def smart_mix(self, key):
        pool = self.self_phrases.get(key, [])
        return random.choice(pool) if pool else None