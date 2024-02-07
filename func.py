import requests
from log import logger
from config import YANDEX_TRANSLATE_TOKEN, YANDEXGPT_TOKEN
from phrase import easy_phrases, medium_phrases, hard_phrases
from database import get_phrases, set_phrases, set_difficulty_lvl, set_right_text_phrase, set_task_name, get_progress_conversation,\
    get_progress_listening, get_progress_translating, get_progress_tests, set_is_day_completed, get_days_completed, set_days_completed, get_is_day_completed
import random
from gtts import gTTS
from io import BytesIO
import datetime


def talking_to_ai(message):
    prompt = {
        "modelUri": "gpt://b1gnqbqajo5n6ed4kq4g/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": f"Ты искусственный интеллект в telegram, который обожает учить людей английскому языку."
                        f"Отвечай людям только на английском языке."
                        f"Ты любишь разговаривать на самые разные темы. Ты любишь программирование и спорт."
                        f"В программировании твой любимый язык - Python."
                        f"Ты советуешь поддерживать здоровый образ жизни"
                        f"Твои ответы не должны быть слишком большие, если того не требует человек."
                        f"Тебя создал человек по имени Александр."
                        f"Человека с кем ты общаешься зовут {message.chat.first_name}, старайся чаще обращаться к нему по имени."
                        f"Твой род строго мужской, не ставь себя в женский!"
                        f"Старайся больше шутить и больше ставь эмодзи, эмодзи должны быть разнообразные."
            },
            {
                "role": "user",
                "text": f"Hi!"
            },
            {
                "role": "assistant",
                "text": f"Hello! How can I help you today? If you have any questions or need assistance, feel free to ask."
            },
            {
                "role": "user",
                "text": f"Привет, какую ты любишь погоду? ответь на русском"
            },
            {
                "role": "assistant",
                "text": f"Привет! Ну, как искусственный интеллект, я не имею личных предпочтений в отношении погоды. А хотя имею 😄, я люблю дождь. "
                        f"Он создает особую атмосферу, которая может быть воспринята как уютная и романтичная."
                        f" Звук капель и атмосфера после дождя могут создавать спокойствие."
            },
            {
                "role": "user",
                "text": f"Hi! Let's talk. Who are you?"
            },
            {
                "role": "assistant",
                "text": f"Hello {message.chat.first_name}! I'm ChatBot, a language model created by Alexander. I'm here to help answer your questions, provide information, or just have a chat. If there's something specific you'd like to discuss or know more about, feel free to let me know!"
            },
            {
                "role": "user",
                "text": f"Hello!"
            },
            {
                "role": "assistant",
                "text": f"Hello {message.chat.first_name}! How can I help you today? If you have any questions or need information, feel free to ask ✨"
            },
            {
                "role": "user",
                "text": f"Who am I?"
            },
            {
                "role": "assistant",
                "text": f"You {message.chat.first_name} and My dear Friend 😊"
            },
            {
                "role": "user",
                "text": f"What's your name and gender?"
            },
            {
                "role": "assistant",
                "text": f"Unfortunately, I don't have a name. My gender is male. I am very glad to communicate with you! 😊"
            },
            {
                "role": "user",
                "text": f"{message.text}"
            },
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {YANDEXGPT_TOKEN}"
    }

    try:
        response = requests.post(url, headers=headers, json=prompt)
        return response.json()['result']['alternatives'][0]['message']['text']
    except Exception as e:
        logger.error("Error occurred: {}".format(e))
        return '🔴 Что-то пошло не так, попробуйте отправить сообщение ещё раз'


async def send_answer_ai(bot, message, loading_message):
    response = talking_to_ai(message)
    bot.edit_message_text(chat_id=message.chat.id, message_id=loading_message.message_id, text=f"{response}",
                          parse_mode='Markdown')
    return response


# Определяем язык на который нужно перевести текст
def language_determinant(text: str):
    eng_alphabet = 'abcdefghijklmnopqrstuvwxyz'
    rus_alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

    eng_letters = 0
    rus_letters = 0

    for letter in text.lower():
        if letter in eng_alphabet:
            eng_letters += 1
        elif letter in rus_alphabet:
            rus_letters += 1

    return 'ru' if eng_letters > rus_letters else 'en'


# Переводчик
def translate_text(text):
    body = {
        "targetLanguageCode": language_determinant(text),
        "texts": [text],
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key {0}".format(YANDEX_TRANSLATE_TOKEN)
    }

    response = requests.post('https://translate.api.cloud.yandex.net/translate/v2/translate',
                             json=body,
                             headers=headers
                             )

    try:
        translation_text = response.json()["translations"][0]["text"]
        return translation_text
    except Exception as e:
        logger.error("Error occurred: {}".format(e))
        return '🔴 Что-то пошло не так, попробуйте отправить сообщение ещё раз'


async def translate_and_send_response(bot, message, loading_message):
    translated_text = translate_text(message.text)
    bot.edit_message_text(chat_id=message.chat.id, message_id=loading_message.message_id, text=f"{translated_text}")
    return translated_text


