import telebot
import asyncio
from log import logger
from telebot import types
from config import TOKEN
from scheduler import start_scheduler
from questions import questions_a0, questions_a1, questions_a2
from func import calculate_score, translate_and_send_response, send_answer_ai, get_voice_message,\
    delete_punctuation_marks, get_tasks, check_complete_task
from database import create_table, user_exists, create_user, get_user_state, set_user_state,\
    get_question_number, set_question_number, get_right_answers, set_right_answers,\
    create_user_answers, user_answers_exists, get_right_text_phrase, get_phrases, set_phrases, get_difficulty_lvl,\
    user_audio_promotion_exists, create_user_audio_promotion, user_daily_tasks_exists, create_user_daily_tasks,\
    get_progress_conversation, set_progress_conversation,\
    get_progress_translating, set_progress_translating,\
    get_progress_listening, set_progress_listening, get_progress_tests, set_progress_tests, get_days_completed


# Создаём таблицы в бд, если их ещё нет
create_table()

bot = telebot.TeleBot(TOKEN)

# Запускаем задачу по расписанию, каждый день бот будет присылать фразу дня и учитывать прогресс ежедневных заданий
start_scheduler(bot)


# Главное меню, приветствуем пользователя и предлагаем выбрать режим бота для пользователя
@bot.message_handler(commands=["start", "help"])
def welcome(message: telebot.types.Message):
    # Сбрасываем состояния пользователя для корректной работы режимов
    set_user_state(message.chat.id, None)
    # Сбрасываем номера вопросов и кол-во правильных ответов для корректной работы тестов
    set_question_number(message.chat.id, None), set_right_answers(message.chat.id, None)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=True)
    item1 = types.KeyboardButton("🗣️ Общение с носителем языка")
    item2 = types.KeyboardButton("🌐 Переводчик")
    item3 = types.KeyboardButton("👂 Аудирование")
    item4 = types.KeyboardButton("✍️ Тесты")
    item5 = types.KeyboardButton("🎯 Ежедневные задания")
    item6 = types.KeyboardButton("⁉️ Обратная связь")
    markup.add(item1, item2, item3, item4, item5, item6)

    # Проверка наличия пользователя в базе данных
    if not user_exists(message.chat.id):
        # Если пользователя нет в базе данных, сохраняем его
        create_user(message.chat.id, message.chat.first_name, message.chat.last_name, message.chat.username, state=None)
    # Проверка наличия полей в бд для дейликов
    if not user_daily_tasks_exists(message.chat.id):
        create_user_daily_tasks(message.chat.id)

    bot.send_message(message.chat.id, f"Приветствую, {message.chat.first_name}! 🌟\n\n"
                                      f"Добро пожаловать в главное меню, где раскрываются захватывающие возможности для изучения английского!\n\n"
                                      f"Выберите интересующий вас режим и погрузитесь в мир языка прямо сейчас ✨🚀",
                     reply_markup=markup)
    logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | Отправлено приветственное сообщение пользователю')


@bot.message_handler(commands=["daily"])
def daily(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=True)
    start_button = types.KeyboardButton("⬅️ В начало")
    markup.add(start_button)
    if get_days_completed(message.chat.id) % 7 == 0 and get_days_completed(message.chat.id) != 0:
        bot.send_message(message.chat.id,
                         f"Поздравляем! Вы успешно выполняли ежедневные задания в течение {get_days_completed(message.chat.id)} дней подряд! 🎉\n"
                         f"Ваше упорство и стремление заслуживают большого уважения. Продолжайте двигаться вперед, и вместе мы сможем преодолеть любые языковые барьеры! 🚀\n\n"
                         f"В благодарность за ваши достижения, мы хотим вручить вам приз от разработчика! Для получения приза, напишите разработчику @Sanechka757, и он поможет вам с получением. 🎁\n"
                         f"Благодарим вас за то, что выбрали нас! Ваш вклад в наше сообщество очень ценен. Спасибо, что вы с нами! 🙌",
                         reply_markup=markup, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'К сожалению сейчас вы не можете получить свой приз 😔\n'
                                          'Призы выдаются только после выполнения ежедневных заданий в течении 7 дней подряд.\n'
                                          'Начните прямо сейчас и вы получите свой заслуженный приз! 💪')


