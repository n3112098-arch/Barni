import json, asyncio, random, time
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from CoinX_config import TOKEN, ADMIN_ID

# --- Инициализация ---
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
DATA_FILE = "data.json"

# --- Загрузка/Сохранение ---
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- Получение игрока ---
def get_user(data, user):
    uid = str(user.id)
    if uid not in data:
        data[uid] = {
            "balance": 5000,
            "generator_level": 0,
            "last_bonus": 0,
            "username": user.username or "",
            "nick": user.first_name,
            "name": user.first_name
        }
    else:
        data[uid].setdefault("balance", 5000)
        data[uid].setdefault("generator_level", 0)
        data[uid].setdefault("last_bonus", 0)
        data[uid].setdefault("username", user.username or "")
        data[uid].setdefault("nick", user.first_name)
        data[uid].setdefault("name", user.first_name)
    return data[uid]

# --- Старт и помощь с подсказками ---
@dp.message_handler(commands=['start', 'help'])
async def start_help(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    save_data(data)

    text = f"Привет, {user['nick']}! 🎉\n\n"
    text += "Вот доступные команды:\n"
    text += "/balance — показать ваш баланс COINX\n"
    text += "/bonus — получить бонус каждые 60 минут (1000 COINX)\n"
    text += "/generator — посмотреть уровень вашего генератора COINX\n"
    text += "/buygen — купить или улучшить генератор\n"
    text += "/setnick — установить свой ник для отображения в топе и передаче COINX\n"
    text += "/give — (только админ) выдать COINX игроку по нику\n"
    text += "/top — показать топ 50 самых богатых игроков\n"
    text += "/bet — ставка на красное/чёрное, 50/50 шанс\n"
    text += "/dice — бросок костей, шанс 50/50 на указанную сумму\n"
    text += "/help — показать это сообщение с подсказками\n\n"
    text += f"Твой баланс: {user['balance']} COINX"

    await message.reply(text)

# --- Баланс ---
@dp.message_handler(commands=['balance'])
async def balance(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    await message.reply(f"Баланс {user['nick']}: {user['balance']} COINX")

# --- Бонус ---
@dp.message_handler(commands=['bonus'])
async def bonus(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    now = int(time.time())
    if now - user['last_bonus'] >= 3600:
        user['balance'] += 1000
        user['last_bonus'] = now
        save_data(data)
        await message.reply(f"Твой бонус 1000 COINX! Новый баланс: {user['balance']}")
    else:
        await message.reply("Бонус доступен каждые 60 минут!")

# --- Генератор ---
GENERATOR_CONFIG = {
    1: {"cost": 10000, "income": 20},
    2: {"cost": 15000, "income": 60},
    3: {"cost": 45000, "income": 180},
    4: {"cost": 135000, "income": 540},
    5: {"cost": 405000, "income": 1620},
    6: {"cost": 1215000, "income": 4860},
    7: {"cost": 3645000, "income": 14580},
    8: {"cost": 10935000, "income": 43740},
    9: {"cost": 32805000, "income": 131220},
    10: {"cost": 98466000, "income": 393660}
}

@dp.message_handler(commands=['generator'])
async def generator(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    await message.reply(f"Твой уровень генератора: {user['generator_level']}\nБаланс: {user['balance']} COINX")

@dp.message_handler(commands=['buygen'])
async def buygen(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    lvl = user['generator_level'] + 1
    if lvl > 10:
        await message.reply("Ты достиг максимального уровня генератора!")
        return
    cost = GENERATOR_CONFIG[lvl]["cost"]
    if user['balance'] >= cost:
        user['balance'] -= cost
        user['generator_level'] = lvl
        save_data(data)
        await message.reply(f"Ты купил генератор уровня {lvl}!")
    else:
        await message.reply(f"Не хватает COINX! Нужно {cost}")

# --- Смена ника ---
@dp.message_handler(commands=['setnick'])
async def set_nick(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Использование: /setnick <новый_ник>")
        return
    new_nick = args[1].strip()
    user["nick"] = new_nick
    save_data(data)
    await message.reply(f"Твой новый ник: {new_nick}")

# --- Передача COINX ---
@dp.message_handler(commands=['give'])
async def give(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    data = load_data()
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Использование: /give <ник> <сумма>")
        return
    target_nick = args[1].strip()
    amount = int(args[2])
    target_user = None
    for uid, u in data.items():
        if u.get("nick") == target_nick:
            target_user = u
            break
    if not target_user:
        await message.reply("Игрок не найден!")
        return
    target_user["balance"] += amount
    save_data(data)
    await message.reply(f"Выдано {amount} COINX игроку {target_nick}")

# --- Топ 50 ---
@dp.message_handler(commands=['top'])
async def top(message: types.Message):
    data = load_data()
    top_players = sorted(data.items(), key=lambda x: x[1]["balance"], reverse=True)[:50]
    text = "🏆 Топ 50 игроков:\n"
    for i, (uid, info) in enumerate(top_players, start=1):
        text += f"{i}. {info.get('nick', info.get('username','Unknown'))} — {info['balance']} COINX\n"
    await message.reply(text)

# --- Ставки на красное/чёрное ---
@dp.message_handler(commands=['bet'])
async def bet(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Использование: /bet <красное/чёрное> <сумма>")
        return
    color = args[1].lower()
    amount = int(args[2])
    if user['balance'] < amount:
        await message.reply("Недостаточно COINX!")
        return
    outcome = random.choice(["красное","чёрное"])
    if color == outcome:
        win = amount
        user['balance'] += win
        save_data(data)
        await message.reply(f"Вы выиграли {win} COINX! Выпало {outcome}")
    else:
        user['balance'] -= amount
        save_data(data)
        await message.reply(f"Вы проиграли {amount} COINX! Выпало {outcome}")

# --- Кости 50/50 ---
@dp.message_handler(commands=['dice'])
async def dice(message: types.Message):
    data = load_data()
    user = get_user(data, message.from_user)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Использование: /dice <сумма>")
        return
    try:
        amount = int(args[1])
    except:
        await message.reply("Сумма должна быть числом!")
        return
    if amount <= 0:
        await message.reply("Сумма должна быть больше нуля!")
        return
    if user['balance'] < amount:
        await message.reply("Недостаточно COINX!")
        return
    outcome = random.choice(["win", "lose"])
    if outcome == "win":
        user['balance'] += amount
        await message.reply(f"Выпало 👍 Вы выиграли {amount} COINX! Баланс: {user['balance']}")
    else:
        user['balance'] -= amount
        await message.reply(f"Выпало 👎 Вы проиграли {amount} COINX! Баланс: {user['balance']}")
    save_data(data)

# --- Фоновые задачи генератора ---
async def generator_task():
    while True:
        data = load_data()
        for uid, u in data.items():
            lvl = u.get("generator_level",0)
            if lvl > 0:
                income = GENERATOR_CONFIG[lvl]["income"]
                u["balance"] += income
        save_data(data)
        await asyncio.sleep(60)

# --- Запуск ---
async def on_startup(_):
    asyncio.create_task(generator_task())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)