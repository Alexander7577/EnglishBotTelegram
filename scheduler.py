from apscheduler.schedulers.background import BackgroundScheduler
from database import get_random_daily_phrase, remove_daily_phrase, get_all_users, get_is_day_completed,\
    set_days_completed, set_is_day_completed, reset_all_progress
from log import logger


def phrase_of_the_day(bot):
    phrase = get_random_daily_phrase()
    # Проверяем, есть ли в бд фразы
    if phrase is None:
        logger.warning("Фразы дня кончились, необходимо добавить новые!!!")
    else:
        users = get_all_users()  # Получаем всех пользователей бота
        for user in users:
            try:
                bot.send_message(user, f'Фраза дня!\n\n{phrase}')
            except Exception as e:
                logger.error(f"Произошла ошибка при отправке сообщения пользователю {user}: {e}")
        # Удаляем использованную фразу
        remove_daily_phrase(phrase)
        logger.info(f"Отправлена фраза дня всем пользователям - {phrase}")


def adjust_days():
    users = get_all_users()
    for user in users:
        if not get_is_day_completed(user):  # Если пользователь не завершил квест за день, то обнуляем ему стрик завершённый дней и сбрасываем прогресс
            set_days_completed(user, 0)
            reset_all_progress()
        elif get_is_day_completed(user):  # Если пользователь завершил квест за день, то начиная новый день, устанавливаем индикатор завершённого квеста в False, и сбрасываем прогресс
            set_is_day_completed(user, 0)
            reset_all_progress()
    logger.info(f"День кончился, появились новые квесты, сбросился прогресс пользователей за день")


def start_scheduler(bot):
    # Создаем объект планировщика
    scheduler = BackgroundScheduler()

    # Добавляем задачу, которая будет выполняться каждый день в 17:00
    scheduler.add_job(phrase_of_the_day, 'cron', hour=17, args=[bot])

    scheduler.add_job(adjust_days, 'cron', hour=0)

    # Запускаем планировщик
    scheduler.start()