# Режим "Разговор с носителем языка"
@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "conversation")
def conversation_handler(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        set_user_state(message.chat.id, None)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из режима "Общение с носителем языка"')
        welcome(message)
    else:
        # Увеличиваем прогресс разговора с носителем на 1 для дейликов
        progress = get_progress_conversation(message.chat.id)
        set_progress_conversation(message.chat.id, progress + 1)

        loading_message = bot.send_message(message.chat.id, "🫠 Бот печатает, подождите...")
        response = asyncio.run(send_answer_ai(bot, message, loading_message))

        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | "Общение с носителем языка" | {message.chat.first_name} - {message.text} | Бот - {response}')

        check_complete_task(bot, message)


# Режим "Переводчик"
@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "translating")
def translater(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        set_user_state(message.chat.id, None)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из режима "Переводчик"')
        welcome(message)
    else:
        # Увеличиваем прогресс переводчика на 1 для дейликов
        progress = get_progress_translating(message.chat.id)
        set_progress_translating(message.chat.id, progress + 1)

        loading_message = bot.send_message(message.chat.id, "🫠 идёт загрузка перевода, подождите...")
        translate_text = asyncio.run(translate_and_send_response(bot, message, loading_message))
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | "Переводчик" | {message.chat.first_name} - {message.text} | Бот - {translate_text}')

        check_complete_task(bot, message)


# Режим "Аудирование"
@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "listening")
def listening_handler(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        set_user_state(message.chat.id, None)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из режима "Аудирование"')
        welcome(message)
    elif message.text in ["😌 Легко", "😐 Средне", "🤯 Сложно"]:
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | Выбирает уровень {message.text} в режиме "Аудирование"')

        if not user_audio_promotion_exists(message.chat.id):  # Создаём запись пользователя для отслеживания фраз если её ещё нет
            create_user_audio_promotion(message.chat.id)

        loading_message = bot.send_message(message.chat.id, " 🫠 Бот записывает голосовое сообщение, подождите...")
        voice_phrase = get_voice_message(message)

        if voice_phrase:
            logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | Бот отправляет фразу "{get_right_text_phrase(message.chat.id)}" в режиме "Аудирование"')

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            start_button = types.KeyboardButton("⬅️ Назад")
            markup.add(start_button)

            set_user_state(message.chat.id, 'audio_answer')
            bot.send_voice(message.chat.id, voice=voice_phrase, reply_markup=markup)
            bot.edit_message_text(chat_id=message.chat.id, message_id=loading_message.message_id,
                                  text="✅ Голосовое сообщение записано!")
        else:
            logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | написал(а) все фразы уровня {message.text} в режиме "Аудирование".')
            bot.send_message(message.chat.id, "Вы отлично справились со всеми фразами на этом уровне, Well done 👍")


# Проверяем верно ли пользователь написал фразу
@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "audio_answer")
def check_phrase(message: telebot.types.Message):
    if message.text == "⬅️ Назад":
        # Обратно возвращаемся в меню выбора аудиосообщений
        set_user_state(message.chat.id, None)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | без ответа возвращается обратно к выбору уровня сложности в режиме "Аудирование"')
        return handle_text(message, audio=True)

    # Удаляем знаки препинания и приводим текст к нижнему регистру для более удобного ввода пользователя
    right_answer = delete_punctuation_marks(get_right_text_phrase(message.chat.id))
    answer_from_user = delete_punctuation_marks(message.text)

    # Если пользователь дал верный ответ, то сообщаем ему об этом и удаляем из списка фразу, которую пользователь правильно написал
    if right_answer == answer_from_user:
        # Увеличиваем прогресс аудирования на 1 для дейликов
        progress = get_progress_listening(message.chat.id)
        set_progress_listening(message.chat.id, progress + 1)

        bot.send_message(message.chat.id, "Вы написали фразу верно, отлично ✅")
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | даёт верный ответ в режиме "Аудирование" - {message.text}')

        check_complete_task(bot, message)

        # Удаляем верно написанную фразу
        difficulty_lvl = get_difficulty_lvl(message.chat.id)
        phrases = get_phrases(message.chat.id, difficulty_lvl)
        phrases.remove(get_right_text_phrase(message.chat.id))
        set_phrases(message.chat.id, difficulty_lvl, phrases)
    else:
        bot.send_message(message.chat.id, f"Вы ошиблись ❌\n\nПравильный вариант - {get_right_text_phrase(message.chat.id)}")
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | даёт неверный ответ в режиме "Аудирование" - {message.text}')

    # Обратно возвращаемся в меню выбора аудиосообщений
    set_user_state(message.chat.id, None)
    logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается обратно к выбору уровня сложности в режиме "Аудирование"')
    handle_text(message, audio=True)


