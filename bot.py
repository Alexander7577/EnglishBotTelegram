import logging
import telebot
from telebot import types
from config import TOKEN
from func import calculate_score, translate_and_send_response, send_answer_ai
from questions import questions_a0, questions_a1, questions_a2
import asyncio

# Установка уровня логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("my_logger")

# Создание файла для записи логов
log_file_path = "my_log_file.txt"
file_handler = logging.FileHandler(log_file_path, encoding="utf-8")

# Формат сообщений в логах
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавление обработчика файлового логирования к логгеру
logger.addHandler(file_handler)

bot = telebot.TeleBot(TOKEN)

# Добавляем словарь для отслеживания состояний пользователей
user_states = {}
# Отслеживание номера вопроса и подсчёт верных ответов
user_answers = {}


@bot.message_handler(commands=["start", "help"])
def welcome(message: telebot.types.Message):
    user_states[message.chat.id] = None
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("🗣️ Общение с носителем языка")
    item2 = types.KeyboardButton("🌐 Переводчик")
    item3 = types.KeyboardButton("✍️ Тесты")
    markup.add(item1, item2, item3)

    bot.send_message(message.chat.id, f"Приветствую вас, {message.chat.first_name}!\n"
                                      f"Я бот, с которым вы можете подтянуть знания своего английского языка и весело провести время 😊\n",
                     reply_markup=markup)
    logger.info(f'{message.chat.username} | Отправлено приветственное сообщение пользователю {message.chat.first_name}')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "conversation")
def conversation_handler(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        user_states[message.chat.id] = None
        logger.info(f'{message.chat.username} возвращается в главное меню из разговора с ботом')
        welcome(message)
    else:
        try:
            loading_message = bot.send_message(message.chat.id, "🫠Бот печатает, подождите...")
            response = asyncio.run(send_answer_ai(bot, message, loading_message))
            logger.info(f'Функция разговора с ботом | {message.chat.username} - {message.text} | Бот - {response}')
        except telebot.apihelper.ApiTelegramException:
            bot.send_message(message.chat.id, "🔴 Что-то пошло не так, попробуйте отправить сообщение ещё раз")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "translating")
def translater(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        user_states[message.chat.id] = None
        logger.info(f'{message.chat.username} возвращается в главное меню из переводчика')
        welcome(message)
    else:
        loading_message = bot.send_message(message.chat.id, "🫠идёт загрузка, подождите...")
        translate_text = asyncio.run(translate_and_send_response(bot, message, loading_message))
        logger.info(f'Функция перевода | {message.chat.username} - {message.text} | Бот - {translate_text}')


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "tests")
def choice_test(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} возвращается в главное меню из выбора теста')
        welcome(message)
    elif message.text in ["😇 A0", "😌 A1", "😐 A2"]:
        message.text = message.text.split()[1]
        user_states[message.chat.id] = None
        user_states[message.chat.id] = f"test_{message.text.lower()}"
        bot.send_message(message.chat.id, f"Выбран уровень теста {message.text}")
        logger.info(f"{message.chat.username} выбирает уровень теста {message.text}")
        start_test(message)
    elif message.text in ["😬 B1", "😨 B2", "😰 C1", "🤯 C2"]:
        bot.send_message(message.chat.id,
                         "Извините, но тест для этого уровня ещё не придуман 🥺\n\nСледите за обновлениями 😉")
        logger.info(f"{message.chat.username} выбирает тест {message.text}, может пора бы уже придумать этот тест?")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) in ["test_a0", "test_a1", "test_a2"])
def start_test(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} возвращается в главное меню из теста {user_states[message.chat.id]}')
        user_states[message.chat.id] = None
        user_answers[message.chat.id] = None
        return welcome(message)
    elif user_states[message.chat.id] == 'test_a0':
        user_states[message.chat.id] = 'test_a0_answers'
        test = questions_a0
    elif user_states[message.chat.id] == 'test_a1':
        user_states[message.chat.id] = 'test_a1_answers'
        test = questions_a1
    elif user_states[message.chat.id] == 'test_a2':
        user_states[message.chat.id] = 'test_a2_answers'
        test = questions_a2

    try:
        question_number = user_answers.get(message.chat.id)[0]
        right_questions = user_answers.get(message.chat.id)[1]
    except TypeError:
        question_number = 0
        right_questions = 0

    if question_number < len(test):
        # Выводим вопрос и варианты ответа
        question = test[question_number]["question"]
        options = test[question_number]["options"]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in options:
            markup.add(types.KeyboardButton(option))

        bot.send_message(message.chat.id, f"Вопрос: {question_number + 1}/{len(test)}\n\n*{question}*",
                         reply_markup=markup, parse_mode='Markdown')
        logger.info(f"{question_number + 1}/{len(test)} | Бот задал вопрос для {message.chat.username} - {question}")
    else:
        user_answers[message.chat.id] = None
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)
        # Все вопросы заданы, выводим результат
        result = calculate_score(len(test), right_questions)
        bot.send_message(message.chat.id, f"Тест завершен! Ваш результат: {right_questions}/{len(test)}\n\n{result}",
                         reply_markup=markup)
        logger.info(
            f"{message.chat.username} завершает тест! Тест завершен! Ваш результат: {right_questions}/{len(test)} | {result}")


