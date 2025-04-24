import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# Загружаем переменные из окружения
TWITCH_TOKEN     = os.environ['TWITCH_TOKEN_2']
TWITCH_CHANNEL   = os.environ['TWITCH_CHANNEL_2']
TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN_2']
TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID_2'])

# Основной класс бота
class BridgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix='!',
            initial_channels=[TWITCH_CHANNEL]
        )
        self.tg = TelegramBot(token=TELEGRAM_TOKEN)
        self.tg_chat_id = TELEGRAM_CHAT_ID

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.author.name.lower() == self.nick.lower():
            return

        text = f'<{message.author.name}>: {message.content}'
        print("Отправляем в Telegram:", text)
        await self.tg.send_message(chat_id=self.tg_chat_id, text=text)
        await self.handle_commands(message)

# HTTP-сервер для Render (ping-keepalive)
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I'm alive!")

def run_fake_server():
    port = int(os.environ.get('PORT', 10000))  # обязательно int
    server = HTTPServer(('0.0.0.0', port), PingHandler)
    server.serve_forever()

# Запускаем "пустой" HTTP-сервер в фоне (для Render)
threading.Thread(target=run_fake_server, daemon=True).start()

# Запуск бота
if __name__ == '__main__':
    bot = BridgeBot()
    bot.run()
