# meta developer: @B_mods
from .. import loader, utils
import datetime
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

class ChatStatsMod(loader.Module):
    """Статистика чата: активность, участники, медиа"""

    strings = {"name": "ChatStats"}

    @loader.command()
    async def chatstat(self, m):
        """Собрать статистику этого чата"""
        await m.edit("📊 Собираю статистику чата...")

        chat = await m.client.get_entity(m.chat_id)
        stats = {
            "total": 0,
            "photo": 0,
            "video": 0,
            "audio": 0,
            "file": 0,
            "sticker": 0,
            "gif": 0,
            "per_user": {},
            "last24h": 0,
            "last7d": 0,
        }

        now = datetime.datetime.utcnow()
        async for msg in m.client.iter_messages(m.chat_id, limit=5000):
            stats["total"] += 1

            # ----- по пользователям -----
            uid = msg.sender_id
            if uid:
                stats["per_user"][uid] = stats["per_user"].get(uid, 0) + 1

            # ----- интервалы -----
            if msg.date > now - datetime.timedelta(days=1):
                stats["last24h"] += 1
            if msg.date > now - datetime.timedelta(days=7):
                stats["last7d"] += 1

            # ----- медиа -----
            if msg.media:
                if isinstance(msg.media, MessageMediaPhoto):
                    stats["photo"] += 1
                elif isinstance(msg.media, MessageMediaDocument):
                    if msg.file:
                        mime = msg.file.mime_type or ""
                        if "video" in mime:
                            stats["video"] += 1
                        elif "audio" in mime:
                            stats["audio"] += 1
                        elif "gif" in mime:
                            stats["gif"] += 1
                        elif "webp" in mime:
                            stats["sticker"] += 1
                        else:
                            stats["file"] += 1

        # ----- Топ пользователей -----
        top_users = sorted(
            stats["per_user"].items(), key=lambda x: x[1], reverse=True
        )[:10]

        lines = [f"📊 **Статистика чата — {chat.title}**\n"]
        lines.append(f"📨 Всего сообщений: **{stats['total']}**")
        lines.append(f"🕓 За 24 часа: **{stats['last24h']}**")
        lines.append(f"🗓 За 7 дней: **{stats['last7d']}**")
        lines.append("\n🎯 **Медиа:**")
        lines.append(f"📷 Фото: **{stats['photo']}**")
        lines.append(f"🎞 Видео: **{stats['video']}**")
        lines.append(f"🎧 Голосовые: **{stats['audio']}**")
        lines.append(f"📁 Файлы: **{stats['file']}**")
        lines.append(f"🌀 GIF: **{stats['gif']}**")
        lines.append(f"🤡 Стикеры: **{stats['sticker']}**")
        lines.append("\n🏆 **ТОП 10 участников:**")

        for uid, count in top_users:
            try:
                user = await m.client.get_entity(uid)
                name = user.first_name or "Без имени"
            except:
                name = "Неизвестно"

            percent = round(count / stats["total"] * 100, 1)
            lines.append(f"• {name}: **{count}** сообщений ({percent}%)")

        await m.edit("\n".join(lines))