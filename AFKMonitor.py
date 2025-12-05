# meta developer: @B_Mods
from .. import loader, utils
import asyncio
import datetime
from telethon.tl.types import UserStatusOffline, UserStatusOnline
from telethon.errors import RPCError

@loader.tds
class AFKMonitor(loader.Module):
    """AFKMonitor — мониторинг online/offline пользователя и лог в 'Избранное'"""
    strings = {"name": "AFKMonitor"}

    def __init__(self):
        # {target_id: {"task": asyncio.Task, "state": {...}}}
        self._monitors = {}
        self._interval = 15  # сек между проверками (можно изменить)

    # ---------- вспомогательные форматеры ----------
    def _now(self):
        return datetime.datetime.now()

    def _fmt_time(self, dt: datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def _sec_to_human(self, s: float):
        s = int(s)
        h, s = divmod(s, 3600)
        m, s = divmod(s, 60)
        parts = []
        if h: parts.append(f"{h}h")
        if m: parts.append(f"{m}m")
        parts.append(f"{s}s")
        return " ".join(parts)

    # ---------- команда старта ----------
    @loader.command()
    async def rad(self, m):
        """
        .rad <user|id> — начать мониторинг пользователя (лог в Избранное)
        Работает только если у пользователя видим last seen.
        """
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Использование: .rad <юзер/айди> (например .rad @username)")

        await m.edit("🔎 Попытка запустить мониторинг...")

        try:
            ent = await m.client.get_entity(args)
        except Exception:
            return await m.edit("❌ Не удалось получить пользователя. Проверь ник/ID.")

        # проверка видимости last seen — работаем только если статус ONLINE или OFFLINE (точное время)
        status = getattr(ent, "status", None)
        if not isinstance(status, (UserStatusOnline, UserStatusOffline)):
            return await m.edit("⚠️ У этого пользователя скрыт/нет точного last seen — мониторинг невозможен.")

        target_id = ent.id
        if target_id in self._monitors:
            return await m.edit("ℹ️ Мониторинг для этого пользователя уже запущен.")

        # стартуем задачу
        task = asyncio.create_task(self._monitor_loop(m.client, ent, m))
        self._monitors[target_id] = {"task": task, "entity": ent}
        await m.edit(f"✅ Мониторинг запущен для: {ent.first_name or ent.username or target_id}\nКоманда для остановки: .radstop")

    # ---------- команда стопа ----------
    @loader.command()
    async def radstop(self, m):
        """
        .radstop — остановить все запущенные мониторинги
        """
        if not self._monitors:
            return await m.edit("ℹ️ Нет активных мониторингов.")

        # отменяем все таски
        stopped = 0
        for tid, info in list(self._monitors.items()):
            task = info.get("task")
            if task and not task.done():
                task.cancel()
            self._monitors.pop(tid, None)
            stopped += 1

        await m.edit(f"⛔ Остановлено мониторингов: {stopped}")

    # ---------- основной цикл мониторинга ----------
    async def _monitor_loop(self, client, ent, m):
        """
        Цикл: каждые self._interval сек запрашиваем статус пользователя.
        Логируем в 'Избранное' события: вошёл/вышел + длительности.
        """
        target_id = ent.id
        name = ent.username or ent.first_name or str(target_id)
        saved = "me"  # отправка в Избранное

        # состояние:
        state = {
            "last_online": None,     # datetime когда стал online
            "last_offline": None,    # datetime когда стал offline
            "is_online": isinstance(getattr(ent, "status", None), UserStatusOnline)
        }

        # начальное уведомление
        try:
            await client.send_message(saved,
                f"[AFKMonitor] Запущен мониторинг: {name}\nВремя старта: {self._fmt_time(self._now())}"
            )
        except RPCError:
            # если не получилось отправить в Saved Messages, всё равно продолжаем
            pass

        try:
            # если изначально online — запишем начало
            if state["is_online"]:
                state["last_online"] = self._now()
                try:
                    await client.send_message(saved,
                        f"[AFKMonitor] {name} уже ONLINE в момент старта: {self._fmt_time(state['last_online'])}"
                    )
                except RPCError:
                    pass

            while True:
                # обновляем entity — получаем актуальный статус
                try:
                    cur = await client.get_entity(target_id)
                except Exception:
                    # не можем получить пользователя — ждём и повторим
                    await asyncio.sleep(self._interval)
                    continue

                cur_status = getattr(cur, "status", None)
                is_online_now = isinstance(cur_status, UserStatusOnline)

                # переход Offline -> Online
                if not state["is_online"] and is_online_now:
                    now = self._now()
                    state["is_online"] = True
                    state["last_online"] = now
                    # если был время оффлай — посчитаем длительность оффлай
                    offline_since = state.get("last_offline")
                    offline_msg = ""
                    if offline_since:
                        offline_dur = (now - offline_since).total_seconds()
                        offline_msg = f"\nOffline duration: {self._sec_to_human(offline_dur)}"
                    text = (
                        f"[AFKMonitor] {name} → ONLINE\n"
                        f"Time: {self._fmt_time(now)}{offline_msg}"
                    )
                    try:
                        await client.send_message(saved, text)
                    except RPCError:
                        pass

                # переход Online -> Offline
                if state["is_online"] and not is_online_now:
                    now = self._now()
                    state["is_online"] = False
                    state["last_offline"] = now
                    online_since = state.get("last_online")
                    online_msg = ""
                    if online_since:
                        online_dur = (now - online_since).total_seconds()
                        online_msg = f"\nOnline duration: {self._sec_to_human(online_dur)}"
                    text = (
                        f"[AFKMonitor] {name} → OFFLINE\n"
                        f"Time: {self._fmt_time(now)}{online_msg}"
                    )
                    try:
                        await client.send_message(saved, text)
                    except RPCError:
                        pass

                # обновляем состояние на всякий случай (если не менялось, просто продолжаем)
                state["is_online"] = is_online_now

                await asyncio.sleep(self._interval)

        except asyncio.CancelledError:
            # при отмене задачи шлём сообщение в Избранное
            try:
                await client.send_message(saved, f"[AFKMonitor] Мониторинг {name} остановлен.")
            except RPCError:
                pass
            return
        except Exception as e:
            try:
                await client.send_message(saved, f"[AFKMonitor] Ошибка мониторинга {name}: {e}")
            except RPCError:
                pass
            return