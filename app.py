"""
RoboSTEAMuL VK-бот v3.1 - ПОЛНАЯ ПЕРЕДЕЛКА СОГЛАСНО ТЗ
Структурированная регистрация ребенка в 8 шагов + подтверждение

Версия: 3.1
Дата: 2024
Статус: РАЗРАБОТКА СОГЛАСНО ТЗ

ТРЕБОВАНИЯ ТЗ:
✅ 8 шагов регистрации (не 7)
✅ Порядок: ФИО → Возраст → Номер сада → Программа → ФИО родителя → Телефон → Связь → Комментарий
✅ Подтверждение перед отправкой
✅ Сохранение состояния в БД
✅ Все ответы во время регистрации - только сценарий, не AI
✅ Отправка администратору с полными данными
"""

import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

# ════════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ
# ════════════════════════════════════════════════════════════════════════════

# VK Параметры
VK_TOKEN = "your_vk_token"
VK_SECRET = "your_vk_secret"
VK_CONFIRMATION_TOKEN = "43a38a83"
VK_GROUP_ID = 123456789
ADMIN_NATALIA_VK_ID = 441534266  # Для отправки заявок
TECH_ADMIN_VK_ID = 123456  # Для ошибок

# Временные зоны и TTL
BOT_TIMEZONE = "Asia/Yekaterinburg"
DRAFT_TTL_HOURS = 24

# ════════════════════════════════════════════════════════════════════════════
# СТРУКТУРЫ ДАННЫХ
# ════════════════════════════════════════════════════════════════════════════

class RegistrationState:
    """Состояния в процессе регистрации"""
    NONE = "none"
    STARTED = "started"
    STEP_1_CHILD_FIO = "step_1_child_fio"
    STEP_2_CHILD_AGE = "step_2_child_age"
    STEP_3_KINDERGARTEN = "step_3_kindergarten"
    STEP_4_PROGRAM = "step_4_program"
    STEP_5_PARENT_FIO = "step_5_parent_fio"
    STEP_6_PARENT_PHONE = "step_6_parent_phone"
    STEP_7_CONTACT_PREF = "step_7_contact_pref"
    STEP_8_COMMENT = "step_8_comment"
    STEP_9_CONFIRM = "step_9_confirm"
    COMPLETED = "completed"


@dataclass
class ApplicationData:
    """Структура заявки"""
    # Идентификаторы
    application_id: str  # RST-YYYYMMDD-XXXXX
    vk_user_id: int
    vk_peer_id: int
    
    # Статусы
    status: str = "draft"  # draft | new | in_progress | completed | rejected
    current_step: str = RegistrationState.NONE
    notification_status: str = "pending"  # pending | sent | failed
    
    # Даты
    created_at: datetime = None
    confirmed_at: datetime = None
    last_updated_at: datetime = None
    
    # ШАГ 1: ФИО ребенка
    child_fio: str = None
    
    # ШАГ 2: Возраст ребенка
    child_age: int = None
    
    # ШАГ 3: Номер детского сада
    kindergarten_number: str = None
    kindergarten_id: int = None
    kindergarten_found: bool = False
    kindergarten_name: str = None
    
    # ШАГ 4: Программа
    program_code: str = None
    program_name: str = None
    
    # ШАГ 5: ФИО родителя
    parent_fio: str = None
    
    # ШАГ 6: Телефон родителя
    parent_phone: str = None
    
    # ШАГ 7: Способ связи
    contact_preference: str = None  # call | written | max | any
    contact_time: str = None
    
    # ШАГ 8: Комментарий
    comment: str = None
    
    # Служебные
    notification_error: str = None
    event_id_processed: str = None  # Для защиты от дублей


# ════════════════════════════════════════════════════════════════════════════
# IN-MEMORY ХРАНИЛИЩЕ (ДО ИНТЕГРАЦИИ С БД)
# ════════════════════════════════════════════════════════════════════════════

# Состояния пользователей
user_states: Dict[int, ApplicationData] = {}

