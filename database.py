import sqlite3
import json


def create_table():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            state TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_answers (
            user_id INTEGER PRIMARY KEY,
            question_number INTEGER,
            right_answers INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_audio_promotion (
            user_id INTEGER PRIMARY KEY,
            easy_phrases TEXT,
            medium_phrases TEXT,
            hard_phrases TEXT,
            difficulty_lvl TEXT,
            'right_answer' TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_pronunciation_promotion (
            user_id INTEGER PRIMARY KEY,
            easy_phrases TEXT,
            medium_phrases TEXT,
            hard_phrases TEXT,
            difficulty_lvl TEXT,
            'right_answer' TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_phrases (
            phrase_id INTEGER PRIMARY KEY,
            text TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_tasks (
            user_id INTEGER PRIMARY KEY,
            task_name TEXT,
            progress_conversation INTEGER DEFAULT 0,
            progress_translating INTEGER DEFAULT 0,
            progress_listening INTEGER DEFAULT 0,
            progress_pronunciation INTEGER DEFAULT 0,
            progress_tests INTEGER DEFAULT 0,
            is_day_completed BOOLEAN DEFAULT 0,
            days_completed INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')

    conn.commit()
    conn.close()


# Проверка на существование пользователя, геттеры, сеттеры и т.п для таблицы users
def user_exists(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user(user_id, first_name, last_name, username, state):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO users (user_id, first_name, last_name, username, state)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, first_name, last_name, username, state))
    conn.commit()
    conn.close()


# Получаем состояние пользователя
def get_user_state(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT state FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


# Устанавливаем состояние пользователю
def set_user_state(user_id, state):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE users SET state = ? WHERE user_id = ?', (state, user_id))
    conn.commit()

    conn.close()


# Проверка на существование пользователя, геттеры, сеттеры и т.п для таблицы user_answers
def user_answers_exists(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM user_answers WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user_answers(user_id, question_number, right_answers):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO user_answers (user_id, question_number, right_answers)
        VALUES (?, ?, ?)
    ''', (user_id, question_number, right_answers))
    conn.commit()

    conn.close()


def get_question_number(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT question_number FROM user_answers WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] else 0


def set_question_number(user_id, question_number):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE user_answers SET question_number = ? WHERE user_id = ?', (question_number, user_id))
    conn.commit()

    conn.close()


def get_right_answers(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT right_answers FROM user_answers WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] else 0


def set_right_answers(user_id, right_answers):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE user_answers SET right_answers = ? WHERE user_id = ?', (right_answers, user_id))
    conn.commit()

    conn.close()


# Проверка на существование пользователя, геттеры, сеттеры и т.п для таблицы user_audio_promotion и user_pronunciation_promotion
def user_promotion_exists(table_name, user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT user_id FROM {table_name} WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user_promotion(table_name, user_id, easy_phrases=None, medium_phrases=None, hard_phrases=None, difficulty_lvl=None, right_answer=None):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'''
        INSERT INTO {table_name} (user_id, easy_phrases, medium_phrases, hard_phrases, difficulty_lvl, right_answer)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, easy_phrases, medium_phrases, hard_phrases, difficulty_lvl, right_answer))
    conn.commit()
    conn.close()


def get_phrases(table_name, user_id, difficulty_lvl):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT {difficulty_lvl} FROM {table_name} WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result[0]:
        result = json.loads(result[0])  # Sqlite не поддерживает списки, поэтому полученный объект преобразуем в список с помощью json
        return True if result == [] else result  # Если result = [], то пользователь верно написал все фразы и мы не будем заново их добавлять, чтобы не попасть в блок добавления фраз, мы возвращаем True
    else:
        return None


def set_phrases(table_name, user_id, difficulty_lvl, phrases):
    phrases_as_json = json.dumps(phrases)  # sqlite не поддерживает списки, поэтому преобразовываем переменную в json объект

    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE {table_name} SET {difficulty_lvl} = ? WHERE user_id = ?', (phrases_as_json, user_id))
    conn.commit()

    conn.close()


def get_difficulty_lvl(table_name, user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT difficulty_lvl FROM {table_name} WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] else None


def set_difficulty_lvl(table_name, user_id, difficulty_lvl):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE {table_name} SET difficulty_lvl = ? WHERE user_id = ?', (difficulty_lvl, user_id))
    conn.commit()

    conn.close()


def get_right_text_phrase(table_name, user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'SELECT right_answer FROM {table_name} WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result[0] else None


def set_right_text_phrase(table_name, user_id, right_answer):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute(f'UPDATE {table_name} SET right_answer = ? WHERE user_id = ?', (right_answer, user_id))
    conn.commit()

    conn.close()


# Проверка на существование пользователя, геттеры, сеттеры и т.п для таблицы daily_phrases
def get_random_daily_phrase():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT text FROM daily_phrases ORDER BY RANDOM() LIMIT 1')

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def add_daily_phrase(text):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO daily_phrases (text) VALUES (?)", (text,))
    conn.commit()

    conn.close()


def remove_daily_phrase(text):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM daily_phrases WHERE text=?", (text,))
    conn.commit()


def daily_phrase_exist():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT text FROM daily_phrases')
    result = cursor.fetchone()

    conn.close()

    return result is not None


# Получаем список всех пользователей бота
def get_all_users():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM users')

    result = [user[0] for user in cursor.fetchall()]
    conn.close()

    return result if result else None


# Проверка на существование пользователя, геттеры, сеттеры и т.п для таблицы daily_tasks
def user_daily_tasks_exists(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT user_id FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result is not None


def create_user_daily_tasks(user_id, task_name=None):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO daily_tasks (user_id, task_name)
        VALUES (?, ?)
    ''', (user_id, task_name))
    conn.commit()

    conn.close()


def set_progress_conversation(user_id, progress_conversation):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET progress_conversation = ? WHERE user_id = ?', (progress_conversation, user_id))
    conn.commit()

    conn.close()


def get_progress_conversation(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT progress_conversation FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_progress_translating(user_id, progress_translating):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET progress_translating = ? WHERE user_id = ?', (progress_translating, user_id))
    conn.commit()

    conn.close()


def get_progress_translating(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT progress_translating FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_progress_listening(user_id, progress_listening):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET progress_listening = ? WHERE user_id = ?', (progress_listening, user_id))
    conn.commit()

    conn.close()


def get_progress_listening(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT progress_listening FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_progress_pronunciation(user_id, progress_pronunciation):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET progress_pronunciation = ? WHERE user_id = ?', (progress_pronunciation, user_id))
    conn.commit()

    conn.close()


def get_progress_pronunciation(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT progress_pronunciation FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_progress_tests(user_id, progress_tests):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET progress_tests = ? WHERE user_id = ?', (progress_tests, user_id))
    conn.commit()

    conn.close()


def get_progress_tests(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT progress_tests FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_is_day_completed(user_id, is_day_completed):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET is_day_completed = ? WHERE user_id = ?', (is_day_completed, user_id))
    conn.commit()

    conn.close()


def get_is_day_completed(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT is_day_completed FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def set_days_completed(user_id, days_completed):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET days_completed = ? WHERE user_id = ?', (days_completed, user_id))
    conn.commit()

    conn.close()


def get_days_completed(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT days_completed FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None


def reset_all_progress():
    users = get_all_users()
    for user in users:
        set_progress_conversation(user, 0)
        set_progress_translating(user, 0)
        set_progress_listening(user, 0)
        set_progress_tests(user, 0)


def set_task_name(user_id, task_name):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE daily_tasks SET task_name = ? WHERE user_id = ?', (task_name, user_id))
    conn.commit()

    conn.close()


def get_task_name(user_id):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT task_name FROM daily_tasks WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None
