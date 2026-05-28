# meta developer: [マークシャ](tg://user?id=6150422667)
# meta pic: https://img.icons8.com/fluency/48/scheduled.png
# meta banner: https://i.ibb.co/7N9k7L0/autopost-banner.png

import datetime
import asyncio
import time

from legacytl.tl.types import Message

from .. import loader, utils

# Premium Emojis (ToastEmoji pack)
E_SHIELD = "<emoji document_id=5255999175174137421>🛡</emoji>"
E_BOX = "<emoji document_id=5256094480498436162>📦</emoji>"
E_BOX2 = "<emoji document_id=5255702998524373856>📦</emoji>"
E_TIME = "<emoji document_id=5255971360965930740>🕔</emoji>"
E_OK = "<emoji document_id=5255813619702049821>✅</emoji>"
E_ERR = "<emoji document_id=5255831443816327915>🗑</emoji>"
E_INFO = "<emoji document_id=5255944749348562622>🎵</emoji>"
E_BELL = "<emoji document_id=5253884483601442590>🔔</emoji>"
E_CARD = "<emoji document_id=5255713220546538619>💳</emoji>"
E_START = "<emoji document_id=5253877736207821121>🔥</emoji>"
E_OWNER = "<emoji document_id=5255977030322760582>🫂</emoji>"


