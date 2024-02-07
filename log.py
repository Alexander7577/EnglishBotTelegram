import logging

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
