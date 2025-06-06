# bot.py

import os
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import database # Импортируем наш модуль для работы с БД

# --- НОВОЕ: Импортируем dotenv ---
from dotenv import load_dotenv

# --- НОВОЕ: Загружаем переменные окружения ---
# Эта функция ищет файл .env в текущей директории и загружает переменные из него.
# В продакшене (на сервере), если переменные окружения установлены системой,
# load_dotenv() просто ничего не сделает, так как они уже будут доступны через os.getenv().
load_dotenv()

# --- НОВОЕ: Читаем токен и URL из переменных окружения ---
# Получаем токен Telegram-бота из переменной окружения.
# Если переменная не установлена, os.getenv() вернет None.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Получаем URL Web App из переменной окружения.
WEB_APP_URL = os.getenv("WEB_APP_URL")

# --- НОВОЕ: Проверка на наличие токена и URL ---
# Это критически важный шаг, чтобы бот не запустился без необходимых данных.
if not TOKEN:
    raise ValueError("Переменная окружения 'TELEGRAM_BOT_TOKEN' не найдена. "
                     "Убедитесь, что она установлена или присутствует в файле .env")
if not WEB_APP_URL:
    raise ValueError("Переменная окружения 'WEB_APP_URL' не найдена. "
                     "Убедитесь, что она установлена или присутствует в файле .env")

# Для отладки: выводим загруженные значения (частично для безопасности токена)
print(f"Загружен токен (первые 5 символов): {TOKEN[:5]}...")
print(f"Загружен URL Web App: {WEB_APP_URL}")


# Функция для обработки команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отправляет приветственное сообщение при команде /start
    и создает пользователя в БД, если его нет.
    Показывает кнопку для открытия Web App.
    """
    user_id = update.effective_user.id
    user_name = update.effective_user.mention_html()

    # Попытка создать или получить пользователя в БД
    try:
        # Предполагаем, что database.create_user_if_not_exists возвращает ID пользователя из БД
        db_user_id = database.create_user_if_not_exists(user_id)
        print(f"Пользователь Telegram ID {user_id} (DB User ID: {db_user_id}) обработан.")
    except Exception as e:
        print(f"Ошибка БД при обработке пользователя {user_id}: {e}")
        await update.message.reply_text("Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.")
        return

    # Создаем кнопки ReplyKeyboardMarkup
    # Кнопка для открытия главного Web App
    open_app_button = KeyboardButton("Начать знакомство!", web_app=WebAppInfo(url=WEB_APP_URL))
    # Кнопки для навигации внутри Web App (примеры)
    search_button = KeyboardButton("Поиск", web_app=WebAppInfo(url=WEB_APP_URL + "/search"))
    messages_button = KeyboardButton("Сообщения", web_app=WebAppInfo(url=WEB_APP_URL + "/messages"))

    keyboard = [
        [open_app_button], # Главная кнопка
        [search_button, messages_button] # Дополнительные кнопки навигации
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_html(
        f'Привет, {user_name}! Добро пожаловать в TOOT. '
        'Нажми кнопку ниже, чтобы начать поиск пар!',
        reply_markup=reply_markup # Прикрепляем нашу клавиатуру
    )

    # --- Убрано set_bot_menu_buttons, так как ReplyKeyboardMarkup уже хорошо работает ---
    # set_bot_menu_buttons использовался бы для set_commands,
    # который показывает меню при клике на иконку "/".
    # Для постоянных кнопок внизу экрана лучше использовать ReplyKeyboardMarkup.
    # Если ты хочешь и меню-кнопки, и ReplyKeyboardMarkup, то нужно будет set_commands.
    # Для начала, ReplyKeyboardMarkup более заметна и удобна.


# Функция для обработки команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет справочное сообщение при команде /help."""
    await update.message.reply_text(
        'Я бот для знакомств TOOT.\n'
        'Нажми на одну из кнопок в нижнем меню, чтобы перейти в приложение:\n'
        '- "Начать знакомство" для основного приложения\n'
        '- "Поиск" для поиска новых знакомств\n'
        '- "Сообщения" для просмотра своих чатов.\n'
        'Или используй команду /start для начала.'
    )

# Функция для обработки любых текстовых сообщений
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отвечает пользователю, если он пишет просто текст."""
    await update.message.reply_text(
        'Пожалуйста, используй кнопки в меню или команды, чтобы взаимодействовать со мной. '
        'Нажми /start, чтобы начать, или /help для справки.'
    )

# --- Убрана неиспользуемая или потенциально запутывающая функция set_bot_menu_buttons ---
# async def set_bot_menu_buttons(bot):
#     """Устанавливает постоянные кнопки меню в Telegram (обычно для set_commands)."""
#     # Если захотим использовать set_commands (меню по клику на /), то здесь будет список Command.
#     # Например:
#     # from telegram import BotCommand
#     # await bot.set_my_commands([
#     #     BotCommand("start", "Запустить бота"),
#     #     BotCommand("help", "Показать помощь"),
#     # ])
#     print("Для постоянных кнопок под полем ввода используется ReplyKeyboardMarkup в start команде.")


def main():
    """Запускает бота."""
    print("Запускаем бота...")
    application = Application.builder().token(TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Запускаем бота
    print("Бот запущен. Ожидаю сообщений...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()