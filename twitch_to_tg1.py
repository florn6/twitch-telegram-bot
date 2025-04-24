import os
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# 1) Вставьте сюда ваши токены и настройки:
TWITCH_TOKEN    = 'oauth:p1hp8v7fcmrandbarkqpt0nlpgu7fm'
TWITCH_CHANNEL  = 'forlorn_6'        # без #, например 'some_channel'
TELEGRAM_TOKEN  = '7554202854:AAG_BoWV3jscXVKMd0YqF5PwMrtybLEN7l4'     # токен от BotFather
TELEGRAM_CHAT_ID = 695808943                  # ваш chat_id (число, без кавычек)

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
