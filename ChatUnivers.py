# meta developer: @B_Mods

from .. import loader, utils
from telethon.tl.types import Message
import asyncio


class ChatUnivers(loader.Module):
    """ChatUnivers — универсальное сохранение контента"""
    strings = {"name": "ChatUnivers"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.auto_forward = False
        self.stop_all = False

    # ===== ПЕРЕСЛАННЫЕ =====

    @loader.command()
    async def sf(self, m):
        """Сохранить все пересланные сообщения"""
        self.stop_all = False
        await m.edit("🔍 Ищу пересланные сообщения...")
        count = 0

        async for msg in self.client.iter_messages(m.chat_id):
            if self.stop_all:
                return await m.edit("⛔ Операция остановлена")

            if msg.fwd_from:
                await self.client.send_message("me", msg)
                count += 1
                await asyncio.sleep(0.05)

        await m.edit(f"✅ Пересланных сохранено: {count}")

    @loader.command()
    async def sfon(self, m):
        """Включить автосохранение пересланных"""
        self.auto_forward = True
        self.stop_all = False
        await m.edit("🟢 Автосохранение включено")

    @loader.command()
    async def sfoff(self, m):
        """Выключить автосохранение"""
        self.auto_forward = False
        await m.edit("🔴 Автосохранение выключено")

    # ===== МЕДИА =====

    @loader.command()
    async def sp(self, m):
        """Сохранить все ФОТО"""
        await self._save_media(m, "photo")

    @loader.command()
    async def sv(self, m):
        """Сохранить все ВИДЕО"""
        await self._save_media(m, "video")

    @loader.command()
    async def svo(self, m):
        """Сохранить все ГОЛОСОВЫЕ"""
        await self._save_media(m, "voice")

    @loader.command()
    async def sn(self, m):
        """Сохранить все КРУЖКИ"""
        await self._save_media(m, "round")

    async def _save_media(self, m, mode):
        self.stop_all = False
        await m.edit("⏳ Сканирую сообщения...")
        count = 0

        async for msg in self.client.iter_messages(m.chat_id):
            if self.stop_all:
                return await m.edit("⛔ Операция остановлена")

            try:
                if mode == "photo" and msg.photo:
                    await self.client.send_message("me", msg)
                elif mode == "video" and msg.video:
                    await self.client.send_message("me", msg)
                elif mode == "voice" and msg.voice:
                    await self.client.send_message("me", msg)
                elif mode == "round" and msg.video_note:
                    await self.client.send_message("me", msg)
                else:
                    continue

                count += 1
                await asyncio.sleep(0.05)
            except:
                pass

        await m.edit(f"✅ Сохранено: {count}")

    # ===== СТОП ВСЕГО =====

    @loader.command()
    async def sstop(self, m):
        """Остановить все действия"""
        self.stop_all = True
        self.auto_forward = False
        await m.edit("🛑 Все операции остановлены")

    # ===== WATCHER =====

    async def watcher(self, m: Message):
        if self.stop_all or not self.auto_forward:
            return

        if m.fwd_from:
            try:
                await self.client.send_message("me", m)
            except:
                pass