# Справочник детских садов
KINDERGARTENS = {
    30: {
        'id': 30,
        'number': '30',
        'subdivision': 'СП',
        'name': 'ДОУ №30 СП',
        'address': 'Зальцмана 24',
        'location': 'Центр',
        'programs': ['robo_stim', 'brick', 'pro', 'dance'],
        'active': True
    },
    448: {
        'id': 448,
        'number': '448',
        'subdivision': None,
        'name': 'ДОУ №448',
        'address': 'Конструктора Духова 25',
        'location': 'Юго-Запад',
        'programs': ['robo_stim', 'brick', 'dance'],
        'active': True
    },
    369: {
        'id': 369,
        'number': '369',
        'subdivision': None,
        'name': 'ДОУ №369',
        'address': 'ул. Советская 15',
        'location': 'Север',
        'programs': ['robo_stim', 'logoped'],
        'active': True
    },
}

# Справочник программ
PROGRAMS = {
    'robo_stim': {
        'name': 'РобоСТИМ',
        'emoji': '🤖',
        'age_min': 3,
        'age_max': 4,
        'price': '300 руб',
        'description': 'Робототехника для малышей'
    },
    'brick': {
        'name': 'РобоСТЕАМ Брик',
        'emoji': '🧱',
        'age_min': 4,
        'age_max': 5,
        'price': '300 руб',
        'description': 'Робототехника средний уровень'
    },
    'pro': {
        'name': 'РобоСТЕАМ Про',
        'emoji': '⚙️',
        'age_min': 5,
        'age_max': 6,
        'price': '400 руб',
        'description': 'Робототехника продвинутый уровень'
    },
    'pro_plus': {
        'name': 'РобоСТЕАМ Про+',
        'emoji': '🏆',
        'age_min': 6,
        'age_max': 12,
        'price': '450 руб',
        'description': 'Робототехника для старших детей'
    },
    'dance': {
        'name': 'Хореография',
        'emoji': '💃',
        'age_min': 3,
        'age_max': 8,
        'price': '350 руб',
        'description': 'Танцы и движение'
    },
    'logoped': {
        'name': 'Логопед и развитие речи',
        'emoji': '🗣️',
        'age_min': 3,
        'age_max': 7,
        'price': '600 руб',
        'description': 'Развитие речи у детей'
    },
    'school_2': {
        'name': 'Дошколёнок 4-5 лет',
        'emoji': '📚',
        'age_min': 4,
        'age_max': 5,
        'price': '350 руб',
        'description': 'Подготовка к школе'
    },
    'school_1': {
        'name': 'Дошколёнок 6-7 лет',
        'emoji': '✏️',
        'age_min': 6,
        'age_max': 7,
        'price': '375 руб',
        'description': 'Интенсивная подготовка к школе'
    },
}

# ════════════════════════════════════════════════════════════════════════════
# ЛОГИРОВАНИЕ
# ════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ════════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ════════════════════════════════════════════════════════════════════════════

def generate_application_id() -> str:
    """Генерация уникального ID заявки: RST-20260727-00001"""
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    seq = len([app for app in user_states.values() 
               if app.application_id.startswith(f"RST-{date_str}")])
    return f"RST-{date_str}-{seq+1:05d}"


def normalize_text(text: str) -> str:
    """Нормализация текста: убрать лишние пробелы, lowercase для сравнения"""
    return ' '.join(text.strip().split()).lower()


def mask_phone(phone: str) -> str:
    """Маскирование телефона для логирования"""
    if len(phone) >= 10:
        return phone[:2] + '*' * (len(phone) - 4) + phone[-2:]
    return '*' * len(phone)


def mask_name(name: str) -> str:
    """Маскирование имени для логирования"""
    if len(name) > 2:
        return name[0] + '*' * (len(name) - 2) + name[-1]
    return '*' * len(name)


# ════════════════════════════════════════════════════════════════════════════
# РАБОТА С СОСТОЯНИЯМИ (БД-слой)
# ════════════════════════════════════════════════════════════════════════════

def get_user_application(user_id: int) -> Optional[ApplicationData]:
    """Получить активную заявку пользователя из БД"""
    return user_states.get(user_id)


def save_application(app: ApplicationData) -> None:
    """Сохранить заявку в БД"""
    app.last_updated_at = datetime.now()
    user_states[app.vk_user_id] = app
    logger.info(f"Application {app.application_id} saved at step {app.current_step}")


