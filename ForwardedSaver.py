from .. import loader, utils
import asyncio

@loader.tds
class ForwardedSaver(loader.Module):
    """Пересылает все пересланные сообщения в Избранное"""
    strings = {"name": "ForwardedSaver"}

    async def client_ready(self, client, db):
        self.client = client
        self.active_chats = set()  # для watcher

    @loader.command()
    async def fwdall(self, m):
        """Пробегает по истории и пересылает все пересланные сообщения"""
        await m.edit("🔄 Идёт проверка истории...")
        count = 0
        async for msg in m.client.iter_messages(m.chat_id):
            if msg.forward:
                try:
                    await m.client.send_message("me", msg)
                    count += 1
                    await asyncio.sleep(0.05)
                except:
                    pass
        await m.edit(f"✅ Переслано сообщений: {count}")

    @loader.command()
    async def fwdstart(self, m):
        """Включает автоматическую пересылку новых пересланных сообщений"""
        self.active_chats.add(m.chat_id)
        await m.edit("▶️ Автопересылка включена")

    @loader.command()
    async def fwdstop(self, m):
        """Отключает автоматическую пересылку"""
        self.active_chats.discard(m.chat_id)
        await m.edit("⏹ Автопересылка выключена")

    async def watcher(self, m):
        if not m.sender_id or not m.chat:
            return
        if m.chat_id not in self.active_chats:
            return
        if m.forward:
            try:
                await self.client.send_message("me", m)
            except:
                pass
