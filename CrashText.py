from .. import loader, utils
import random

@loader.tds
class CrashText(loader.Module):
    """Генератор краш-текста (Zalgo / Lag Text)"""
    strings = {"name": "CrashText"}

    zalgo_up = [
        '̍','̎','̄','̅','̿','̑','̆','̐','͒','͗','͑','̇','̈','̊','͂',
        '̓','̈','͊','͋','͌','̃','̂','̌','͐','̀','́','̋','̏','̒','̓','̔','̽','̉','ͣ',
        'ͤ','ͥ','ͦ','ͧ','ͨ','ͩ','ͪ','ͫ','ͬ','ͭ','ͮ','ͯ','̾','͛','͆','̚'
    ]
    zalgo_down = [
        '̖','̗','̘','̙','̜','̝','̞','̟','̠','̤','̥','̦','̩','̪','̫','̬','̭','̮','̯','̰',
        '̱','̲','̳','̹','̺','̻','̼','ͅ','͇','͈','͉','͍','͎','͓','͔','͕','͚'
    ]
    zalgo_mid = [
        '̕','̛','̀','́','͘','̡','̢','̧','̨','̴','̵','̶','͜','͝','͞','͟','͠','͢','̸','̷','͡'
    ]

    def zalgo(self, text):
        out = ""
        for c in text:
            out += c
            for _ in range(random.randint(8, 25)):
                out += random.choice(self.zalgo_up + self.zalgo_down + self.zalgo_mid)
        return out

    @loader.command()
    async def crash(self, m):
        """
        .crash <текст> — создаёт краш-текст (лаг-текст)
        """
        text = utils.get_args_raw(m)
        if not text:
            return await m.edit("Напиши текст: .crash <слово>")

        zalgo_text = self.zalgo(text)
        await m.edit(zalgo_text)
