import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# Переменные окружения
TWITCH_TOKEN     = os.environ['TWITCH_TOKEN']
TWITCH_CHANNEL   = os.environ['TWITCH_CHANNEL']
TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])

# Twitch → Telegram бот
class BridgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix='!',
            initial_channels=[TWITCH_CHANNEL]
        )
        self.tg = TelegramBot(token=TELEGRAM_TOKEN)

    async def event_ready(self):
        pass

    async def event_message(self, message):
        if message.author.name.lower() == self.nick.lower():
            return

        text = f'🔥{message.author.name}: {message.content}'
        await self.tg.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
        await self.handle_commands(message)

# HTTP-сервер для Render
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I'm alive!")

def run_fake_server():
    port = int(os.environ.get('PORT', 10000))
    HTTPServer(('0.0.0.0', port), PingHandler).serve_forever()

# Запуск
if __name__ == '__main__':
    threading.Thread(target=run_fake_server, daemon=True).start()
    BridgeBot().run()
