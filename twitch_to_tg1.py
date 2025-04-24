import os
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# Загружаем переменные из окружения
TWITCH_TOKEN    = os.environ['TWITCH_TOKEN_2']
TWITCH_CHANNEL  = os.environ['TWITCH_CHANNEL_2']
TELEGRAM_TOKEN  = os.environ['TELEGRAM_TOKEN_2']
TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID_2'])

class BridgeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN,
            prefix='!',                   # префикс для команд (необязательно)
            initial_channels=[TWITCH_CHANNEL]
        )
        # Инициализируем Telegram-клиент
        self.tg = TelegramBot(token=TELEGRAM_TOKEN)
        self.tg_chat_id = TELEGRAM_CHAT_ID

    async def event_ready(self):
        """Сработает при подключении к Twitch"""
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        """Срабатывает на каждое сообщение в чате"""
        # Чтобы бот не пересылал свои же сообщения:
        if message.author.name.lower() == self.nick.lower():
            return

        text = f'<{message.author.name}>: {message.content}'
        print("Отправляем в Telegram:", text)

        # Пересылаем в Telegram (async-версия API)
        await self.tg.send_message(chat_id=self.tg_chat_id, text=text)

        # Не забываем пропускать стандартную обработку (если нужны команды TwitchIO)
        await self.handle_commands(message)

if __name__ == '__main__':
    bot = BridgeBot()
    bot.run()


import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I'm alive!")

def run_fake_server():
    server = HTTPServer(('0.0.0.0', 10000), PingHandler)
    server.serve_forever()

# Запускаем сервер в фоновом потоке
threading.Thread(target=run_fake_server, daemon=True).start()
