import re
import asyncio
import requests
import logging
from telethon import TelegramClient, events

# --- 🔹 Включаем логирование для отладки ---
logging.basicConfig(level=logging.INFO)

# --- 🔹 Ваши данные для Telethon (User API) ---
API_ID = 21679979  # Ваш API ID
API_HASH = '14beec52e9c14c53628e3e038c6725c7'  # Ваш API Hash
PHONE_NUMBER = '+77003080198'  # Ваш номер Telegram

GROUP_ID = -1002344170059  # ID группы, откуда получаем сигналы
BOT_CHAT_ID = '5380447145'  # ID чата с вашим ботом

# --- 🔹 Подключение к Telegram через User API ---
client = TelegramClient('anon', API_ID, API_HASH)

# --- 🔹 Функция для отправки сообщений в бота ---
def send_to_bot(message):
    url = f"https://api.telegram.org/bot8141334032:AAEnpNjpF-iEZQzlxf4fjbwq_vQAiiA6yXw/sendMessage"
    data = {"chat_id": BOT_CHAT_ID, "text": message}
    response = requests.post(url, data=data)
    logging.info(f"Сообщение отправлено в бота: {message}, ответ: {response.status_code}")

# --- 🔹 Функция обработки сигналов ---
def parse_trade_signal(message_text):
    start_index = message_text.find("BINANCE:")
    if start_index == -1:
        return None

    cleaned_text = message_text[start_index:]
    parts = cleaned_text.split(',')
    if len(parts) < 3:
        return None

    platform_action, currency_pair, price_part = parts[0], parts[1], parts[2]
    action = platform_action.split('-')[1] if '-' in platform_action else None
    price = price_part.split('=')[1].strip() if '=' in price_part else None

    if action and currency_pair and price:
        return {
            'platform': 'BINANCE',
            'action': action.strip(),
            'currency_pair': currency_pair.strip(),
            'price': float(price)
        }
    return None

# --- 🔹 Обработчик сообщений из закрытой группы ---
@client.on(events.NewMessage(chats=GROUP_ID))
async def handler(event):
    text = event.raw_text
    logging.info(f"Получено сообщение из группы: {text}")  # ЛОГ ДЛЯ ПРОВЕРКИ!

    signal_info = parse_trade_signal(text)

    if signal_info:
        message = (f"Сигнал получен: {signal_info['action']} на {signal_info['currency_pair']} "
                   f"по цене {signal_info['price']}")
        logging.info(f"Пересылаем сигнал в бота: {message}")  # ЛОГ ДЛЯ ПРОВЕРКИ!
        send_to_bot(message)

# --- 🔹 Функция для теста без новых сообщений ---
class FakeEvent:
    def __init__(self, text):
        self.raw_text = text  # Telethon использует raw_text для сообщений

async def test_handler():
    logging.info("=== Запуск теста ===")

    # Создаем фейковое сообщение
    fake_event = FakeEvent("BINANCE:ENTER-LONG🟢,BTCUSDT,💲current price = 50000")

    # Вызываем handler() вручную
    await handler(fake_event)

    logging.info("=== Тест завершен ===")

# --- 🔹 Запускаем Telethon ---
async def start_client():
    await client.start(PHONE_NUMBER)
    logging.info("Telethon успешно подключен!")
    loop.create_task(test_handler())  # Запускаем тест
    await client.run_until_disconnected()

# --- 🔹 Запуск кода ---
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start_client())
