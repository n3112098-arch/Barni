# meta developer: @B_Mods
from .. import loader
import datetime


@loader.tds
class ForwardSaver(loader.Module):
    """Сохраняет ТОЛЬКО новые пересланные сообщения из ЛС в Избранные"""
    strings = {"name": "ForwardSaver"}

    async def client_ready(self, client, db):
        self.client = client
        # момент запуска модуля
        self.started_at = datetime.datetime.now(datetime.timezone.utc)

    async def watcher(self, m):
        # только ЛС
        if not m or not m.is_private:
            return

        # не свои сообщения
        if m.out:
            return

        # только пересланные
        if not m.fwd_from:
            return

        # ❗ игнорируем всё, что было ДО запуска модуля
        if not m.date or m.date <= self.started_at:
            return

        try:
            await m.forward_to("me")  # Избранные
        except:
            pass