# Режим "Тесты"
@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "tests")
def choice_test(message: telebot.types.Message):                                        # Выбор тестов для пользователя
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из режима "Тесты"')
        welcome(message)
    elif message.text in ["😇 A0", "😌 A1", "😐 A2"]:
        message.text = message.text.split()[1]
        set_user_state(message.chat.id, f"test_{message.text.lower()}")
        bot.send_message(message.chat.id, f"Выбран уровень теста {message.text}")
        logger.info(f"{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | выбирает уровень теста {message.text}")
        if not user_answers_exists(message.chat.id):
            create_user_answers(message.chat.id, None, None)  # Создаём запись пользователя для отслеживания вопросов и подсчёта верных ответов если её ещё нет
        start_test(message)
    elif message.text in ["😬 B1", "😨 B2", "😰 C1", "🤯 C2"]:
        bot.send_message(message.chat.id,
                         "Извините, но тест для этого уровня ещё не придуман 🥺\n\nСледите за обновлениями 😉")
        logger.info(f"{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | выбирает тест {message.text}, может пора бы уже придумать этот тест?")


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) in ["test_a0", "test_a1", "test_a2"])
def start_test(message: telebot.types.Message):                 # Задаём вопрос пользователю и выводим варианты ответов
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из теста {get_user_state(message.chat.id)}')
        set_user_state(message.chat.id, None)
        return welcome(message)
    elif get_user_state(message.chat.id) == 'test_a0':
        set_user_state(message.chat.id, 'test_a0_answers')
        test = questions_a0
    elif get_user_state(message.chat.id) == 'test_a1':
        set_user_state(message.chat.id, 'test_a1_answers')
        test = questions_a1
    elif get_user_state(message.chat.id) == 'test_a2':
        set_user_state(message.chat.id, 'test_a2_answers')
        test = questions_a2

    question_number = get_question_number(message.chat.id)
    right_questions = get_right_answers(message.chat.id)

    if question_number < len(test):
        # Выводим вопрос и варианты ответа
        question = test[question_number]["question"]
        options = test[question_number]["options"]

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for option in options:
            markup.add(types.KeyboardButton(option))

        bot.send_message(message.chat.id, f"Вопрос: {question_number + 1}/{len(test)}\n\n*{question}*",
                         reply_markup=markup, parse_mode='Markdown')
        logger.info(f"{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | {question_number + 1}/{len(test)} - Бот задал вопрос - {question}")
    else:
        # Все вопросы заданы, выводим результат

        # Увеличиваем прогресс тестов на 1 для дейликов если набрали за тест больше 70%
        if (100 * right_questions) / len(test) >= 70:
            progress = get_progress_tests(message.chat.id)
            set_progress_tests(message.chat.id, progress + 1)

        set_question_number(message.chat.id, None), set_right_answers(message.chat.id, None)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        result = calculate_score(len(test), right_questions)
        bot.send_message(message.chat.id, f"Тест завершен! Ваш результат: {right_questions}/{len(test)}\n\n{result}",
                         reply_markup=markup)
        logger.info(
            f"{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | Тест завершен! Результат: {right_questions}/{len(test)} | {result}")

        check_complete_task(bot, message)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) in ["test_a0_answers", "test_a1_answers", "test_a2_answers"])
