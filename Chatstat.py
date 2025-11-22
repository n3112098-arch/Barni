# meta developer: @B_Mods
from .. import loader, utils
import datetime
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

class ChatStatsMod(loader.Module):
    """статистика чата: фото, гиф, стикеры, медиа, сообщения"""

    strings = {"name": "ChatStats"}

    def _normalize_dt(self, dt):
        if not dt:
            return None
        if dt.tzinfo:
            return dt.astimezone(datetime.timezone.utc)
        return dt.replace(tzinfo=datetime.timezone.utc)

    @loader.command()
    async def chatstat(self, m):
        """Показать статистику чата"""
        await m.edit("📊 Собираю статистику...")

        now = datetime.datetime.now(datetime.timezone.utc)

        stats = {
            "total": 0,
            "photo": 0,
            "video": 0,
            "audio": 0,
            "file": 0,
            "sticker": 0,
            "gif": 0,
            "last24h": 0,
            "last7d": 0,
        }

        # читаем последние 3000 сообщений
        async for msg in m.client.iter_messages(m.chat_id, limit=20000):
            if not msg:
                continue

            stats["total"] += 1

            # дата
            msg_dt = self._normalize_dt(msg.date)

            if msg_dt:
                if msg_dt > now - datetime.timedelta(days=1):
                    stats["last24h"] += 1
                if msg_dt > now - datetime.timedelta(days=7):
                    stats["last7d"] += 1

            # медиа
            if msg.media:
                if isinstance(msg.media, MessageMediaPhoto):
                    stats["photo"] += 1

                elif isinstance(msg.media, MessageMediaDocument):
                    if msg.file:
                        mime = (msg.file.mime_type or "").lower()

                        if "video" in mime:
                            stats["video"] += 1
                        elif "audio" in mime or "voice" in mime:
                            stats["audio"] += 1
                        elif "gif" in mime:
                            stats["gif"] += 1
                        elif "webp" in mime:
                            stats["sticker"] += 1
                        else:
                            stats["file"] += 1
                    else:
                        stats["file"] += 1

        text = (
            f"📊 Статистика чата\n\n"
            f"📨 Сообщений: {stats['total']}\n"
            f"🕓 За 24ч: {stats['last24h']}\n"
            f"🗓 За 7 дней: {stats['last7d']}\n\n"
            f"📷 Фото: {stats['photo']}\n"
            f"🌀 GIF: {stats['gif']}\n"
            f"🤡 Стикеры: {stats['sticker']}\n"
            f"🎞 Видео: {stats['video']}\n"
            f"🎧 Голосовые: {stats['audio']}\n"
            f"📁 Файлы: {stats['file']}"
        )

        await m.edit(text)