@loader.tds
class AutoPostMod(loader.Module):
    """Модуль для планирования отложенных постов по МСК (до 100 за раз)"""

    strings = {
        "name": "AutoPost",
        "planning": (
            f"{E_SHIELD} <b>Планирование запущено!</b>\n"
            f"{E_BELL} Старт (МСК): <code>{{}}</code>\n"
            f"{E_BOX} Количество: <code>{{}}</code>\n"
            f"{E_TIME} Интервал: <code>{{}} мин.</code>\n"
            f"{E_INFO} Всего: <b>{{}}</b> постов\n"
            f"{E_TIME} Финал (МСК): ≈<code>{{}}</code>"
        ),
        "success": f"{E_OK} <b>Успешно создано {{}} из {{}} постов!</b>",
        "error": f"{E_ERR} <b>Ошибка:</b>\n<code>{{}}</code>",
        "args_err": (
            f"{E_ERR} <b>Ошибка в аргументах!</b>\n\n"
            f"{E_INFO} <b>Формат:</b>\n"
            "<code>.auto [кол-во] [интервал] [ЧЧ:ММ] [текст]</code>\n"
        ),
        "limit": f"{E_ERR} <b>Слишком много!</b> Максимум 100 постов.",
        "progress": (
            f"{E_BOX2} <b>Создаю отложки...</b>\n"
            f"{E_INFO} Прогресс: <code>{{}}/{{}} ({{}}%)</code>\n"
            f"{E_TIME} Осталось: ~{{}} мин"
        ),
        "status": (
            f"{E_SHIELD} <b>AutoPost — статус</b>\n\n"
            f"{E_OWNER} Владелец: <code>{{owner_id}}</code>\n"
            f"{E_TIME} Аптайм модуля: <b>{{uptime}}</b>\n"
            f"{E_BOX} Создано за всё время: <b>{{total}}</b> постов\n"
            f"{E_INFO} Последняя задача: <b>{{last_task}}</b>"
        ),
        "logs_empty": f"{E_ERR} <b>Логи пусты.</b>",
        "logs_title": f"{E_CARD} <b>Логи отложек ({{count}})</b>",
    }

    strings_ru = {
        "name": "AutoPost",
        "planning": (
            f"{E_SHIELD} <b>Планирование запущено!</b>\n"
            f"{E_BELL} Старт (МСК): <code>{{}}</code>\n"
            f"{E_BOX} Количество: <code>{{}}</code>\n"
            f"{E_TIME} Интервал: <code>{{}} мин.</code>\n"
            f"{E_INFO} Всего: <b>{{}}</b> постов\n"
            f"{E_TIME} Финал (МСК): ≈<code>{{}}</code>"
        ),
        "success": f"{E_OK} <b>Успешно создано {{}} из {{}} постов!</b>",
        "error": f"{E_ERR} <b>Ошибка:</b>\n<code>{{}}</code>",
        "args_err": (
            f"{E_ERR} <b>Ошибка в аргументах!</b>\n\n"
            f"{E_INFO} <b>Формат:</b>\n"
            "<code>.auto [кол-во] [интервал] [ЧЧ:ММ] [текст]</code>\n"
        ),
        "limit": f"{E_ERR} <b>Слишком много!</b> Максимум 100 постов.",
        "progress": (
            f"{E_BOX2} <b>Создаю отложки...</b>\n"
            f"{E_INFO} Прогресс: <code>{{}}/{{}} ({{}}%)</code>\n"
            f"{E_TIME} Осталось: ~{{}} мин"
        ),
        "status": (
            f"{E_SHIELD} <b>AutoPost — статус</b>\n\n"
            f"{E_OWNER} Владелец: <code>{{owner_id}}</code>\n"
            f"{E_TIME} Аптайм модуля: <b>{{uptime}}</b>\n"
            f"{E_BOX} Создано за всё время: <b>{{total}}</b> постов\n"
            f"{E_INFO} Последняя задача: <b>{{last_task}}</b>"
        ),
        "logs_empty": f"{E_ERR} <b>Логи пусты.</b>",
        "logs_title": f"{E_CARD} <b>Логи отложек ({{count}})</b>",
    }

    async def client_ready(self, client, db):
        self._start_ts = time.time()
        self._logs = self._db.get(self.strings("name"), "logs", [])
        self._total_posts = self._db.get(self.strings("name"), "total_posts", 0)
        self._last_task = self._db.get(
            self.strings("name"), "last_task", "Ещё не запускалось"
        )

    def _add_log(self, text: str):
        tz_moscow = datetime.timezone(datetime.timedelta(hours=3))
        stamp = datetime.datetime.now(tz_moscow).strftime("%d.%m %H:%M:%S")
        self._logs.append(f"<code>[{stamp}]</code> {text}")
        if len(self._logs) > 50:
            self._logs = self._logs[-50:]
        self._db.set(self.strings("name"), "logs", self._logs)

    def _format_td(self, seconds: int) -> str:
        hours, rem = divmod(seconds, 3600)
        mins, secs = divmod(rem, 60)
        if hours:
            return f"{hours}ч {mins}мин"
        if mins:
            return f"{mins}мин {secs}сек"
        return f"{secs}сек"

    @loader.command(ru_doc="Запланировать посты: .auto [кол-во] [интервал] [время] [текст]")
    async def autocmd(self, message: Message):
        """Создать серию отложенных сообщений по МСК"""
        if not await self._check_owner(message):
            return

        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("args_err"))
            return

        try:
            parts = args.split(maxsplit=3)
            if len(parts) < 4:
                raise ValueError
            count, interval = int(parts[0]), int(parts[1])
            start_time_str, text = parts[2], parts[3]
        except (ValueError, IndexError):
            await utils.answer(message, self.strings("args_err"))
            return

        if count > 100:
            await utils.answer(message, self.strings("limit"))
            return

        tz_moscow = datetime.timezone(datetime.timedelta(hours=3))
        now_msk = datetime.datetime.now(tz_moscow)

        try:
            time_parts = list(map(int, start_time_str.split(":")))
            start_date = now_msk.replace(
                hour=time_parts[0],
                minute=time_parts[1],
                second=0,
                microsecond=0,
            )

            if start_date < now_msk:
                start_date += datetime.timedelta(days=1)

            final_date = start_date + datetime.timedelta(minutes=interval * (count - 1))

            planning_msg = await utils.answer(
                message,
                self.strings("planning").format(
                    start_date.strftime("%H:%M %d.%m"),
                    count,
                    interval,
                    count,
                    final_date.strftime("%H:%M %d.%m"),
                ),
            )

            current_schedule = start_date
            successful = 0

            self._add_log(
                f"{E_START} Старт генерации {count} постов (чат: {message.chat_id})"
            )

            for i in range(count):
                try:
                    current_text = text.replace("{n}", str(i + 1)).replace(
                        "{N}", str(i + 1)
                    )

                    await self._client.send_message(
                        message.chat_id,
                        current_text,
                        schedule=current_schedule,
                    )
                    successful += 1

                    if (i + 1) % 5 == 0 and i < count - 1:
                        rem_min = interval * (count - i - 1)
                        await planning_msg.edit(
                            self.strings("progress").format(
                                i + 1,
                                count,
                                round((i + 1) / count * 100),
                                rem_min,
                            )
                        )

                    current_schedule += datetime.timedelta(minutes=interval)
                    await asyncio.sleep(0.3)
                except Exception as e:
                    self._add_log(
                        f"{E_BELL} Ошибка (пост {i+1}): {str(e)[:50]}"
                    )
                    await self._client.send_message(
                        message.chat_id,
                        f"{E_BELL} Ошибка #{i+1}: {str(e)[:50]}",
                    )

            self._total_posts += successful
            self._db.set(self.strings("name"), "total_posts", self._total_posts)

            last_task_str = f"{successful} шт. до {final_date.strftime('%H:%M')}"
            self._last_task = last_task_str
            self._db.set(self.strings("name"), "last_task", self._last_task)

            self._add_log(f"{E_OK} Успешно создано {successful}/{count} постов")

            await planning_msg.edit(
                self.strings("success").format(successful, count)
                + f"\n{E_CARD} Старт: {start_date.strftime('%H:%M')}\n"
                + f"{E_TIME} Конец: {final_date.strftime('%H:%M %d.%m')}"
            )
        except Exception as e:
            self._add_log(f"{E_ERR} Критическая ошибка: {str(e)[:50]}")
            await utils.answer(message, self.strings("error").format(str(e)))

    @loader.command(ru_doc="| статус модуля AutoPost")
    async def autostatcmd(self, message: Message):
        """Показать статус модуля"""
        if not await self._check_owner(message):
            return

        uptime_str = self._format_td(int(time.time() - self._start_ts))
        text = self.strings("status").format(
            owner_id=self._client.tg_id,
            uptime=uptime_str,
            total=self._total_posts,
            last_task=self._last_task,
        )
        await utils.answer(message, text)

    @loader.command(ru_doc="| логи отложек")
    async def autologscmd(self, message: Message):
        """Показать последние 20 логов модуля"""
        if not await self._check_owner(message):
            return

        if not self._logs:
            await utils.answer(message, self.strings("logs_empty"))
            return

        logs_text = "\n".join(self._logs[-20:])
        out_text = (
            f"{self.strings('logs_title').format(count=len(self._logs))}\n\n{logs_text}"
        )

        await utils.answer(message, out_text)

    async def _check_owner(self, message: Message) -> bool:
        """Проверка, что команду вызвал владелец"""
        if getattr(message, "from_id", None) and hasattr(message.from_id, "user_id"):
            user_id = message.from_id.user_id
        else:
            user_id = getattr(message, "sender_id", None) or message.from_id

        if user_id != self._client.tg_id:
            return False
        return True
