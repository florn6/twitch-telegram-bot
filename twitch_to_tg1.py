import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from twitchio.ext import commands
from telegram import Bot as TelegramBot

# Загружаем переменные из окружения
TWITCH_TOKEN     = os.environ['TWITCH_TOKEN']        # токен от аккаунта tw2tg_bot
TWITCH_CHANNEL   = os.environ['TWITCH_CHANNEL']      # имя канала, например forlorn_6
TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']      # токен Telegram-бота
TELEGRAM_CHAT_ID = int(os.environ['TELEGRAM_CHAT_ID'])  # ID, куда слать (например, твой ID)

# Основной Twitch->Telegram бот
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
        print(f'✅ Twitch бот запущен как {self.nick}')

    async def event_message(self, message):
        # Игнорируем свои собственные сообщения
        if message.author.name.lower() == self.nick.lower():
            return

        # Формируем сообщение
        text = f'<{message.author.name}>: {message.content}'
        
        # Логируем в консоль (Render лог)
        print(f'📩 Новое сообщение от {message.author.name}: {message.content}')
        print(f'⏩ Отправляем в Telegram: {text}')
        
        # Отправляем в Telegram
        await self.tg.send_message(chat_id=self.tg_chat_id, text=text)
        
        # Обработка команд, если будут
        await self.handle_commands(message)

# "Фальшивый" HTTP-сервер, чтобы Render не засыпал
class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"I'm alive!")

def run_fake_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), PingHandler)
    server.serve_forever()

# Запускаем сервер в фоне
threading.Thread(target=run_fake_server, daemon=True).start()

# Запуск Twitch-бота
if __name__ == '__main__':
    bot = BridgeBot()
    bot.run()
