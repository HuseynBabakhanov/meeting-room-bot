"""
Переводы для бота на русский и азербайджанский языки
"""

TRANSLATIONS = {
    'ru': {
        # Кнопки выбора языка
        'select_language': 'Выберите язык / Dil seçin',
        'language_russian': '🇷🇺 Русский',
        'language_azerbaijani': '🇦🇿 Azərbaycan',
        'language_selected': '✅ Язык выбран',
        
        # Приветствие
        'welcome': "Привет, {name}! 👋\n\nЯ помогу вам забронировать переговорную комнату.\nВыберите действие:",
        
        # Кнопки главного меню
        'btn_view_bookings': '📅 Посмотреть брони',
        'btn_create_booking': '➕ Забронировать комнату',
        'btn_my_bookings': '🗑 Мои брони',
        'btn_help': 'ℹ️ Помощь',
        'btn_back': '◀️ Назад',
        'btn_cancel': '◀️ Отмена',
        'btn_confirm': '✅ Подтвердить',
        'btn_back_to_menu': '◀️ Назад в меню',
        'btn_main_menu': '◀️ Главное меню',
        'btn_change_language': '🌐 Сменить язык',
        
        # Главное меню
        'main_menu': 'Главное меню. Выберите действие:',
        
        # Просмотр броней
        'no_bookings': '📅 На ближайшие 7 дней броней нет.\n\nКомната свободна!',
        'upcoming_bookings': '📅 <b>Брони на ближайшие 7 дней:</b>\n\n',
        
        # Процесс бронирования
        'select_date': '📅 <b>Выберите дату бронирования:</b>',
        'select_time': '🕐 <b>Выберите время начала</b>\n\nДата: {date}\n✅ - свободно, ❌ - занято',
        'select_duration': '⏱ <b>Выберите длительность</b>\n\nНачало: {time}',
        'enter_description': '📝 <b>Введите описание встречи</b>\n\nДата: {date}\nВремя: {start_time} - {end_time}\nДлительность: {duration} мин\n\nНапишите, для чего нужна комната:',
        
        # Длительности
        'duration_30': '30 минут',
        'duration_60': '1 час',
        'duration_90': '1.5 часа',
        'duration_120': '2 часа',
        'duration_180': '3 часа',
        
        # Дни недели
        'today': 'Сегодня ({date})',
        'tomorrow': 'Завтра ({date})',
        'monday': 'Пн',
        'tuesday': 'Вт',
        'wednesday': 'Ср',
        'thursday': 'Чт',
        'friday': 'Пт',
        'saturday': 'Сб',
        'sunday': 'Вс',
        
        # Месяцы
        'january': 'января',
        'february': 'февраля',
        'march': 'марта',
        'april': 'апреля',
        'may': 'мая',
        'june': 'июня',
        'july': 'июля',
        'august': 'августа',
        'september': 'сентября',
        'october': 'октября',
        'november': 'ноября',
        'december': 'декабря',
        
        # Подтверждение и ошибки
        'time_occupied': 'Это время занято!',
        'booking_success': '✅ <b>Бронирование создано!</b>\n\n📅 Дата: {date}\n⏰ Время: {start_time} - {end_time}\n📝 Описание: {description}',
        'booking_error': '❌ Произошла ошибка при создании бронирования. Попробуйте еще раз.',
        'time_already_booked': '❌ К сожалению, это время уже забронировано.\nПопробуйте выбрать другое время.',
        
        # Мои брони
        'my_bookings_empty': 'У вас пока нет активных бронирований.',
        'my_bookings_title': '<b>Ваши бронирования:</b>\n\n',
        'btn_cancel_booking': '🗑 Отменить ({time})',
        'booking_cancelled': '✅ Бронирование отменено',
        'cancel_error': '❌ Ошибка при отмене',
        
        # Справка
        'help_title': '<b>ℹ️ Справка по использованию бота</b>\n\n<b>Основные функции:</b>\n\n',
        'help_view': '📅 <b>Посмотреть брони</b> - показывает все брони на ближайшую неделю\n\n',
        'help_create': '➕ <b>Забронировать комнату</b> - создать новое бронирование:\n   1. Выберите дату\n   2. Выберите время начала\n   3. Выберите длительность\n   4. Опишите цель встречи\n\n',
        'help_my': '🗑 <b>Мои брони</b> - ваши активные бронирования с возможностью отмены\n\n',
        'help_rules': '<b>Правила:</b>\n• Комнату можно бронировать с 08:00 до 20:00\n• Минимальная длительность - 30 минут\n• Вы можете отменить только свои брони\n• Бронировать можно на 7 дней вперед',
    },
    
    'az': {
        # Kнопки выбора языка
        'select_language': 'Выберите язык / Dil seçin',
        'language_russian': '🇷🇺 Русский',
        'language_azerbaijani': '🇦🇿 Azərbaycan',
        'language_selected': '✅ Dil seçildi',
        
        # Приветствие
        'welcome': "Salam, {name}! 👋\n\nMən sizə görüş otağını rezerv etməyə kömək edəcəyəm.\nƏməliyyatı seçin:",
        
        # Кнопки главного меню
        'btn_view_bookings': '📅 Rezervləri göstər',
        'btn_create_booking': '➕ Otağı rezerv et',
        'btn_my_bookings': '🗑 Mənim rezervlərim',
        'btn_help': 'ℹ️ Kömək',
        'btn_back': '◀️ Geri',
        'btn_cancel': '◀️ Ləğv et',
        'btn_confirm': '✅ Təsdiq et',
        'btn_back_to_menu': '◀️ Menyuya qayıt',
        'btn_main_menu': '◀️ Əsas menyu',
        'btn_change_language': '🌐 Dili dəyiş',
        
        # Главное меню
        'main_menu': 'Əsas menyu. Əməliyyatı seçin:',
        
        # Просмотр броней
        'no_bookings': '📅 Yaxın 7 gün üçün rezerv yoxdur.\n\nOtaq boşdur!',
        'upcoming_bookings': '📅 <b>Yaxın 7 gün üçün rezervlər:</b>\n\n',
        
        # Процесс бронирования
        'select_date': '📅 <b>Rezerv tarixini seçin:</b>',
        'select_time': '🕐 <b>Başlama vaxtını seçin</b>\n\nTarix: {date}\n✅ - boş, ❌ - məşğul',
        'select_duration': '⏱ <b>Müddəti seçin</b>\n\nBaşlama: {time}',
        'enter_description': '📝 <b>Görüşün təsvirini daxil edin</b>\n\nTarix: {date}\nVaxt: {start_time} - {end_time}\nMüddət: {duration} dəq\n\nOtaq nə üçün lazımdır:',
        
        # Длительности
        'duration_30': '30 dəqiqə',
        'duration_60': '1 saat',
        'duration_90': '1.5 saat',
        'duration_120': '2 saat',
        'duration_180': '3 saat',
        
        # Дни недели
        'today': 'Bu gün ({date})',
        'tomorrow': 'Sabah ({date})',
        'monday': 'Be',
        'tuesday': 'Ça',
        'wednesday': 'Çə',
        'thursday': 'Ca',
        'friday': 'Cü',
        'saturday': 'Şə',
        'sunday': 'Ba',
        
        # Месяцы
        'january': 'yanvar',
        'february': 'fevral',
        'march': 'mart',
        'april': 'aprel',
        'may': 'may',
        'june': 'iyun',
        'july': 'iyul',
        'august': 'avqust',
        'september': 'sentyabr',
        'october': 'oktyabr',
        'november': 'noyabr',
        'december': 'dekabr',
        
        # Подтверждение и ошибки
        'time_occupied': 'Bu vaxt məşğuldur!',
        'booking_success': '✅ <b>Rezerv yaradıldı!</b>\n\n📅 Tarix: {date}\n⏰ Vaxt: {start_time} - {end_time}\n📝 Təsvir: {description}',
        'booking_error': '❌ Rezerv yaradılarkən xəta baş verdi. Yenidən cəhd edin.',
        'time_already_booked': '❌ Təəssüf ki, bu vaxt artıq rezerv edilib.\nBaşqa vaxt seçin.',
        
        # Мои брони
        'my_bookings_empty': 'Hələ aktiv rezerviniz yoxdur.',
        'my_bookings_title': '<b>Sizin rezervləriniz:</b>\n\n',
        'btn_cancel_booking': '🗑 Ləğv et ({time})',
        'booking_cancelled': '✅ Rezerv ləğv edildi',
        'cancel_error': '❌ Ləğv edərkən xəta',
        
        # Справка
        'help_title': '<b>ℹ️ Botdan istifadə üzrə kömək</b>\n\n<b>Əsas funksiyalar:</b>\n\n',
        'help_view': '📅 <b>Rezervləri göstər</b> - yaxın həftə üçün bütün rezervləri göstərir\n\n',
        'help_create': '➕ <b>Otağı rezerv et</b> - yeni rezerv yaradın:\n   1. Tarixi seçin\n   2. Başlama vaxtını seçin\n   3. Müddəti seçin\n   4. Görüşün məqsədini yazın\n\n',
        'help_my': '🗑 <b>Mənim rezervlərim</b> - aktiv rezervləriniz və ləğv etmək imkanı\n\n',
        'help_rules': '<b>Qaydalar:</b>\n• Otağı 08:00-dan 20:00-a kimi rezerv etmək olar\n• Minimum müddət - 30 dəqiqə\n• Yalnız öz rezervlərinizi ləğv edə bilərsiniz\n• 7 gün qabaqcadan rezerv etmək olar',
    }
}


def get_text(lang, key, **kwargs):
    """Получить переведенный текст"""
    text = TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def get_weekday(lang, weekday):
    """Получить название дня недели"""
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    return get_text(lang, days[weekday])


def get_month(lang, month):
    """Получить название месяца"""
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    return get_text(lang, months[month - 1])