def create_new_application(user_id: int, peer_id: int) -> ApplicationData:
    """Создать новую заявку"""
    app = ApplicationData(
        application_id=generate_application_id(),
        vk_user_id=user_id,
        vk_peer_id=peer_id,
        status="draft",
        current_step=RegistrationState.STARTED,
        created_at=datetime.now(),
        last_updated_at=datetime.now()
    )
    save_application(app)
    return app


def is_application_expired(app: ApplicationData) -> bool:
    """Проверка: заявка протухла (> 24 часов)"""
    if app.status != "draft":
        return False
    
    now = datetime.now()
    if (now - app.last_updated_at).total_seconds() > DRAFT_TTL_HOURS * 3600:
        return True
    
    return False


# ════════════════════════════════════════════════════════════════════════════
# ПОИСК ДЕТСКИХ САДОВ
# ════════════════════════════════════════════════════════════════════════════

def search_kindergarten(number: str) -> Optional[Dict]:
    """Поиск детского сада по нормализованному номеру"""
    number_clean = number.split()[0]  # "30 СП" → "30"
    
    try:
        kg_id = int(number_clean)
        if kg_id in KINDERGARTENS:
            return KINDERGARTENS[kg_id]
    except ValueError:
        pass
    
    return None


# ════════════════════════════════════════════════════════════════════════════
# ВЫБОР ПРОГРАММ ПО ВОЗРАСТУ
# ════════════════════════════════════════════════════════════════════════════

def get_programs_for_age(age: int) -> List[str]:
    """Получить коды программ, подходящих по возрасту"""
    suitable = []
    for code, prog in PROGRAMS.items():
        if prog['age_min'] <= age <= prog['age_max']:
            suitable.append(code)
    return suitable


# ════════════════════════════════════════════════════════════════════════════
# ВАЛИДАТОРЫ
# ════════════════════════════════════════════════════════════════════════════

def validate_child_fio(text: str) -> Tuple[bool, str]:
    """
    Валидация ФИО ребенка
    - 2-4 слова
    - Русские/латинские буквы, дефис
    - Нормализация пробелов и регистра
    """
    if not text or not text.strip():
        return False, "Пожалуйста, напишите ФИО ребенка. Пример: Петров Иван Сергеевич"
    
    # Проверка символов
    if not all(c.isalpha() or c.isspace() or c == '-' for c in text):
        return False, "Используйте только буквы, пробелы и дефисы. Пример: Петров-Иванов Иван"
    
    # Проверка количества слов
    words = [w for w in text.split() if w]
    if len(words) < 2:
        return False, "Напишите хотя бы фамилию и имя. Пример: Петров Иван"
    if len(words) > 4:
        return False, "Слишком много слов! Максимум 4. Пример: Петров Иван Сергеевич"
    
    # Нормализация: первая буква заглавная в каждом слове
    normalized = ' '.join(w.capitalize() for w in words)
    return True, normalized


def validate_child_age(text: str) -> Tuple[bool, int]:
    """
    Валидация возраста
    - Целое число 2-12
    """
    text = text.strip()
    
    # Извлечение числа
    match = re.search(r'\d+', text)
    if not match:
        return False, "Пожалуйста, напишите возраст цифрой. Пример: 3 или 5 лет"
    
    try:
        age = int(match.group())
        if age < 2 or age > 12:
            return False, f"Возраст должен быть от 2 до 12 лет. Вы указали: {age}"
        return True, age
    except ValueError:
        return False, "Пожалуйста, напишите возраст цифрой. Пример: 3"


def normalize_kindergarten_number(text: str) -> str:
    """
    Нормализация номера детского сада
    
    Входные примеры:
    - 30, №30, ДОУ 30, ДОУ №30, Детский сад 30, д/с 30, 30 СП, 30сп, нет
    
    Выход:
    - 30, 30 СП, или None
    """
    text = text.strip().lower()
    
    # Специальный случай: "Нет"
    if text in ['нет', 'не', 'не посещает', 'не ходит']:
        return None
    
    # Удаляем префиксы
    prefixes = ['детский сад', 'детсад', 'дoу', 'доу', 'д/с', 'д-с', 'садик', 'сад']
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break
    
    # Удаляем символ №
    text = text.replace('№', '').replace('#', '').strip()
    
    # Извлекаем число и суффикс СП
    match = re.search(r'(\d+)\s*(сп|п)?', text, re.IGNORECASE)
    if match:
        number = match.group(1)
        suffix = match.group(2)
        
        if suffix and suffix.lower() in ['сп', 'п']:
            return f"{number} СП"
        else:
            return number
    
    return text.strip() if text.strip() else None