def handle_test_answer(message: telebot.types.Message):  # Проверяем ответы и переходим к следующему вопросу
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращение в главное меню из теста {get_user_state(message.chat.id)}')
        set_user_state(message.chat.id, None)
        set_question_number(message.chat.id, None), set_right_answers(message.chat.id, None)
        return welcome(message)
    elif get_user_state(message.chat.id) == "test_a0_answers":
        set_user_state(message.chat.id, "test_a0")
        test = questions_a0
    elif get_user_state(message.chat.id) == "test_a1_answers":
        set_user_state(message.chat.id, "test_a1")
        test = questions_a1
    elif get_user_state(message.chat.id) == "test_a2_answers":
        set_user_state(message.chat.id, "test_a2")
        test = questions_a2

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_button = types.KeyboardButton("⬅️ В начало")
    next_button = types.KeyboardButton("Далее ➡️")
    markup.add(start_button, next_button)

    # Проверяем, является ли ответ правильным
    question_number = get_question_number(message.chat.id)
    right_questions = get_right_answers(message.chat.id)

    correct_option = test[question_number]["correct_option"]
    user_answer = message.text
    logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | даёт ответ - {user_answer}')

    if user_answer == correct_option:
        # Пользователь ответил правильно
        right_questions += 1
        bot.send_message(message.chat.id, "Правильно! 👍", reply_markup=markup)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | даёт правильный ответ!')
    else:
        # Пользователь ответил неправильно
        bot.send_message(message.chat.id, f"Неправильно. Правильный ответ: {correct_option} 👎", reply_markup=markup)
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | даёт неверный ответ!')

    # Переходим к следующему вопросу
    set_question_number(message.chat.id, question_number + 1), set_right_answers(message.chat.id, right_questions)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "feedback")
