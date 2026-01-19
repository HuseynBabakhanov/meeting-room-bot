"""
Модуль для работы с базой данных (SQLite локально, PostgreSQL на сервере)
Управление бронированиями переговорной комнаты
"""

import sqlite3
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
import os
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных бронирований"""
    
    def __init__(self, db_name: str = "meeting_room.db"):
        """Инициализация базы данных"""
        db_url = os.getenv("DATABASE_URL")
        self.db_name = db_name
        self.is_postgres = db_url is not None and db_url.strip() != ""
        
        if self.is_postgres:
            # Преобразуем DigitalOcean URL формат в psycopg2 совместимый
            self.db_url = self._convert_db_url(db_url)
            logger.info(f"PostgreSQL режим: подключение к БД")
        else:
            self.db_url = None
            logger.info(f"SQLite режим: использую локальную БД {db_name}")
            
        self.init_db()
    
    def _convert_db_url(self, url: str) -> str:
        """Преобразуем DigitalOcean URL в формат для psycopg2"""
        if not url or url.strip() == "":
            logger.error("DATABASE_URL пуста!")
            return None
            
        # Если URL уже содержит 'postgresql://', используем его как есть
        if url.startswith('postgresql://'):
            # Заменяем 'username=' на 'user=' если есть
            url = url.replace('username=', 'user=')
            logger.info("DATABASE_URL успешно преобразована")
            return url
        # Если формат неправильный, логируем для отладки
        logger.warning(f"Необычный формат DATABASE_URL: {url[:50]}...")
        return url
    
    def get_connection(self):
        """Получить соединение с базой данных"""
        if self.is_postgres:
            if not self.db_url:
                logger.error("DATABASE_URL не установлена, переходим на SQLite")
                self.is_postgres = False
                conn = sqlite3.connect(self.db_name)
                conn.row_factory = sqlite3.Row
                return conn
            
            try:
                conn = psycopg2.connect(self.db_url)
                logger.info("Успешное подключение к PostgreSQL")
                return conn
            except Exception as e:
                logger.error(f"Ошибка подключения к PostgreSQL: {e}")
                logger.error(f"DATABASE_URL формат: {self.db_url[:50] if self.db_url else 'None'}...")
                raise
        else:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            return conn
    
    def init_db(self):
        """Инициализация структуры базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if self.is_postgres:
            # PostgreSQL синтаксис
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    user_name TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    language TEXT DEFAULT 'ru',
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    updated_at TIMESTAMP
                )
            ''')
            
            # Индексы для PostgreSQL
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON bookings(start_time)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON bookings(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
                ON bookings(status)
            ''')
        else:
            # SQLite синтаксис
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    description TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'ru',
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    updated_at TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON bookings(start_time)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON bookings(user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_status 
            ON bookings(status)
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("База данных инициализирована")
    
    def create_booking(
        self,
        user_id: int,
        user_name: str,
        start_time: str,
        end_time: str,
        description: str
    ) -> bool:
        """
        Создать новое бронирование
        
        Args:
            user_id: ID пользователя Telegram
            user_name: Имя пользователя
            start_time: Время начала (ISO format)
            end_time: Время окончания (ISO format)
            description: Описание встречи
            
        Returns:
            True если бронирование создано успешно
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            created_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT INTO bookings 
                (user_id, user_name, start_time, end_time, description, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user_name, start_time, end_time, description, created_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Создано бронирование: {user_name} с {start_time} до {end_time}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при создании бронирования: {e}")
            return False
    
    def get_upcoming_bookings(self, days: int = 7) -> List[Dict]:
        """
        Получить все предстоящие бронирования
        
        Args:
            days: Количество дней вперед
            
        Returns:
            Список бронирований
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            future = (datetime.now() + timedelta(days=days)).isoformat()
            
            cursor.execute('''
                SELECT * FROM bookings
                WHERE status = 'active'
                AND end_time > ?
                AND start_time < ?
                ORDER BY start_time
            ''', (now, future))
            
            bookings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return bookings
            
        except Exception as e:
            logger.error(f"Ошибка при получении бронирований: {e}")
            return []
    
    def get_bookings_by_date(self, date: str) -> List[Dict]:
        """
        Получить все бронирования на конкретную дату
        
        Args:
            date: Дата в формате YYYY-MM-DD
            
        Returns:
            Список бронирований
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            start_of_day = f"{date}T00:00:00"
            end_of_day = f"{date}T23:59:59"
            
            cursor.execute('''
                SELECT * FROM bookings
                WHERE status = 'active'
                AND start_time >= ?
                AND start_time <= ?
                ORDER BY start_time
            ''', (start_of_day, end_of_day))
            
            bookings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return bookings
            
        except Exception as e:
            logger.error(f"Ошибка при получении бронирований на дату {date}: {e}")
            return []
    
    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """
        Получить все активные бронирования пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список бронирований пользователя
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute('''
                SELECT * FROM bookings
                WHERE user_id = ?
                AND status = 'active'
                AND end_time > ?
                ORDER BY start_time
            ''', (user_id, now))
            
            bookings = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return bookings
            
        except Exception as e:
            logger.error(f"Ошибка при получении бронирований пользователя {user_id}: {e}")
            return []
    
    def get_booking(self, booking_id: int) -> Optional[Dict]:
        """
        Получить информацию о конкретном бронировании
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            Информация о бронировании или None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM bookings
                WHERE id = ?
            ''', (booking_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"Ошибка при получении бронирования {booking_id}: {e}")
            return None
    
    def delete_booking(self, booking_id: int) -> bool:
        """
        Отменить (удалить) бронирование
        
        Args:
            booking_id: ID бронирования
            
        Returns:
            True если бронирование отменено успешно
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Помечаем как отмененное вместо удаления
            cursor.execute('''
                UPDATE bookings
                SET status = 'cancelled'
                WHERE id = ?
            ''', (booking_id,))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Бронирование {booking_id} отменено")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при отмене бронирования {booking_id}: {e}")
            return False
    
    def cleanup_old_bookings(self, days: int = 30):
        """
        Очистить старые бронирования
        
        Args:
            days: Удалить бронирования старше указанного количества дней
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                DELETE FROM bookings
                WHERE end_time < ?
            ''', (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Удалено {deleted_count} старых бронирований")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке старых бронирований: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Получить статистику по бронированиям
        
        Returns:
            Словарь со статистикой
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Общее количество активных бронирований
            cursor.execute('''
                SELECT COUNT(*) as total FROM bookings
                WHERE status = 'active'
                AND end_time > ?
            ''', (datetime.now().isoformat(),))
            
            total_active = cursor.fetchone()['total']
            
            # Количество бронирований сегодня
            today = datetime.now().date().isoformat()
            cursor.execute('''
                SELECT COUNT(*) as today FROM bookings
                WHERE status = 'active'
                AND start_time LIKE ?
            ''', (f"{today}%",))
            
            today_count = cursor.fetchone()['today']
            
            # Самый активный пользователь
            cursor.execute('''
                SELECT user_name, COUNT(*) as count
                FROM bookings
                WHERE status = 'active'
                GROUP BY user_id
                ORDER BY count DESC
                LIMIT 1
            ''')
            
            top_user = cursor.fetchone()
            conn.close()
            
            return {
                'total_active': total_active,
                'today': today_count,
                'top_user': dict(top_user) if top_user else None
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            return {}
    
    def set_user_language(self, user_id: int, language: str, first_name: str = None, 
                         last_name: str = None, username: str = None) -> bool:
        """
        Установить язык пользователя
        
        Args:
            user_id: ID пользователя Telegram
            language: Код языка ('ru' или 'az')
            first_name: Имя пользователя
            last_name: Фамилия пользователя
            username: Username пользователя
            
        Returns:
            True если успешно
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            updated_at = datetime.now().isoformat()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, language, first_name, last_name, username, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, language, first_name, last_name, username, updated_at))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Язык пользователя {user_id} установлен: {language}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при установке языка: {e}")
            return False
    
    def get_user_language(self, user_id: int) -> str:
        """
        Получить язык пользователя
        
        Args:
            user_id: ID пользователя Telegram
            
        Returns:
            Код языка ('ru' или 'az'), по умолчанию 'ru'
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT language FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result['language'] if result else 'ru'
            
        except Exception as e:
            logger.error(f"Ошибка при получении языка: {e}")
            return 'ru'