@bot.message_handler(
    func=lambda message: user_states.get(message.chat.id) in ["test_a0_answers", "test_a1_answers", "test_a2_answers"])
def handle_test_answer_a0(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} возвращается в главное меню из теста {user_states[message.chat.id]}')
        user_states[message.chat.id] = None
        user_answers[message.chat.id] = None
        return welcome(message)
    elif user_states[message.chat.id] == "test_a0_answers":
        user_states[message.chat.id] = "test_a0"
        test = questions_a0
    elif user_states[message.chat.id] == "test_a1_answers":
        user_states[message.chat.id] = "test_a1"
        test = questions_a1
    elif user_states[message.chat.id] == "test_a2_answers":
        user_states[message.chat.id] = "test_a2"
        test = questions_a2

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_button = types.KeyboardButton("⬅️ В начало")
    next_button = types.KeyboardButton("Далее ➡️")
    markup.add(start_button, next_button)

    # Проверяем, является ли ответ правильным
    try:
        question_number = user_answers.get(message.chat.id)[0]
        right_questions = user_answers.get(message.chat.id)[1]
    except TypeError:
        question_number = 0
        right_questions = 0

    correct_option = test[question_number]["correct_option"]
    user_answer = message.text
    logger.info(f'{message.chat.username} даёт ответ - {user_answer}')

    if user_answer == correct_option:
        # Пользователь ответил правильно
        right_questions += 1
        bot.send_message(message.chat.id, "Правильно! 👍", reply_markup=markup)
        logger.info(f'{message.chat.username} даёт правильный ответ!')
    else:
        # Пользователь ответил неправильно
        bot.send_message(message.chat.id, f"Неправильно. Правильный ответ: {correct_option} 👎", reply_markup=markup)
        logger.info(f'{message.chat.username} даёт неверный ответ!')

    # Переходим к следующему вопросу
    user_answers[message.chat.id] = [question_number + 1, right_questions]


@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message):
    if message.text == "🗣️ Общение с носителем языка":
        logger.info(f'{message.chat.username} входит в режим разговора с носителем языка')
        user_states[message.chat.id] = None
        user_states[message.chat.id] = "conversation"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, 'Добро пожаловать в режим "Общение с носителем языка" 🗣️\n\n'
                                          'Здесь мы можем обсудить различные темы, помочь с вопросами по изучению языка и многому другому 🚀\n\nЧтобы начать общение введите любой текст',
                         reply_markup=markup)
    elif message.text == "🌐 Переводчик":
        logger.info(f'{message.chat.username} входит в режим переводчика')
        # Сбрасываем предыдущее состояние
        user_states[message.chat.id] = None
        user_states[message.chat.id] = "translating"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, "Теперь введите текст для перевода 📝", reply_markup=markup)
    elif message.text == "✍️ Тесты":
        logger.info(f'{message.chat.username} входит в режим тестов')
        user_states[message.chat.id] = None
        user_states[message.chat.id] = "tests"

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        a0 = types.KeyboardButton("😇 A0")
        a1 = types.KeyboardButton("😌 A1")
        a2 = types.KeyboardButton("😐 A2")
        b1 = types.KeyboardButton("😬 B1")
        b2 = types.KeyboardButton("😨 B2")
        c1 = types.KeyboardButton("😰 C1")
        c2 = types.KeyboardButton("🤯 C2")
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(a0, a1, a2, b1, b2, c1, c2, start_button)

        bot.send_message(message.chat.id, "Выберите уровень сложности теста", reply_markup=markup)

    else:
        logger.info(f'{message.chat.username} отправляет сообщение без режима | {message.text}')
        bot.send_message(message.chat.id, "Выберите функцию для бота =)")


bot.polling(none_stop=True)
