"""
Модуль для работы с данными бронирований (JSON-based storage)
Управление бронированиями переговорной комнаты
"""

import json
import os
import logging
from datetime import datetime, timedelta, timezone

BAKU_TZ = timezone(timedelta(hours=4))

def now_baku():
    return datetime.now(BAKU_TZ).replace(tzinfo=None)
from typing import List, Dict, Optional
import threading

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с данными бронирований через JSON файлы"""
    
    def __init__(self, data_dir: str = "data"):
        """Инициализация хранилища"""
        self.data_dir = data_dir
        self.bookings_file = os.path.join(data_dir, "bookings.json")
        self.users_file = os.path.join(data_dir, "users.json")
        self.booking_id_file = os.path.join(data_dir, "booking_id.json")
        self.lock = threading.Lock()  # Для безопасного доступа из разных потоков
        
        # Создаем директорию если её нет
        os.makedirs(data_dir, exist_ok=True)
        
        logger.info("📁 JSON режим: хранение данных в файлах")
        self.init_db()
    
    def init_db(self):
        """Инициализация файлов данных"""
        try:
            # Инициализируем файлы если их нет
            if not os.path.exists(self.bookings_file):
                self._write_json(self.bookings_file, [])
                logger.info(f"✅ Создан файл бронирований: {self.bookings_file}")
            
            if not os.path.exists(self.users_file):
                self._write_json(self.users_file, {})
                logger.info(f"✅ Создан файл пользователей: {self.users_file}")
            
            if not os.path.exists(self.booking_id_file):
                self._write_json(self.booking_id_file, {"next_id": 1})
                logger.info(f"✅ Создан счетчик ID: {self.booking_id_file}")
            
            logger.info("✅ Инициализация завершена успешно")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации: {e}")
            raise
    
    def _read_json(self, filepath: str):
        """Читать JSON файл потокобезопасно"""
        with self.lock:
            try:
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        return json.load(f)
                return {} if 'users' in filepath else []
            except Exception as e:
                logger.error(f"Ошибка чтения {filepath}: {e}")
                return {} if 'users' in filepath else []
    
    def _write_json(self, filepath: str, data):
        """Писать JSON файл потокобезопасно"""
        with self.lock:
            try:
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                logger.error(f"Ошибка записи {filepath}: {e}")
    
    def get_user_language(self, user_id: int) -> Optional[str]:
        """Получить язык пользователя"""
        users = self._read_json(self.users_file)
        user = users.get(str(user_id))
        return user.get('language') if user else None
    
    def set_user_language(self, user_id: int, language: str, first_name: str = None, 
                         last_name: str = None, username: str = None):
        """Установить язык пользователя"""
        users = self._read_json(self.users_file)
        users[str(user_id)] = {
            'language': language,
            'first_name': first_name,
            'last_name': last_name,
            'username': username,
            'updated_at': datetime.now().isoformat()
        }
        self._write_json(self.users_file, users)
        logger.info(f"Пользователь {user_id} выбрал язык: {language}")
    
    def create_booking(self, user_id: int, user_name: str, start_time: str, 
                      end_time: str, description: str) -> bool:
        """Создать бронирование"""
        try:
            bookings = self._read_json(self.bookings_file)
            counter = self._read_json(self.booking_id_file)
            
            booking_id = counter.get('next_id', 1)
            
            booking = {
                'id': booking_id,
                'user_id': user_id,
                'user_name': user_name,
                'start_time': start_time,
                'end_time': end_time,
                'description': description,
                'created_at': datetime.now().isoformat(),
                'status': 'active'
            }
            
            bookings.append(booking)
            self._write_json(self.bookings_file, bookings)
            
            counter['next_id'] = booking_id + 1
            self._write_json(self.booking_id_file, counter)
            
            logger.info(f"✅ Бронирование #{booking_id} создано для {user_name}")
            return True
        except Exception as e:
            logger.error(f"Ошибка создания бронирования: {e}")
            return False
    
    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Получить брони пользователя"""
        bookings = self._read_json(self.bookings_file)
        user_bookings = [b for b in bookings if b['user_id'] == user_id and b['status'] == 'active']
        return sorted(user_bookings, key=lambda x: x['start_time'])
    
    def get_booking(self, booking_id: int) -> Optional[Dict]:
        """Получить бронь по ID"""
        bookings = self._read_json(self.bookings_file)
        for booking in bookings:
            if booking['id'] == booking_id:
                return booking
        return None
    
    def get_bookings_by_date(self, date_str: str) -> List[Dict]:
        """Получить брони на конкретную дату"""
        bookings = self._read_json(self.bookings_file)
        date_bookings = []
        
        for booking in bookings:
            if booking['status'] == 'active':
                start = datetime.fromisoformat(booking['start_time'])
                if start.date().isoformat() == date_str:
                    date_bookings.append(booking)
        
        return sorted(date_bookings, key=lambda x: x['start_time'])
    
    def get_all_bookings(self) -> List[Dict]:
        """Получить все активные брони"""
        bookings = self._read_json(self.bookings_file)
        return [b for b in bookings if b['status'] == 'active']
    
    def get_upcoming_bookings(self, days: int = 7) -> List[Dict]:
        """Получить предстоящие брони на ближайшие N дней"""
        bookings = self._read_json(self.bookings_file)
        now = now_baku()
        end_date = now + timedelta(days=days)
        
        upcoming = []
        for booking in bookings:
            if booking['status'] == 'active':
                start = datetime.fromisoformat(booking['start_time'])
                if now <= start <= end_date:
                    upcoming.append(booking)
        
        return sorted(upcoming, key=lambda x: x['start_time'])
    
    def cancel_booking(self, booking_id: int, user_id: int) -> bool:
        """Отменить бронирование"""
        try:
            bookings = self._read_json(self.bookings_file)
            
            for booking in bookings:
                if booking['id'] == booking_id and booking['user_id'] == user_id and booking['status'] == 'active':
                    booking['status'] = 'cancelled'
                    booking['cancelled_at'] = datetime.now().isoformat()
                    self._write_json(self.bookings_file, bookings)
                    logger.info(f"✅ Бронирование #{booking_id} отменено")
                    return True
            
            logger.warning(f"Бронирование #{booking_id} не найдено или уже отменено")
            return False
        except Exception as e:
            logger.error(f"Ошибка отмены бронирования: {e}")
            return False
    
    def cleanup_old_bookings(self, days: int = 30):
        """Удалить старые отменённые брони"""
        try:
            bookings = self._read_json(self.bookings_file)
            cutoff_date = datetime.now() - timedelta(days=days)
            
            filtered_bookings = []
            removed_count = 0
            
            for booking in bookings:
                if booking['status'] == 'cancelled':
                    cancelled_at = datetime.fromisoformat(booking.get('cancelled_at', booking['created_at']))
                    if cancelled_at < cutoff_date:
                        removed_count += 1
                        continue
                filtered_bookings.append(booking)
            
            self._write_json(self.bookings_file, filtered_bookings)
            if removed_count > 0:
                logger.info(f"🧹 Удалено {removed_count} старых отменённых бронирований")
        except Exception as e:
            logger.error(f"Ошибка очистки: {e}")
    
    def export_bookings(self, filename: str = "bookings_export.json"):
        """Экспортировать все брони в файл"""
        try:
            bookings = self._read_json(self.bookings_file)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(bookings, f, ensure_ascii=False, indent=2)
            logger.info(f"📤 Брони экспортированы в {filename}")
            return True
        except Exception as e:
            logger.error(f"Ошибка экспорта: {e}")
            return False
