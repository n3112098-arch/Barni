# meta developer: @B_Mods
"""
Impersonator — создаёт картинку с фейковым сообщением (как будто от другого пользователя).
Безопасно: это изображение, а не реальное сообщение от чужого аккаунта.
Команды:
    .fake <user> <text>   - сгенерировать картинку, где имя/ника берет из <user>
    .fakeq <text>         - ответом на сообщение: взять имя/аватар из reply и вставить <text>
"""

from .. import loader, utils
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io, base64, textwrap, asyncio

# --- компактный встроенный шрифт (поддержка кириллицы может быть ограничена) ---
FONT_B64 = b"""
AAEAAAASAQAABAAgR0RFRrRCsIIAAjWsAAACYkdQT1P/////AAO0AAAAFGNtYXAA
AAAAAAADsAAAACBnbHlm6rxeVQAAAxgAAA5laGVhZP////8AAAMQAAAANmhoZWEE
/////wAAAyQAAAAkaG10eP////8AAAOsAAAAGGxvY2EAAAAAAAADqAAAAAxtYXhw
AAAAgAAABOQAAAAgbmFtZf////8AAATYAAACaHBvc3T/////AAAFBAAAAChwcmVw
AAAAAAAFBAAAACR2dW5pAAABAAAAAQAAAAMAAAAA/wABAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAA==
"""

def _get_fonts():
    try:
        b = io.BytesIO(base64.b64decode(FONT_B64))
        big = ImageFont.truetype(b, 36)
        b2 = io.BytesIO(base64.b64decode(FONT_B64))
        small = ImageFont.truetype(b2, 20)
        return big, small
    except Exception:
        return ImageFont.load_default(), ImageFont.load_default()

BIG_FONT, SMALL_FONT = _get_fonts()

@loader.tds
class Impersonator(loader.Module):
    """Создаёт изображение с фейковым сообщением"""
    strings = {"name": "Impersonator"}

    async def _make_card(self, name, status_text, message_text, avatar_bytes=None):
        # Базовые размеры
        width = 860
        # рассчитываем высоту по объёму текста
        wrap_chars = 48  # приблизительная ширина для переноса
        lines = []
        for paragraph in message_text.splitlines():
            lines += textwrap.wrap(paragraph, wrap_chars) or [""]

        text_height = max(120, 40 + len(lines) * 30)
        height = 160 + text_height

        # холст
        img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)

        # фон карточки (бледно-серый)
        draw.rectangle([(10, 10), (width-10, height-10)], fill=(249, 249, 249), outline=(230,230,230))

        # аватар
        avatar_size = 80
        av_x, av_y = 30, 25
        if avatar_bytes:
            try:
                av = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
                av = av.resize((avatar_size, avatar_size))
                # округляем аватар
                mask = Image.new("L", (avatar_size, avatar_size), 0)
                mdraw = ImageDraw.Draw(mask)
                mdraw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                avatar = Image.new("RGBA", (avatar_size, avatar_size), (255,255,255,0))
                avatar.paste(av, (0,0), av)
                avatar = ImageOps.fit(avatar, (avatar_size, avatar_size))
                img.paste(avatar, (av_x, av_y), mask)
            except Exception:
                # если аватар не загрузился — рисуем серый круг
                draw.ellipse((av_x, av_y, av_x+avatar_size, av_y+avatar_size), fill=(200,200,200))
        else:
            draw.ellipse((av_x, av_y, av_x+avatar_size, av_y+avatar_size), fill=(200,200,200))

        # имя и статус
        name_x = av_x + avatar_size + 20
        name_y = av_y + 4
        try:
            draw.text((name_x, name_y), name, font=BIG_FONT, fill=(24,24,24))
        except Exception:
            draw.text((name_x, name_y), name, fill=(24,24,24))

        try:
            draw.text((name_x, name_y+40), status_text, font=SMALL_FONT, fill=(120,120,120))
        except Exception:
            draw.text((name_x, name_y+40), status_text, fill=(120,120,120))

        # сообщение — текстный блок
        text_x = 30
        text_y = av_y + avatar_size + 20
        bubble_x0 = 30
        bubble_x1 = width - 30
        bubble_y0 = text_y - 10
        bubble_y1 = text_y + text_height - 20
        # фон пузыря
        draw.rectangle((bubble_x0, bubble_y0, bubble_x1, bubble_y1), fill=(255,255,255), outline=(230,230,230))
        # отрисовка текста построчно
        cur_y = text_y
        for line in lines:
            try:
                draw.text((text_x+12, cur_y), line, font=SMALL_FONT, fill=(10,10,10))
            except Exception:
                draw.text((text_x+12, cur_y), line, fill=(10,10,10))
            cur_y += 28

        # мелкая подпись справа (время/иконка)
        try:
            draw.text((width-200, bubble_y1+5), "Telegram · сейчас", font=SMALL_FONT, fill=(140,140,140))
        except Exception:
            draw.text((width-200, bubble_y1+5), "Telegram · сейчас", fill=(140,140,140))

        # сохранение в BytesIO
        out = io.BytesIO()
        out.name = "fake_message.png"
        img.save(out, "PNG")
        out.seek(0)
        return out

    # ---- .fake <user> <text>
    @loader.command()
    async def fake(self, m):
        """.fake <user> <text> — создать фейковое сообщение от <user>"""
        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Использование: .fake @user Текст сообщения")

        parts = args.split(" ", 1)
        if len(parts) < 2:
            return await m.edit("Нужно: .fake <user> <текст>")

        user_ident, text = parts[0], parts[1]
        await m.edit("🔧 Генерирую картинку...")

        # пытаемся получить entity (имя/аватар)
        avatar_bytes = None
        name = user_ident
        try:
            ent = await m.client.get_entity(user_ident)
            name = ent.first_name or getattr(ent, "username", user_ident)
            try:
                avatar_bytes = await m.client.download_profile_photo(ent, bytes)
            except Exception:
                avatar_bytes = None
        except Exception:
            # если не удалось получить — оставляем как текст
            pass

        card = await self._make_card(name, "в сети недавно", text, avatar_bytes)
        await m.client.send_file(m.chat_id, card)
        try:
            await m.delete()
        except:
            pass

    # ---- .fakeq <text> (reply)
    @loader.command()
    async def fakeq(self, m):
        """.fakeq <text> — ответом на сообщение: создать фейк от автора reply"""
        if not m.is_reply:
            return await m.edit("Ответь на сообщение, чтобы использовать .fakeq")

        args = utils.get_args_raw(m)
        if not args:
            return await m.edit("Напиши текст сообщения для фейка")

        reply = await m.get_reply_message()
        if not reply or not reply.sender:
            return await m.edit("Не удалось получить автора reply")

        ent = reply.sender
        name = ent.first_name or getattr(ent, "username", str(ent.id))
        avatar_bytes = None
        try:
            avatar_bytes = await m.client.download_profile_photo(ent, bytes)
        except Exception:
            avatar_bytes = None

        await m.edit("🔧 Генерирую картинку...")
        card = await self._make_card(name, "в сети недавно", args, avatar_bytes)
        await m.client.send_file(m.chat_id, card)
        try:
            await m.delete()
        except:
            pass