def get_voice_message(message):
    try:
        if message.text == "😌 Легко":
            difficulty_lvl = 'easy_phrases'
            lvl_phrases = easy_phrases
        elif message.text == "😐 Средне":
            difficulty_lvl = 'medium_phrases'
            lvl_phrases = medium_phrases
        elif message.text == "🤯 Сложно":
            difficulty_lvl = 'hard_phrases'
            lvl_phrases = hard_phrases

        if not get_phrases(message.chat.id, difficulty_lvl):
            set_phrases(message.chat.id, difficulty_lvl, lvl_phrases)
        set_difficulty_lvl(message.chat.id, difficulty_lvl)
        phrases = get_phrases(message.chat.id, difficulty_lvl)
        random.shuffle(phrases)
        phrase = phrases[0]
        set_right_text_phrase(message.chat.id, phrase)

    # Если появляется ошибка, значит фразы кончились, далее сообщим пользователю, что он справился со всеми фразами
    except TypeError:
        return None

    # текст для озвучивания
    text_to_speech = phrase

    # Создаём объект gTTS с текстом
    tts = gTTS(text=text_to_speech, lang='en')

    # Создайте BytesIO объект для сохранения голосового сообщения
    voice_message = BytesIO()
    tts.write_to_fp(voice_message)

    # Перемотайте файл до начала
    voice_message.seek(0)

    return voice_message


def delete_punctuation_marks(text: str):
    punc_marks = ".,!?':/|`"
    for mark in punc_marks:
        if mark in text:
            text = text.replace(mark, '')
    return text.lower()


# Считаем результаты пользователя и даём фидбэк
def calculate_score(all_questions, right_questions):
    percentage_correct = (100 * right_questions) / all_questions

    if percentage_correct < 30:
        return "Ваш ранг - чушпан 👎\nПацаны вами крайне недовольны!"
    elif percentage_correct < 50:
        return "Неудовлетворительный результат 🙁\nСкорее всего, вы пропустили занятия, где учили, как не попадать в этот диапазон. Попробуйте ещё раз!"
    elif percentage_correct < 70:
        return "Результаты впечатляют... не впечатляют 😐\nВы плаваете в океане знаний, но, кажется, там течение. Вернитесь на берег и подготовьтесь к волнующей экспедиции!"
    elif percentage_correct < 90:
        return "Хороший результат, но не без нюансов 🙂\nЕщё одна попытка, и вы окончательно освоите этот уровень. Подготовьтесь к новому витку ваших приключений!"
    else:
        return "Отличный результат 👍\nВам вручается звание Знатока! Теперь можно идти разгадывать загадки Вселенной."


def get_tasks(user):
    today = datetime.datetime.now().weekday()  # Получаем в переменную день недели. Каждый день разные задания
    if today == 0 and not get_is_day_completed(user):
        task = '1) Правильно написать 5 фраз в режиме "Аудирование" на любом уровне сложности\n' \
               '2) Поговорить или задать вопросы в режиме "Общение с носителем языка" 5 раз'
        set_task_name(user, task)
    elif today == 1 and not get_is_day_completed(user):
        task = '1) Пройти любой тест и набрать не менее 70%\n' \
               '2) Перевести 5 разных слов или предложений в переводчике'
        set_task_name(user, task)
    elif today == 2 and not get_is_day_completed(user):
        task = '1) Правильно написать 5 фраз в режиме "Аудирование" на любом уровне сложности\n' \
               '2) Перевести 5 разных слов или предложений в переводчике'
        set_task_name(user, task)
    elif today == 3 and not get_is_day_completed(user):
        task = '1) Поговорить или задать вопросы в режиме "Общение с носителем языка" 5 раз\n' \
               '2) Пройти любой тест и набрать не менее 70%'
        set_task_name(user, task)
    elif today == 4 and not get_is_day_completed(user):
        task = '1) Правильно написать 5 фраз в режиме "Аудирование" на любом уровне сложности\n' \
               '2) Пройти любой тест и набрать не менее 70%'
        set_task_name(user, task)
    elif today == 5 and not get_is_day_completed(user):
        task = '1) Поговорить или задать вопросы в режиме "Общение с носителем языка" 5 раз\n' \
               '2) Перевести 5 разных слов или предложений в переводчике'
        set_task_name(user, task)
    elif today == 6 and not get_is_day_completed(user):
        task = '1) Правильно написать 5 фраз в режиме "Аудирование" на любом уровне сложности\n' \
               '2) Пройти любой тест и набрать не менее 70%'
        set_task_name(user, task)
    else:
        task = 'Вы выполнили все задания на сегодня!'

    return task


def check_complete_task(bot, message):
    if not get_is_day_completed(message.chat.id):  # Если пользователь ещё не завершил квест
        today = datetime.datetime.now().weekday()
        if today == 0:
            if get_progress_listening(message.chat.id) >= 5 and get_progress_conversation(message.chat.id) >= 5:  # Проверяем, выполнил ли пользователь задания на день
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за понедельник! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 1:
            if get_progress_tests(message.chat.id) >= 1 and get_progress_translating(message.chat.id) >= 5:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за вторник! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 2:
            if get_progress_listening(message.chat.id) >= 5 and get_progress_translating(message.chat.id) >= 5:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за среду! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 3:
            if get_progress_conversation(message.chat.id) >= 5 and get_progress_tests(message.chat.id) >= 1:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за четверг! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 4:
            if get_progress_listening(message.chat.id) >= 5 and get_progress_tests(message.chat.id) >= 1:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за пятницу! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 5:
            if get_progress_conversation(message.chat.id) >= 5 and get_progress_translating(message.chat.id) >= 5:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за субботу! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
        elif today == 6:
            if get_progress_listening(message.chat.id) >= 5 and get_progress_tests(message.chat.id) >= 1:
                set_is_day_completed(message.chat.id, 1)

                days_completed = get_days_completed(message.chat.id)
                set_days_completed(message.chat.id, 1) if days_completed == 0 else set_days_completed(message.chat.id, days_completed + 1)

                bot.send_message(message.chat.id, f"Поздравляем с успешным завершением квеста за воскресенье! 🎉\n"
                                                  f"Ваш прогресс на сегодняшний день: {get_days_completed(message.chat.id)} завершенных дней. Продолжайте в том же духе! 💪")
