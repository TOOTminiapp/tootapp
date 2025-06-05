# bot.py

import os
from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import database # Импортируем наш модуль для работы с БД

# ТВОЙ ТОКЕН ТЕЛЕГРАМ БОТА
TOKEN = "7782172857:AAGJY3aCID_EIBg6OPDPQiErIMEycMavhX4"

# !!! ВАЖНО: УКАЖИ ЗДЕСЬ URL ТВОЕГО БЭКЕНДА/WEB APP !!!
# Для локальной разработки используй localhost и порт, который будет использовать твой бэкенд (например, 8000)
# В будущем, когда развернешь на Render.com, здесь будет URL от Render.
WEB_APP_URL = "http://localhost:8000" # Пока так, потом это будет URL твоего развернутого Web App

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
        db_user_id = database.create_user_if_not_exists(user_id)
        print(f"Пользователь Telegram ID {user_id} (DB User ID: {db_user_id}) обработан.")
    except Exception as e:
        print(f"Ошибка БД при обработке пользователя {user_id}: {e}")
        await update.message.reply_text("Произошла ошибка при регистрации. Пожалуйста, попробуйте еще раз.")
        return

    # Создаем кнопку Web App
    keyboard = [
        [KeyboardButton("Начать знакомство!", web_app=WebAppInfo(url=WEB_APP_URL))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

    await update.message.reply_html(
        f'Привет, {user_name}! Добро пожаловать в TOOT. '
        'Нажми кнопку ниже, чтобы начать поиск пар!',
        reply_markup=reply_markup # Прикрепляем нашу клавиатуру
    )

    # Также устанавливаем меню для всего бота
    await set_bot_menu_buttons(context.bot)


# Функция для обработки команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет справочное сообщение при команде /help."""
    await update.message.reply_text(
        'Я бот для знакомств TOOT.\n'
        'Нажми на одну из кнопок в нижнем меню, чтобы перейти в приложение:\n'
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

# Функция для установки постоянных кнопок меню Telegram
async def set_bot_menu_buttons(bot):
    """Устанавливает постоянные кнопки меню в Telegram."""
    menu_buttons = [
        KeyboardButton("Поиск", web_app=WebAppInfo(url=WEB_APP_URL + "/search")), # Пример с путем
        KeyboardButton("Сообщения", web_app=WebAppInfo(url=WEB_APP_URL + "/messages")) # Пример с путем
    ]
    # Web App URL для кнопок меню должен быть полным
    await bot.set_chat_menu_button(
        menu_button=None # Сбрасываем старую, если есть
    )
    # Используем set_chat_menu_button для создания кнопки "Меню" в поле ввода
    # А для постоянных кнопок под полем ввода лучше использовать ReplyKeyboardMarkup
    # В данном случае, ReplyKeyboardMarkup устанавливается в `start` и остается видимой.
    # Если хотим, чтобы они были доступны через кнопку "Меню" (рядом с кнопкой камеры),
    # то это другая функция: set_commands.

    # Для показа кнопок под полем ввода (как в Тиндере)
    # Мы уже это делаем в `start` и оно останется.
    # Но для Menu Button, которая открывается по клику на иконку
    # рядом с полем ввода сообщения, нужно использовать set_commands.
    # Пока оставим то, что есть в start.
    print("Кнопки меню для Web App должны быть установлены через ReplyKeyboardMarkup в start команде.")
    print(f"URL для Web App: {WEB_APP_URL}")


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