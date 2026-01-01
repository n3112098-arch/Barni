from .. import loader, utils
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.types import InputPeerNotifySettings

class OnlyPM(loader.Module):
    """🔇 Отключает все группы и каналы, оставляя только ЛС"""
    strings = {"name": "OnlyPM"}

    async def mute_all(self):
        async for dialog in self.client.iter_dialogs():
            if dialog.is_user:
                continue  # ЛС не трогаем

            try:
                await self.client(
                    UpdateNotifySettingsRequest(
                        peer=dialog.entity,
                        settings=InputPeerNotifySettings(
                            mute_until=2**31
                        )
                    )
                )
            except:
                continue

    async def unmute_all(self):
        async for dialog in self.client.iter_dialogs():
            try:
                await self.client(
                    UpdateNotifySettingsRequest(
                        peer=dialog.entity,
                        settings=InputPeerNotifySettings(
                            mute_until=0
                        )
                    )
                )
            except:
                continue

    @loader.command()
    async def onlypm(self, m):
        """🔇 Отключить все группы и каналы"""
        await m.edit("🔕 Отключаю все группы и каналы...")
        await self.mute_all()
        await m.edit("✅ Теперь включены только личные сообщения")

    @loader.command()
    async def onlypmoff(self, m):
        """🔔 Включить обратно уведомления"""
        await m.edit("🔔 Возвращаю уведомления...")
        await self.unmute_all()
        await m.edit("✅ Уведомления восстановлены")