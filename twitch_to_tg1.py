import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# Конфигурация (все секретные данные через переменные окружения)
CONFIG = {
    'TWITCH_TOKEN': os.getenv('TWITCH_TOKEN', 'oauth:19cot6n9t0mez7j80q7ft611wqrb3a'),  # Только для локального тестирования!
    'TWITCH_CHANNEL': os.getenv('TWITCH_CHANNEL', ''),  # Ваш канал в lowercase
    'TELEGRAM_TOKEN': os.getenv('TELEGRAM_TOKEN', ''),
    'TELEGRAM_CHAT_ID': int(os.getenv('TELEGRAM_CHAT_ID', 0))
}

class BridgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=CONFIG['TWITCH_TOKEN'],
            prefix='!',
            initial_channels=[CONFIG['TWITCH_CHANNEL']]
        )
        self.tg = TelegramBot(token=CONFIG['TELEGRAM_TOKEN'])
        self.tg_chat_id = CONFIG['TELEGRAM_CHAT_ID']

    async def event_ready(self):
        print(f'Бот подключен как | {self.nick}')

    async def event_message(self, message):
        if message.author.name.lower() == self.nick.lower():
            return

        text = f'<{message.author.name}>: {message.content}'
        try:
            await self.tg.send_message(chat_id=self.tg_chat_id, text=text)
        except Exception as e:
            print(f"Ошибка Telegram: {e}")

    async def event_error(self, error):
        print(f"Twitch ошибка: {error}")
        await self.close()

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def run_server():
    server = HTTPServer(('0.0.0.0', int(os.getenv('PORT', 10000))), HealthHandler)
    server.serve_forever()

if __name__ == '__main__':
    # Проверка конфигурации
    if not CONFIG['TWITCH_TOKEN'].startswith('oauth:'):
        print("ОШИБКА: Неверный формат Twitch токена")
        exit(1)
        
    if not CONFIG['TWITCH_CHANNEL']:
        print("ОШИБКА: Укажите TWITCH_CHANNEL")
        exit(1)

    threading.Thread(target=run_server, daemon=True).start()
    
    try:
        bot = BridgeBot()
        bot.run()
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        exit(1)
