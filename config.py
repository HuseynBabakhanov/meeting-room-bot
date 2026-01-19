"""
Конфигурация бота
"""

import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Токен бота (получите у @BotFather в Telegram)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Настройки базы данных
# DATABASE_URL = os.getenv("DATABASE_URL")  # Больше не нужна - используем JSON
DATABASE_NAME = "meeting_room.db"  # Больше не используется

# Настройки времени работы комнаты
ROOM_OPEN_HOUR = 8  # Комната открывается в 08:00
ROOM_CLOSE_HOUR = 20  # Комната закрывается в 20:00

# Доступные длительности бронирования (в минутах)
BOOKING_DURATIONS = [30, 60, 90, 120, 180]

# Максимальное количество дней для бронирования вперед
MAX_BOOKING_DAYS = 7

# Временные слоты (интервал между доступными временами)
TIME_SLOT_INTERVAL = 30  # минут

# Автоматическая очистка старых бронирований (дни)
AUTO_CLEANUP_DAYS = 30

# ID группы для уведомлений о бронировании (получите у @userinfobot в группе)
# Формат: -100123456789 (со знаком минус, если ID больше)
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # Опционально, если есть - будут уведомления в группу
