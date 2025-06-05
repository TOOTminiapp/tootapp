from fastapi import FastAPI, Request # <--- ЭТА СТРОКА ДОЛЖНА БЫТЬ ПЕРВОЙ В ИМПОРТАХ
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import os

app = FastAPI() # <--- FastAPI() теперь будет определено!

# --- Настройка для отдачи статических файлов (твоего React-приложения) ---
# Мы будем считать, что твои скомпилированные файлы React будут находиться в папке 'webapp/build'
# Пока этой папки нет, но мы ее создадим позже.
WEBAPP_BUILD_DIR = "webapp/build"

# Создаем директорию, если ее нет, чтобы избежать ошибок при первом запуске
os.makedirs(WEBAPP_BUILD_DIR, exist_ok=True)
# Создаем простую заглушку index.html, чтобы было что отдавать
if not os.path.exists(os.path.join(WEBAPP_BUILD_DIR, "index.html")):
    with open(os.path.join(WEBAPP_BUILD_DIR, "index.html"), "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>TOOT Web App</title>
            <style>
                body { font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background-color: #f0f0f0; }
                .container { text-align: center; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
                h1 { color: #333; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Привет из TOOT Web App!</h1>
                <p>Это твой будущий интерфейс знакомств.</p>
                <p>Он открылся внутри Telegram!</p>
            </div>
        </body>
        </html>
        """)

# Монтируем статические файлы. Это означает, что FastAPI будет отдавать файлы из этой директории
# по корневому URL (/). Например, если запрос /index.html, он ищет его в WEBAPP_BUILD_DIR.
app.mount("/", StaticFiles(directory=WEBAPP_BUILD_DIR, html=True), name="static")

# --- API Эндпоинты (пример) ---
# В будущем здесь будут эндпоинты для профилей, лайков, чатов и т.д.

@app.get("/api/hello")
async def hello_api():
    return {"message": "Привет от API TOOT!"}

@app.get("/api/user_info")
async def get_user_info(telegram_id: int):
    # Здесь в будущем будет логика получения инфо о пользователе из БД
    # Пока просто заглушка
    return {"telegram_id": telegram_id, "status": "Заглушка: информация о пользователе"}


# --- Важно: Маршрут для Web App ---
# Этот маршрут будет возвращать index.html, который будет загружаться внутри Telegram Web App.
# Если твой React-роутинг будет использовать History API (большинство так делают),
# то важно, чтобы все пути, которые не являются API-эндпоинтами, возвращали index.html.
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def serve_webapp(request: Request, full_path: str):
    # Отдаем index.html для всех маршрутов, не соответствующих API
    # Это нужно для клиентского роутинга React
    return FileResponse(os.path.join(WEBAPP_BUILD_DIR, "index.html"))

