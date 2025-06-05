# database.py

import os
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection as pg_conn # Для аннотации типов


# --- КОНФИГУРАЦИЯ ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ ---
# В идеале эти данные должны храниться в переменных окружения
# Для локальной разработки пока можно оставить так, но для деплоя на Render
# или другой сервер обязательно перенесем их в переменные окружения!
DB_NAME = os.getenv("DB_NAME", "TOOT") # Имя твоей базы данных (может быть postgres или toot_db, если создал)
DB_USER = os.getenv("DB_USER", "postgres") # Имя пользователя PostgreSQL
DB_PASSWORD = os.getenv("DB_PASSWORD", "723050544") # Пароль пользователя PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost") # Хост базы данных (обычно localhost для локальной)
DB_PORT = os.getenv("DB_PORT", "5432") # Порт PostgreSQL

# ВНИМАНИЕ: Замени 'your_db_password' на реальный пароль к твоей базе данных PostgreSQL!
if DB_PASSWORD == "your_db_password":
    print("ВНИМАНИЕ: Пожалуйста, замени 'your_db_password' в database.py на свой реальный пароль PostgreSQL.")


# --- ФУНКЦИЯ ПОДКЛЮЧЕНИЯ К БД ---
def get_db_connection() -> pg_conn:
    """Устанавливает и возвращает соединение с базой данных PostgreSQL."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Успешное подключение к базе данных PostgreSQL.")
        return conn
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        # В реальном приложении здесь лучше бросить исключение или логировать ошибку
        raise # Повторно выбрасываем исключение, чтобы ошибка была видна


# --- БАЗОВЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ---

def create_user_if_not_exists(telegram_id: int) -> int:
    """
    Создает нового пользователя в таблице users, если его еще нет.
    Возвращает user_id существующего или нового пользователя.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Проверяем, существует ли пользователь с таким telegram_id
        cur.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
        user_data = cur.fetchone()

        if user_data:
            user_id = user_data[0]
            print(f"Пользователь с Telegram ID {telegram_id} уже существует. User ID: {user_id}")
            # Обновляем last_active_at при повторном обращении
            cur.execute("UPDATE users SET last_active_at = CURRENT_TIMESTAMP WHERE user_id = %s", (user_id,))
        else:
            # Создаем нового пользователя
            cur.execute(
                "INSERT INTO users (telegram_id) VALUES (%s) RETURNING user_id",
                (telegram_id,)
            )
            user_id = cur.fetchone()[0]
            print(f"Новый пользователь создан с Telegram ID {telegram_id}. User ID: {user_id}")

            # Также создаем пустой профиль для нового пользователя
            cur.execute(
                "INSERT INTO profiles (user_id) VALUES (%s)",
                (user_id,)
            )
            print(f"Создан пустой профиль для User ID: {user_id}")

            # И базовую подписку
            cur.execute(
                "INSERT INTO subscriptions (user_id, level) VALUES (%s, 'Base')",
                (user_id,)
            )
            print(f"Создана базовая подписка для User ID: {user_id}")

        conn.commit() # Сохраняем изменения в базе данных
        return user_id

    except psycopg2.Error as e:
        if conn:
            conn.rollback() # Откатываем изменения в случае ошибки
        print(f"Ошибка при создании/получении пользователя: {e}")
        raise # Повторно выбрасываем исключение
    finally:
        if conn:
            conn.close() # Всегда закрываем соединение с БД

# --- Пример использования (для тестирования) ---
if __name__ == '__main__':
    # Это код, который будет выполнен только если запустить database.py напрямую
    # Попробуй запустить этот файл отдельно, чтобы проверить подключение к БД
    print("Тестируем подключение к базе данных и создание пользователя...")
    try:
        # Попытка создать пользователя с тестовым Telegram ID
        test_telegram_id = 123456789
        user_id = create_user_if_not_exists(test_telegram_id)
        print(f"Тестовый пользователь успешно обработан. User ID: {user_id}")

        # Попробуем еще раз с тем же ID, чтобы убедиться, что он не создается повторно
        user_id_again = create_user_if_not_exists(test_telegram_id)
        print(f"Повторная обработка тестового пользователя. User ID: {user_id_again}")

    except Exception as e:
        print(f"Произошла ошибка во время тестирования: {e}")