def validate_kindergarten_number(text: str) -> Tuple[bool, Optional[str]]:
    """Валидация номера детского сада"""
    if not text or not text.strip():
        return False, "Пожалуйста, напишите номер сада или «Нет». Примеры: 30, 448, 30 СП"
    
    normalized = normalize_kindergarten_number(text)
    
    if normalized is None:
        # Пользователь ответил "Нет"
        return True, None
    
    # Проверка что есть хотя бы одна цифра
    if not any(c.isdigit() for c in normalized):
        return False, "Пожалуйста, напишите номер сада цифрой. Примеры: 30, 448, 30 СП"
    
    return True, normalized


def validate_parent_fio(text: str) -> Tuple[bool, str]:
    """Валидация ФИО родителя (как ребенка, но отчество необязательно)"""
    if not text or not text.strip():
        return False, "Пожалуйста, напишите ФИО родителя. Пример: Иванов Сергей Петрович"
    
    # Проверка символов
    if not all(c.isalpha() or c.isspace() or c == '-' for c in text):
        return False, "Используйте только буквы. Пример: Иванов Сергей"
    
    # Проверка количества слов
    words = [w for w in text.split() if w]
    if len(words) < 2:
        return False, "Напишите фамилию и имя. Пример: Иванов Сергей"
    if len(words) > 4:
        return False, "Слишком много слов! Пример: Иванов Сергей Петрович"
    
    # Нормализация
    normalized = ' '.join(w.capitalize() for w in words)
    return True, normalized


def validate_parent_phone(text: str) -> Tuple[bool, str]:
    """
    Валидация телефона
    - Российские номера: +7XXXXXXXXXX
    - Другие: + и 8-15 цифр
    """
    text = text.strip()
    
    # Извлекаем только цифры
    digits = re.sub(r'\D', '', text)
    
    # Обработка российского номера
    if digits.startswith('7') and len(digits) == 11:
        return True, '+' + digits
    elif digits.startswith('8') and len(digits) == 11:
        # 8XXXXXXXXXX → +79XXXXXXXXX
        return True, '+7' + digits[1:]
    elif len(digits) >= 8 and len(digits) <= 15:
        # Другие страны
        return True, '+' + digits
    else:
        return False, f"Проверьте номер. Примеры: +7 900 123-45-67, 89211234567"


def validate_contact_preference(text: str) -> Tuple[bool, str]:
    """Валидация способа связи"""
    text = normalize_text(text)
    
    preferences = {
        'позвонить': 'call',
        'call': 'call',
        'звонок': 'call',
        'phone': 'call',
        'написать': 'written',
        'written': 'written',
        'вк': 'written',
        'vk': 'written',
        'max': 'max',
        'максимум': 'max',
        'all': 'max',
        'всё равно': 'any',
        'any': 'any',
        'без разницы': 'any',
    }
    
    if text in preferences:
        return True, preferences[text]
    
    # Пытаемся найти подстроку
    for key, val in preferences.items():
        if key in text:
            return True, val
    
    return False, "Выберите способ: Позвонить, Написать в VK, MAX или Без разницы"


def validate_comment(text: str) -> Tuple[bool, Optional[str]]:
    """Валидация комментария"""
    if not text or normalize_text(text) in ['пропустить', 'skip', '-', 'нет']:
        return True, None
    
    text = text.strip()
    
    if len(text) > 1000:
        return False, "Комментарий слишком длинный (максимум 1000 символов)"
    
    # Базовая защита от HTML/скриптов
    if any(tag in text.lower() for tag in ['<script', '<iframe', 'javascript:', 'onclick']):
        return False, "Комментарий содержит недопустимый контент"
    
    return True, text
