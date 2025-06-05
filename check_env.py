import os
from dotenv import load_dotenv

load_dotenv()

print(f"Telegram Bot Token: {os.getenv('TELEGRAM_BOT_TOKEN')}")
print(f"Database URL: {os.getenv('DATABASE_URL')}")

if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('DATABASE_URL'):
    print("Environment variables loaded successfully!")
else:
    print("Failed to load one or more environment variables.")
