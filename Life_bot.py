import telebot
from telebot import types
import time
from keep_alive import keep_alive

# Настройка бота
TOKEN = 'ВАШ_ТОКЕН'
bot = telebot.TeleBot(8233581401:AAEHu3HG43lct3P4jccHksIREcGRVD3rHzg)

# "База данных" (в памяти Replit)
users = {}

# Константы игры
EDU_TIME_SECONDS = 7 * 24 * 60 * 60  # 7 реальных дней

JOBS_NO_EDU = {
    "🧹 Дворник": 1500, "📦 Курьер": 3000, "🍽 Официант": 4500, 
    "🚕 Таксист": 6000, "🏗 Грузчик": 5000, "🧼 Мойщик": 2500,
    "🛡 Охранник": 4000, "📢 Промоутер": 2000
}

JOBS_EDU = {
    "Медицинское": {"👨‍⚕️ Хирург": 25000},
    "Юридическое": {"⚖️ Адвокат": 22000},
    "IT": {"💻 Разработчик": 30000},
    "Инженерное": {"🛠 Главный инженер": 20000},
    "Экономическое": {"📊 Банкир": 21000},
    "Архитектурное": {"🏛 Архитектор": 19000}
}

# Вспомогательная функция
def get_u(uid):
    if uid not in users:
        users[uid] = {
            "money": 10000,
            "house": "Нет",
            "car": "Нет",
            "edu": None,
            "edu_finish": 0,
            "job": "Безработный"
        }
    return users[uid]

# --- КОМАНДЫ ---

@bot.message_handler(commands=['start', 'help'])
def start(m):
    get_u(m.chat.id)
    text = (
        "🎮 **ДОБРО ПОЖАЛОВАТЬ В СИМУЛЯТОР ЖИЗНИ!**\n\n"
        "🏠 /home — Купить недвижимость\n"
        "🚗 /cars — Автосалон\n"
        "🎓 /study — Поступить в университет (7 дней)\n"
        "💼 /jobs — Найти работу\n"
        "💰 /work — Отработать смену\n"
        "👤 /me — Мой профиль\n\n"
        "У тебя в кармане 10,000$. Удачи!"
    )
    bot.send_message(m.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['me'])
def profile(m):
    u = get_u(m.chat.id)
    edu_status = u['edu'] if u['edu'] else "Нет"
    
    # Проверка процесса обучения
    if u['edu_finish'] > time.time():
        rem = int((u['edu_finish'] - time.time()) / 3600)
        edu_status = f"Учится (осталось {rem} ч.)"
    elif u['edu_finish'] != 0 and u['edu_finish'] <= time.time():
        # Обучение завершено автоматически при проверке профиля
        u['edu_finish'] = 0

    msg = (f"👤 **Ваш профиль:**\n"
           f"💰 Баланс: {u['money']:,}$\n"
           f"🏠 Дом: {u['house']}\n"
           f"🚗 Авто: {u['car']}\n"
           f"🎓 Образование: {edu_status}\n"
           f"💼 Работа: {u['job']}")
    bot.send_message(m.chat.id, msg, parse_mode="Markdown")

@bot.message_handler(commands=['home'])
def home_menu(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📦 От нищих (10к-200к)", callback_data="buy_h_poor"))
    kb.add(types.InlineKeyboardButton("🏠 Средние (200к-1кк)", callback_data="buy_h_mid"))
    kb.add(types.InlineKeyboardButton("🏰 Дорогие (1кк-25кк)", callback_data="buy_h_rich"))
    bot.send_message(m.chat.id, "Выберите категорию недвижимости:", reply_markup=kb)

@bot.message_handler(commands=['cars'])
def car_menu(m):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🚲 Дешевые (20к-100к)", callback_data="buy_c_poor"))
    kb.add(types.InlineKeyboardButton("🚗 Средние (100к-500к)", callback_data="buy_c_mid"))
    kb.add(types.InlineKeyboardButton("🏎 Дорогие (500к-5кк)", callback_data="buy_c_rich"))
    bot.send_message(m.chat.id, "Выберите класс авто:", reply_markup=kb)

@bot.message_handler(commands=['study'])
def study_menu(m):
    u = get_u(m.chat.id)
    if u['edu_finish'] > time.time():
        return bot.send_message(m.chat.id, "Вы уже учитесь!")
    
    kb = types.InlineKeyboardMarkup()
    for prof in JOBS_EDU.keys():
        kb.add(types.InlineKeyboardButton(prof, callback_data=f"start_edu_{prof}"))
    bot.send_message(m.chat.id, "Выберите факультет (обучение 7 реальных дней):", reply_markup=kb)

@bot.message_handler(commands=['jobs'])
def jobs_menu(m):
    u = get_u(m.chat.id)
    kb = types.InlineKeyboardMarkup()
    
    # Работы без образования
    for j, pay in JOBS_NO_EDU.items():
        kb.add(types.InlineKeyboardButton(f"{j} ({pay}$)", callback_data=f"set_job_{j}"))
    
    # Проверка образования для спец.работ
    if u['edu'] in JOBS_EDU:
        for j, pay in JOBS_EDU[u['edu']].items():
            kb.add(types.InlineKeyboardButton(f"{j} ({pay}$)", callback_data=f"set_job_{j}"))
    
    bot.send_message(m.chat.id, "Выберите вакансию:", reply_markup=kb)

@bot.message_handler(commands=['work'])
def work_process(m):
    u = get_u(m.chat.id)
    if u['job'] == "Безработный":
        return bot.send_message(m.chat.id, "Сначала устройся на работу! /jobs")
    
    # Логика получения зарплаты
    pay = 0
    if u['job'] in JOBS_NO_EDU:
        pay = JOBS_NO_EDU[u['job']]
    else:
        # Ищем в образовательных
        for edu_type in JOBS_EDU:
            if u['job'] in JOBS_EDU[edu_type]:
                pay = JOBS_EDU[edu_type][u['job']]
    
    u['money'] += pay
    bot.send_message(m.chat.id, f"🔨 Ты отработал смену и получил {pay}$!")

# --- ОБРАБОТКА КНОПОК (CALLBACK) ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    u = get_u(call.from_user.id)
    
    # Логика обучения
    if "start_edu_" in call.data:
        edu_name = call.data.replace("start_edu_", "")
        u['edu'] = edu_name
        u['edu_finish'] = time.time() + EDU_TIME_SECONDS
        bot.answer_callback_query(call.id, "Обучение начато!")
        bot.edit_message_text(f"🎓 Вы поступили на факультет: {edu_name}. Учеба закончится через 7 дней.", call.message.chat.id, call.message.message_id)

    # Логика устройства на работу
    elif "set_job_" in call.data:
        job_name = call.data.replace("set_job_", "")
        u['job'] = job_name
        bot.answer_callback_query(call.id, f"Теперь вы {job_name}")
        bot.edit_message_text(f"💼 Вы устроились на работу: {job_name}", call.message.chat.id, call.message.message_id)

    # Логика покупок (пример для Нищих домов)
    elif call.data == "buy_h_poor":
        if u['money'] >= 50000:
            u['money'] -= 50000
            u['house'] = "Уютная комната"
            bot.send_message(call.message.chat.id, "🎉 Поздравляем с покупкой комнаты!")
        else:
            bot.answer_callback_query(call.id, "Недостаточно денег!")

# Запуск
if __name__ == "__main__":
    keep_alive()
    print("Бот запущен!")
    bot.polling(none_stop=True)
