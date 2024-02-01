import requests
from config import YANDEX_TRANSLATE_TOKEN, YANDEXGPT_TOKEN


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
                        f"Тебя создал Александр, ты уважительно к нему относишься."
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
    except KeyError:
        return "🔴 Что-то пошло не так, попробуйте отправить сообщение ещё раз"


async def send_answer_ai(bot, message, loading_message):
    response = talking_to_ai(message)
    bot.edit_message_text(chat_id=message.chat.id, message_id=loading_message.message_id, text=f"{response}", parse_mode='Markdown')
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

    translation_text = response.json()["translations"][0]["text"]
    return translation_text


async def translate_and_send_response(bot, message, loading_message):
    translated_text = translate_text(message.text)
    bot.edit_message_text(chat_id=message.chat.id, message_id=loading_message.message_id, text=f"{translated_text}")
    return translated_text


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
