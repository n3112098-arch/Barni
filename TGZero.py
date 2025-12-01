# meta developer: @B_Mods

from .. import loader, utils
import asyncio
from telethon.tl.types import Channel, Chat, User

class TGZero(loader.Module):
    """Полная очистка аккаунта: удаление всех диалогов, кроме избранного и твоих проектов"""

    strings = {"name": "TGZero"}

    def __init__(self):
        self.stop_flag = False

    async def iter_chats(self, client):
        async for dialog in client.iter_dialogs():
            entity = dialog.entity

            # Пропускаем избранное
            if entity.id == (await client.get_me()).id:
                continue

            # Пропускаем собственные каналы/группы
            if isinstance(entity, (Channel, Chat)) and getattr(entity, "creator", False):
                continue

            yield dialog

    @loader.command()
    async def cleartest(self, m):
        """Показать, что будет удалено"""
        me = await m.client.get_me()
        msg = "🧪 *Тест очистки:*\n\nБудет удалено:\n"

        async for dialog in self.iter_chats(m.client):
            entity = dialog.entity
            if isinstance(entity, User):
                msg += f"👤 Диалог с пользователем: {entity.first_name}\n"
            elif isinstance(entity, Channel):
                msg += f"📢 Канал: {entity.title}\n"
            elif isinstance(entity, Chat):
                msg += f"👥 Группа: {entity.title}\n"

        await m.edit(msg or "Нечего удалять.")

    @loader.command()
    async def clearstop(self, m):
        """Остановить очистку"""
        self.stop_flag = True
        await m.edit("⛔ Очистка остановлена!")

    @loader.command()
    async def clearakk(self, m):
        """Полная очистка аккаунта TGZero"""
        self.stop_flag = False
        await m.edit("🧹 *Запуск TGZero...*\nУдаляем всё, кроме избранного и твоих проектов.")

        count = 0

        # Перебираем диалоги
        async for dialog in self.iter_chats(m.client):
            if self.stop_flag:
                return await m.edit(f"⛔ Очистка остановлена!\nУдалено: {count}")

            entity = dialog.entity

            try:
                # Каналы/группы — выходим + удаляем чат
                if isinstance(entity, (Channel, Chat)):
                    await m.client.delete_dialog(entity.id)
                else:
                    # Обычные чаты — удаляем переписку
                    await m.client.delete_dialog(entity.id)

                count += 1
                await asyncio.sleep(0.2)

            except Exception as e:
                pass

        await m.edit(f"✔️ TGZero завершён.\nУдалено: {count}")