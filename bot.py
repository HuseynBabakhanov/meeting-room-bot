"""
Telegram бот для резервации митинг-рума
Удобный интерфейс для бронирования переговорной комнаты
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)
from database import Database
from config import BOT_TOKEN, GROUP_CHAT_ID
from translations import get_text, get_weekday, get_month

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
SELECTING_LANGUAGE, SELECTING_DATE, SELECTING_TIME, ENTERING_DURATION, ENTERING_DESCRIPTION = range(5)

# Инициализация базы данных
db = Database()


class MeetingRoomBot:
    """Класс для управления ботом бронирования переговорной"""
    
    def __init__(self):
        self.db = Database()
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_type = update.effective_chat.type
        
        # В личном чате всегда показываем выбор языка при первом запуске
        if chat_type == 'private':
            # Проверяем, выбирал ли пользователь язык в личном чате
            user_lang = self.db.get_user_language(user.id)
            
            # Если язык не выбран, показываем выбор
            if not user_lang or user_lang not in ['ru', 'az']:
                keyboard = [
                    [InlineKeyboardButton(get_text('ru', 'language_russian'), callback_data="lang_ru")],
                    [InlineKeyboardButton(get_text('az', 'language_azerbaijani'), callback_data="lang_az")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    get_text('ru', 'select_language'),
                    reply_markup=reply_markup
                )
            else:
                # Показываем главное меню на выбранном языке
                await self.show_main_menu(update, context, user_lang, user)
        else:
            # В группе показываем двуязычный интерфейс
            keyboard = [
                [InlineKeyboardButton("📅 Посмотреть брони / Bronları göstər", callback_data="view_bookings")],
                [InlineKeyboardButton("➕ Забронировать / Rezerv et", url=f"https://t.me/{context.bot.username}?start=booking")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = (
                "👋 Привет! Я бот для бронирования Meeting Room 2A\n"
                "👋 Salam! Mən Meeting Room 2A rezervasiya botuyam\n\n"
                "📋 RU: Нажмите кнопки для просмотра и создания броней\n"
                "📋 AZ: Rezervləri görmək və yaratmaq üçün düymələrə basın"
            )
            
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    async def select_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик выбора языка"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        language = query.data.split('_')[1]  # lang_ru -> ru
        
        # Сохраняем язык пользователя
        self.db.set_user_language(
            user_id=user.id,
            language=language,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username
        )
        
        await query.answer(get_text(language, 'language_selected'), show_alert=True)
        
        # Показываем главное меню
        keyboard = [
            [InlineKeyboardButton(get_text(language, 'btn_view_bookings'), callback_data="view_bookings")],
            [InlineKeyboardButton(get_text(language, 'btn_create_booking'), callback_data="create_booking")],
            [InlineKeyboardButton(get_text(language, 'btn_my_bookings'), callback_data="my_bookings")],
            [InlineKeyboardButton(get_text(language, 'btn_help'), callback_data="help")],
            [InlineKeyboardButton(get_text(language, 'btn_change_language'), callback_data="change_language")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = get_text(language, 'welcome', name=user.first_name)
        
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)
    
    async def change_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать меню смены языка"""
        query = update.callback_query
        await query.answer()
        
        keyboard = [
            [InlineKeyboardButton(get_text('ru', 'language_russian'), callback_data="lang_ru")],
            [InlineKeyboardButton(get_text('az', 'language_azerbaijani'), callback_data="lang_az")],
            [InlineKeyboardButton(get_text('ru', 'btn_back'), callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text('ru', 'select_language'),
            reply_markup=reply_markup
        )
    
    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE, lang: str = None, user = None):
        """Показать главное меню"""
        if not user:
            user = update.effective_user
        if not lang:
            lang = self.db.get_user_language(user.id)
        
        chat_type = update.effective_chat.type
        
        # В группе показываем упрощенное меню
        if chat_type in ['group', 'supergroup']:
            keyboard = [
                [InlineKeyboardButton(get_text(lang, 'btn_view_bookings'), callback_data="view_bookings")],
                [InlineKeyboardButton("➕ Забронировать (в личном чате)", url=f"https://t.me/{context.bot.username}?start=booking")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            welcome_text = (
                f"👋 Бот для бронирования Meeting Room 2A\n\n"
                f"📋 Просматривайте брони здесь\n"
                f"➕ Для бронирования нажмите кнопку ниже - откроется личный чат"
            )
        else:
            # В личном чате полное меню
            keyboard = [
                [InlineKeyboardButton(get_text(lang, 'btn_view_bookings'), callback_data="view_bookings")],
                [InlineKeyboardButton(get_text(lang, 'btn_create_booking'), callback_data="create_booking")],
                [InlineKeyboardButton(get_text(lang, 'btn_my_bookings'), callback_data="my_bookings")],
                [InlineKeyboardButton(get_text(lang, 'btn_help'), callback_data="help")],
                [InlineKeyboardButton(get_text(lang, 'btn_change_language'), callback_data="change_language")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            welcome_text = get_text(lang, 'welcome', name=user.first_name)
        
        if update.message:
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        else:
            await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)
    
    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать главное меню"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        chat_type = update.effective_chat.type
        
        # В группе показываем упрощенное меню
        if chat_type in ['group', 'supergroup']:
            keyboard = [
                [InlineKeyboardButton(get_text(lang, 'btn_view_bookings'), callback_data="view_bookings")],
                [InlineKeyboardButton("➕ Забронировать (в личном чате)", url=f"https://t.me/{context.bot.username}?start=booking")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = (
                f"👋 Бот для бронирования Meeting Room 2A\n\n"
                f"📋 Просматривайте брони здесь\n"
                f"➕ Для бронирования нажмите кнопку ниже"
            )
        else:
            # В личном чате полное меню
            keyboard = [
                [InlineKeyboardButton(get_text(lang, 'btn_view_bookings'), callback_data="view_bookings")],
                [InlineKeyboardButton(get_text(lang, 'btn_create_booking'), callback_data="create_booking")],
                [InlineKeyboardButton(get_text(lang, 'btn_my_bookings'), callback_data="my_bookings")],
                [InlineKeyboardButton(get_text(lang, 'btn_help'), callback_data="help")],
                [InlineKeyboardButton(get_text(lang, 'btn_change_language'), callback_data="change_language")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            text = get_text(lang, 'main_menu')
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup
        )
    
    async def view_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать все брони на сегодня и ближайшие дни"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        # Получаем брони на ближайшие 7 дней
        bookings = self.db.get_upcoming_bookings(days=7)
        
        if not bookings:
            text = get_text(lang, 'no_bookings')
        else:
            text = get_text(lang, 'upcoming_bookings')
            current_date = None
            
            for booking in bookings:
                booking_date = datetime.fromisoformat(booking['start_time']).date()
                
                # Добавляем заголовок даты
                if current_date != booking_date:
                    current_date = booking_date
                    date_str = self._format_date(booking_date, lang)
                    text += f"\n<b>{date_str}</b>\n"
                
                start = datetime.fromisoformat(booking['start_time'])
                end = datetime.fromisoformat(booking['end_time'])
                
                text += (
                    f"⏰ {start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n"
                    f"👤 {booking['user_name']}\n"
                    f"📝 {booking['description']}\n"
                    f"{'─' * 30}\n"
                )
        
        keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def start_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать процесс бронирования - выбор даты"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        # Создаем клавиатуру с датами на неделю вперед
        keyboard = []
        today = datetime.now().date()
        
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = self._format_date(date, lang)
            button_text = f"{date_str}"
            if i == 0:
                button_text = get_text(lang, 'today', date=date.strftime('%d.%m'))
            elif i == 1:
                button_text = get_text(lang, 'tomorrow', date=date.strftime('%d.%m'))
            
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"date_{date.isoformat()}"
            )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="back_to_menu")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'select_date'),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return SELECTING_DATE
    
    async def select_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор времени начала"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        # Сохраняем выбранную дату
        selected_date = query.data.split('_')[1]
        context.user_data['booking_date'] = selected_date
        
        # Получаем занятые слоты на выбранную дату
        bookings = self.db.get_bookings_by_date(selected_date)
        
        # Создаем клавиатуру с временными слотами (с 8:00 до 20:00)
        keyboard = []
        date_obj = datetime.fromisoformat(selected_date).date()
        
        for hour in range(8, 20):
            for minute in [0, 30]:
                time_str = f"{hour:02d}:{minute:02d}"
                time_obj = datetime.combine(date_obj, datetime.strptime(time_str, "%H:%M").time())
                
                # Проверяем, доступно ли это время
                is_available = self._is_time_available(time_obj, bookings)
                
                button_text = f"{'✅' if is_available else '❌'} {time_str}"
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"time_{time_str}" if is_available else "occupied"
                )])
        
        keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="create_booking")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        date_formatted = self._format_date(date_obj, lang)
        await query.edit_message_text(
            get_text(lang, 'select_time', date=date_formatted),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return SELECTING_TIME
    
    async def select_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выбор длительности бронирования"""
        query = update.callback_query
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        if query.data == "occupied":
            await query.answer(get_text(lang, 'time_occupied'), show_alert=True)
            return SELECTING_TIME
        
        await query.answer()
        
        # Сохраняем выбранное время
        selected_time = query.data.split('_')[1]
        context.user_data['booking_time'] = selected_time
        
        # Создаем клавиатуру с вариантами длительности
        keyboard = [
            [InlineKeyboardButton(get_text(lang, 'duration_30'), callback_data="duration_30")],
            [InlineKeyboardButton(get_text(lang, 'duration_60'), callback_data="duration_60")],
            [InlineKeyboardButton(get_text(lang, 'duration_90'), callback_data="duration_90")],
            [InlineKeyboardButton(get_text(lang, 'duration_120'), callback_data="duration_120")],
            [InlineKeyboardButton(get_text(lang, 'duration_180'), callback_data="duration_180")],
            [InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data=f"date_{context.user_data['booking_date']}")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(lang, 'select_duration', time=selected_time),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return ENTERING_DURATION
    
    async def enter_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запросить описание встречи"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        # Сохраняем длительность
        duration = int(query.data.split('_')[1])
        context.user_data['booking_duration'] = duration
        
        # Вычисляем время окончания
        date_str = context.user_data['booking_date']
        time_str = context.user_data['booking_time']
        start_time = datetime.fromisoformat(f"{date_str}T{time_str}")
        end_time = start_time + timedelta(minutes=duration)
        
        keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_cancel'), callback_data="create_booking")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            get_text(
                lang, 'enter_description',
                date=self._format_date(start_time.date(), lang),
                start_time=start_time.strftime('%H:%M'),
                end_time=end_time.strftime('%H:%M'),
                duration=duration
            ),
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return ENTERING_DESCRIPTION
    
    async def send_group_notification(self, context: ContextTypes.DEFAULT_TYPE, user, start_time, end_time, description):
        """Отправить уведомление о новой брони в группу"""
        if not GROUP_CHAT_ID:
            return  # Если GROUP_CHAT_ID не установлен, не отправляем уведомление
        
        try:
            # Форматируем сообщение для группы (двуязычное)
            message = (
                f"📢 <b>НОВАЯ БРОНЬ</b> / <b>YENİ REZERV</b>\n\n"
                f"👤 <b>Пользователь / Istifadəçi:</b> {user.full_name}\n"
                f"📅 <b>Дата / Tarix:</b> {start_time.strftime('%d.%m.%Y')}\n"
                f"⏰ <b>Время / Saat:</b> {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}\n"
                f"📝 <b>Описание / Təsvir:</b> {description}\n"
            )
            
            await context.bot.send_message(
                chat_id=int(GROUP_CHAT_ID),
                text=message,
                parse_mode='HTML'
            )
            logger.info(f"Уведомление о брони отправлено в группу {GROUP_CHAT_ID}")
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления в группу: {e}")
    

    async def confirm_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Подтверждение и создание брони"""
        description = update.message.text
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        # Получаем данные бронирования
        date_str = context.user_data['booking_date']
        time_str = context.user_data['booking_time']
        duration = context.user_data['booking_duration']
        
        start_time = datetime.fromisoformat(f"{date_str}T{time_str}")
        end_time = start_time + timedelta(minutes=duration)
        
        # Проверяем, не занято ли время
        if not self._check_availability(start_time, end_time):
            keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_back_to_menu'), callback_data="back_to_menu")]]
            await update.message.reply_text(
                get_text(lang, 'time_already_booked'),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return ConversationHandler.END
        
        # Создаем бронирование
        success = self.db.create_booking(
            user_id=user.id,
            user_name=user.full_name,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            description=description
        )
        
        if success:
            # Отправляем уведомление в группу
            await self.send_group_notification(context, user, start_time, end_time, description)
            
            keyboard = [
                [InlineKeyboardButton(get_text(lang, 'btn_my_bookings'), callback_data="my_bookings")],
                [InlineKeyboardButton(get_text(lang, 'btn_main_menu'), callback_data="back_to_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                get_text(
                    lang, 'booking_success',
                    date=self._format_date(start_time.date(), lang),
                    start_time=start_time.strftime('%H:%M'),
                    end_time=end_time.strftime('%H:%M'),
                    description=description
                ),
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                get_text(lang, 'booking_error')
            )
        
        # Очищаем данные
        context.user_data.clear()
        return ConversationHandler.END
    
    async def my_bookings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать брони пользователя"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        user_id = user.id
        bookings = self.db.get_user_bookings(user_id)
        
        if not bookings:
            text = get_text(lang, 'my_bookings_empty')
            keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="back_to_menu")]]
        else:
            text = get_text(lang, 'my_bookings_title')
            keyboard = []
            
            for booking in bookings:
                start = datetime.fromisoformat(booking['start_time'])
                end = datetime.fromisoformat(booking['end_time'])
                
                text += (
                    f"📅 {self._format_date(start.date(), lang)}\n"
                    f"⏰ {start.strftime('%H:%M')} - {end.strftime('%H:%M')}\n"
                    f"📝 {booking['description']}\n\n"
                )
                
                keyboard.append([InlineKeyboardButton(
                    get_text(lang, 'btn_cancel_booking', time=start.strftime('%d.%m %H:%M')),
                    callback_data=f"cancel_{booking['id']}"
                )])
            
            keyboard.append([InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="back_to_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def cancel_booking(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отменить бронирование"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        booking_id = int(query.data.split('_')[1])
        user_id = user.id
        
        # Проверяем, принадлежит ли бронь пользователю
        booking = self.db.get_booking(booking_id)
        
        if booking and booking['user_id'] == user_id:
            self.db.delete_booking(booking_id)
            await query.answer(get_text(lang, 'booking_cancelled'), show_alert=True)
        else:
            await query.answer(get_text(lang, 'cancel_error'), show_alert=True)
        
        # Обновляем список броней
        await self.my_bookings(update, context)
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать справку"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        lang = self.db.get_user_language(user.id)
        
        help_text = (
            get_text(lang, 'help_title') +
            get_text(lang, 'help_view') +
            get_text(lang, 'help_create') +
            get_text(lang, 'help_my') +
            get_text(lang, 'help_rules')
        )
        
        keyboard = [[InlineKeyboardButton(get_text(lang, 'btn_back'), callback_data="back_to_menu")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            help_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def cancel_operation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отменить текущую операцию"""
        context.user_data.clear()
        return ConversationHandler.END
    
    async def bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик добавления бота в группу"""
        # Проверяем, что бот был добавлен в чат
        if update.my_chat_member and update.my_chat_member.new_chat_member.status in ["member", "administrator"]:
            # Отправляем приветственное сообщение на двух языках
            keyboard = [
                [InlineKeyboardButton("📅 Посмотреть брони / Bronları göstər", callback_data="view_bookings")],
                [InlineKeyboardButton("➕ Забронировать / Rezerv et (в личном чате / şəxsi çatda)", url=f"https://t.me/{context.bot.username}?start=booking")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            text = (
                "👋 Привет! Я бот для бронирования Meeting Room 2A\n"
                "👋 Salam! Mən Meeting Room 2A rezervasiya botuyam\n\n"
                "📋 RU: Нажмите кнопки ниже для просмотра и создания броней\n"
                "📋 AZ: Rezervləri görmək və yaratmaq üçün düymələrə basın"
            )
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=reply_markup
            )
    
    async def new_member_joined(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик добавления нового участника в группу"""
        # Показываем интерфейс когда новый участник присоединяется к группе
        if update.message.new_chat_members:
            # Получаем информацию о новых участниках
            new_members = [member for member in update.message.new_chat_members if not member.is_bot]
            
            if new_members:
                # Проверяем язык первого участника (обычно добавляют по одному)
                user_lang = 'ru'  # по умолчанию
                if new_members[0].language_code:
                    # Определяем язык из настроек Telegram
                    if new_members[0].language_code.startswith('az'):
                        user_lang = 'az'
                    elif new_members[0].language_code.startswith('ru'):
                        user_lang = 'ru'
                    else:
                        # Для других языков показываем двуязычное приветствие
                        user_lang = 'both'
                
                keyboard = [
                    [InlineKeyboardButton("📅 Посмотреть брони / Bronları göstər", callback_data="view_bookings")],
                    [InlineKeyboardButton("➕ Забронировать / Rezerv et", url=f"https://t.me/{context.bot.username}?start=booking")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                names = ", ".join([member.first_name for member in new_members])
                
                if user_lang == 'ru':
                    text = (
                        f"👋 Добро пожаловать, {names}!\n\n"
                        "🏢 Здесь вы можете управлять бронированием Meeting Room 2A\n\n"
                        "📋 Используйте кнопки ниже для просмотра и создания броней"
                    )
                elif user_lang == 'az':
                    text = (
                        f"👋 Xoş gəlmisiniz, {names}!\n\n"
                        "🏢 Burada Meeting Room 2A rezervasiyasını idarə edə bilərsiniz\n\n"
                        "📋 Rezervləri görmək və yaratmaq üçün aşağıdakı düymələrdən istifadə edin"
                    )
                else:
                    text = (
                        f"👋 Добро пожаловать / Xoş gəlmisiniz, {names}!\n\n"
                        "🏢 RU: Здесь вы можете управлять бронированием Meeting Room 2A\n"
                        "🏢 AZ: Burada Meeting Room 2A rezervasiyasını idarə edə bilərsiniz\n\n"
                        "📋 Используйте кнопки ниже / Aşağıdakı düymələrdən istifadə edin"
                    )
                
                await update.message.reply_text(text, reply_markup=reply_markup)
    
    def _format_date(self, date, lang='ru'):
        """Форматирование даты"""
        weekday_str = get_weekday(lang, date.weekday())
        month_str = get_month(lang, date.month)
        
        return f"{weekday_str}, {date.day} {month_str}"
    
    def _is_time_available(self, time_obj, bookings):
        """Проверка доступности времени"""
        for booking in bookings:
            start = datetime.fromisoformat(booking['start_time'])
            end = datetime.fromisoformat(booking['end_time'])
            
            if start <= time_obj < end:
                return False
        
        return True
    
    def _check_availability(self, start_time, end_time):
        """Проверка доступности временного слота"""
        bookings = self.db.get_bookings_by_date(start_time.date().isoformat())
        
        for booking in bookings:
            booking_start = datetime.fromisoformat(booking['start_time'])
            booking_end = datetime.fromisoformat(booking['end_time'])
            
            # Проверяем пересечение временных интервалов
            if (start_time < booking_end and end_time > booking_start):
                return False
        
        return True


def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    bot = MeetingRoomBot()
    
    # Обработчик процесса бронирования
    booking_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(bot.start_booking, pattern="^create_booking$")],
        states={
            SELECTING_DATE: [CallbackQueryHandler(bot.select_time, pattern="^date_")],
            SELECTING_TIME: [CallbackQueryHandler(bot.select_duration, pattern="^time_|^occupied$")],
            ENTERING_DURATION: [CallbackQueryHandler(bot.enter_description, pattern="^duration_")],
            ENTERING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, bot.confirm_booking)],
        },
        fallbacks=[
            CallbackQueryHandler(bot.main_menu, pattern="^back_to_menu$"),
            CallbackQueryHandler(bot.start_booking, pattern="^create_booking$")
        ],
    )
    
    # Добавляем обработчики
    application.add_handler(ChatMemberHandler(bot.bot_added_to_group, ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bot.new_member_joined))
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CallbackQueryHandler(bot.select_language, pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(bot.change_language, pattern="^change_language$"))
    application.add_handler(booking_handler)
    application.add_handler(CallbackQueryHandler(bot.view_bookings, pattern="^view_bookings$"))
    application.add_handler(CallbackQueryHandler(bot.my_bookings, pattern="^my_bookings$"))
    application.add_handler(CallbackQueryHandler(bot.cancel_booking, pattern="^cancel_"))
    application.add_handler(CallbackQueryHandler(bot.show_help, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(bot.main_menu, pattern="^back_to_menu$"))
    
    # Запускаем бота
    logger.info("Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