def handle_feedback(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из выбора теста')
        welcome(message)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        logger.warning(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | Оставляет feedback | {message.text}')
        bot.send_message(message.chat.id, "Спасибо, ваш ответ записан 📝\n"
                                          "Если у вас есть еще какие-то идеи или вопросы, не стесняйтесь делиться. Ваш вклад ценен!",
                         reply_markup=markup)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == "daily")
def handle_daily(message: telebot.types.Message):
    if message.text == "⬅️ В начало":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | возвращается в главное меню из раздела "Ежедневные задания"')
        welcome(message)


@bot.message_handler(content_types=["text"])
def handle_text(message: telebot.types.Message, audio=False):
    if message.text == "🗣️ Общение с носителем языка":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | входит в режим "Общение с носителем языка"')
        # Сбрасываем предыдущее состояние
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "conversation")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, 'Добро пожаловать в режим *"Общение с носителем языка"* 🗣️\n\n'
                                          'Здесь открываются бескрайние возможности для обсуждения различных тем, получения помощи в вопросах изучения языка и, конечно же, многого другого! 🚀\n\n'
                                          'Погрузитесь в диалог, введя любой текст, и давайте вместе раскроем чарующий мир языкового общения. 🌍💬\n\n'
                                          'Жду ваших слов, чтобы начать это увлекательное путешествие!',
                         reply_markup=markup, parse_mode='Markdown')
    elif message.text == "🌐 Переводчик":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | входит в режим "Переводчик"')
        # Сбрасываем предыдущее состояние
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "translating")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, 'Добро пожаловать в режим *"Переводчик"* 🌐!\n\n'
                                          'Здесь каждое слово — это не только перевод, но и путешествие в мир английского языка и его культуры.\n\n'
                                          'Дайте волю вашему любопытству, и вместе мы откроем двери к бескрайнему океану знаний! 🌊🔓\n\n'
                                          'Чтобы продолжить, введите текст для перевода 📝',
                         reply_markup=markup, parse_mode='Markdown')
    elif message.text == "✍️ Тесты":
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | входит в режим "Тесты"')
        # Сбрасываем предыдущее состояние
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "tests")

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

        bot.send_message(message.chat.id, 'Добро пожаловать в захватывающий режим *"Тесты"* 📝!\n\n'
                                          'Здесь вы сможете проверить свои знания, пройдя увлекательные тесты по разнообразным темам. 🌐🧠\n'
                                          'Готовьтесь к вызову ума, и давайте вместе пройдем этот увлекательный путь знаний! 🚀💡\n\n'
                                          'Давайте узнаем, насколько хорошо вы владеете выбранным уровнем. 🌟🤔\n\n'
                                          'Погрузитесь в мир вопросов и ответов, чтобы узнать что-то новое и удивительное! 🌈🌐',
                         reply_markup=markup, parse_mode='Markdown')
    elif message.text == "👂 Аудирование" or audio:  # Если переменная audio True, значит мы продолжаем быть в режиме аудирование
        # Сбрасываем предыдущее состояние
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "listening")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        easy_lvl = types.KeyboardButton("😌 Легко")
        medium_lvl = types.KeyboardButton("😐 Средне")
        hard_lvl = types.KeyboardButton("🤯 Сложно")
        markup.add(easy_lvl, medium_lvl, hard_lvl, start_button)

        if not audio:
            logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | входит в режим "Аудирование"')

            bot.send_message(message.chat.id, 'Добро пожаловать в увлекательный режим *"Аудирование"*! 👂\n\n'
                                              'Здесь вы имеете возможность улучшить свое восприятие английской речи и избавиться от путаницы в словах 😃.\n\n'
                                              'Для продолжения выберите уровень сложности, который вам комфортен 🌟.\n'
                                              'Бот отправит вам голосовое сообщение 🎤, а ваша задача - переписать фразу, сказанную ботом, текстом!\n\n'
                                              'Регистр и знаки препинания не влияют на результат 😉.\n'
                                              'Готовы погрузиться в мир аудиовызовов и улучшения навыков понимания речи? 🚀🗣️',
                             reply_markup=markup, parse_mode='Markdown')
        elif audio:
            bot.send_message(message.chat.id, "Продолжайте покорять вершины режима *Аудирование*!\n"
                                              "Слушать на английском - значит погружаться в мир мировой культуры, образования и инноваций.",
                             reply_markup=markup, parse_mode='Markdown')
    elif message.text == "🎯 Ежедневные задания":
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "daily")

        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | заходит в раздел "Ежедневные задания"')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, f'Добро пожаловать в раздел ежедневных заданий! 🎯\n\n'
                                          f'Здесь вы найдете интересные задания, которые помогут развивать навыки и улучшать знания.\n'
                                          f'Начните день с новыми вызовами и достижениями! 🚀\n\n'
                                          f'Не забывайте, что если вы выполняете задания 7 дней подряд, вы получаете приз от разработчика! 🎁\n'
                                          f'Однако, будьте внимательны, пропустив день, вы потеряете свой прогресс, так что держите серию и не упускайте ни одного дня!\n\n'
                                          f'Для получения приза наберите команду /daily 🔥\n\n'
                                          f'Количество выполненных дней: {get_days_completed(message.chat.id)}\n\n'
                                          f'Ваши задания на сегодня:\n\n{get_tasks(message.chat.id)}',
                         reply_markup=markup, parse_mode='Markdown')
    elif message.text == "⁉️ Обратная связь":
        set_user_state(message.chat.id, None)
        set_user_state(message.chat.id, "feedback")

        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | заходит в раздел "Обратная связь"')

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        start_button = types.KeyboardButton("⬅️ В начало")
        markup.add(start_button)

        bot.send_message(message.chat.id, 'Добро пожаловать в раздел *"Обратная связь"*\n\n'
                                          'Здесь ваш голос имеет особенное значение! Если вы обнаружили баги, хотите предложить улучшения или просто поделиться своим мнением, вы находитесь в нужном месте.\n'
                                          'Ваши отзывы помогут сделать бота еще лучше.\n\n'
                                          'Благодарю вас за использование бота и за ваши ценные замечания! 🙏🤖',
                         reply_markup=markup, parse_mode='Markdown')
    else:
        logger.info(f'{message.chat.username} - {message.chat.last_name} - {message.chat.first_name} | отправляет сообщение без режима - {message.text}')
        bot.send_message(message.chat.id, "Выберите функцию для бота =)")


bot.polling(none_stop=True)
