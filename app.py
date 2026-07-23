#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 RoboSTEAMuL VK Bot - Улучшенная версия 2.0
Функции: Приветствие, Программы, Филиалы, Цены, Контакты, Запись
Бот отвечает только на входящие сообщения (без лишних отправок)
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.utils import get_random_id
from datetime import datetime
import sqlite3
import json
from difflib import SequenceMatcher

# ===== ЛОГГЕР =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ПЕРЕМЕННЫЕ =====
load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
API_VERSION = os.getenv('API_VERSION', '5.131')
VK_SECRET_KEY = os.getenv('VK_SECRET_KEY', '')
VK_CONFIRMATION_CODE = os.getenv('VK_CONFIRMATION_CODE', '')

# ===== ПРОВЕРКА =====
if not VK_TOKEN or not GROUP_ID:
    logger.error("❌ VK_TOKEN или GROUP_ID не установлены!")
    raise ValueError("VK_TOKEN и GROUP_ID обязательны")

logger.info("✅ VK_TOKEN загружен")
logger.info(f"✅ GROUP_ID: {GROUP_ID}")

# ===== FLASK =====
app = Flask(__name__)

# ===== БАЗА ДАННЫХ =====
REGISTRATIONS_DB = 'registrations.db'

def init_registrations_db():
    """Инициализировать базу данных для записей"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                child_name TEXT NOT NULL,
                child_age INTEGER NOT NULL,
                program TEXT NOT NULL,
                branch TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_state (
                user_id INTEGER PRIMARY KEY,
                state TEXT DEFAULT 'default',
                registration_data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ База данных записей инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")

# ===== VK API =====
vk = None
try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    logger.info("✅ VK API успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка VK API: {e}")

# ===== БОТ ИНФОРМАЦИЯ =====
BOT_NAME = "RoboSTEAMuL Bot"
BOT_VERSION = "2.0 Pro"
SCHOOL_WEBSITE = "robosteamul.com"
SCHOOL_EMAIL = "info@robosteamul.com"

# ===== КОНТАКТЫ =====
CONTACTS = {
    'phone_1': {
        'name': 'Наталья',
        'number': '+7 (922) 014-44-94'
    },
    'phone_2': {
        'name': 'Ксения',
        'number': '+7 (904) 805-25-61'
    },
    'phone_3': {
        'name': 'Жанна',
        'number': '+7 (951) 239-86-49'
    }
}

WORK_SCHEDULE = {
    'weekdays': 'Пн-Пт',
    'time': '09:00-18:00',
    'weekends': 'Выходные'
}

# ===== ФИЛИАЛЫ =====
BRANCHES_LIST = [
    {'name': 'ДОУ №30', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №30СП', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №10 Копейск', 'programs': ['Робототехника']},
    {'name': 'ДОУ №18СП', 'programs': ['Робототехника']},
    {'name': 'ДОУ №24 Копейск', 'programs': ['Робототехника']},
    {'name': 'ДОУ №44', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №44СП', 'programs': ['Хореография']},
    {'name': 'ДОУ №48', 'programs': ['Робототехника']},
    {'name': 'ДОУ №66', 'programs': ['Хореография']},
    {'name': 'ДОУ №66СП', 'programs': ['Робототехника']},
    {'name': 'ДОУ №221СП', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №339', 'programs': ['Робототехника']},
    {'name': 'ДОУ №351', 'programs': ['Робототехника']},
    {'name': 'ДОУ №366', 'programs': ['Робототехника']},
    {'name': 'ДОУ №369', 'programs': ['Робототехника']},
    {'name': 'ДОУ №413', 'programs': ['Робототехника']},
    {'name': 'ДОУ №416', 'programs': ['Робототехника']},
    {'name': 'ДОУ №418', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №421', 'programs': ['Робототехника']},
    {'name': 'ДОУ №428', 'programs': ['Робототехника']},
    {'name': 'ДОУ №444', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №448', 'programs': ['Робототехника']},
    {'name': 'ДОУ №448СП', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №450', 'programs': ['Робототехника']},
    {'name': 'ДОУ №475', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'Гимназия №76', 'programs': ['Робототехника']}
]

# ===== ПРОГРАММЫ =====
PROGRAMS_INFO = {
    'robosteam': {
        'name': '🤖 РобоSTEAM (3-4 года)',
        'age': '3-4 года',
        'price': '300 руб./занятие',
        'duration': '30 минут',
    },
    'brik': {
        'name': '🧱 РобоSTEAM Брик (5-6 лет)',
        'age': '5-6 лет',
        'price': '300 руб./занятие',
        'duration': '60 минут',
    },
    'pro': {
        'name': '⚙️ РобоSTEAM Про (6-8 лет)',
        'age': '6-8 лет',
        'price': '400 руб./занятие',
        'duration': '60 минут',
    },
    'choreography': {
        'name': '💃 Хореография (3-8 лет)',
        'age': '3-8 лет',
        'price': '350 руб./занятие',
        'duration': '30-60 минут',
    },
    'doshkolenok_1': {
        'name': '👶 Дошколёнок - Подготовка к школе (4-5 лет)',
        'age': '4-5 лет',
        'price': '400 руб./занятие',
        'duration': '60 минут',
    },
    'doshkolenok_2': {
        'name': '👶 Дошколёнок - Подготовка к школе (6-7 лет)',
        'age': '6-7 лет',
        'price': '400 руб./занятие',
        'duration': '60 минут',
    },
    'logoped': {
        'name': '🗣️ Логопед (3-7 лет)',
        'age': '3-7 лет',
        'price': '600 руб./занятие',
        'duration': '60 минут',
    },
    'diagnostics': {
        'name': '📋 Диагностика',
        'age': '3-7 лет',
        'price': '800 руб.',
        'duration': 'Одно обследование',
    },
}

# ===== ФУНКЦИИ БАЗЫ ДАННЫХ =====

def get_user_state(user_id):
    """Получить состояние пользователя"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        c.execute('SELECT state, registration_data FROM user_state WHERE user_id = ?', (user_id,))
        row = c.fetchone()
        conn.close()
        
        if row:
            return row[0], json.loads(row[1]) if row[1] else {}
        return 'default', {}
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния: {e}")
        return 'default', {}

def set_user_state(user_id, state, data=None):
    """Установить состояние пользователя"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        data_json = json.dumps(data) if data else '{}'
        
        c.execute('''
            INSERT OR REPLACE INTO user_state (user_id, state, registration_data, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, state, data_json))
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ Ошибка установки состояния: {e}")

def save_registration(user_id, child_name, child_age, program, branch, phone):
    """Сохранить запись в БД"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO registrations (user_id, child_name, child_age, program, branch, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, child_name, child_age, program, branch, phone))
        
        conn.commit()
        conn.close()
        logger.info(f"✅ Запись сохранена для пользователя {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения записи: {e}")
        return False

# ===== ФУНКЦИИ ОТПРАВКИ =====

def send_message(user_id, message):
    """Отправить сообщение"""
    if not vk:
        logger.error("❌ VK API не инициализирован")
        return False
    
    try:
        logger.info(f"📤 Отправляю сообщение пользователю {user_id}")
        vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            v=API_VERSION
        )
        logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return False

# ===== ФУНКЦИИ ПРИВЕТСТВИЯ =====

def get_greeting():
    """Приветствие в зависимости от времени суток"""
    current_hour = datetime.now().hour
    
    # Определяем время суток
    if 5 <= current_hour < 12:
        greeting = """🌅 Доброе утро!

Рады видеть вас в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество и логику.

⏰ Режим работы компании:
• Пн-Пт: 09:00-18:00
• Сб-Вс: Выходные
• 🤖 Чат-бот отвечает 24/7

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
    
    elif 12 <= current_hour < 17:
        greeting = """🌤️ Добрый день!

Добро пожаловать в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество и логику.

⏰ Режим работы компании:
• Пн-Пт: 09:00-18:00
• Сб-Вс: Выходные
• 🤖 Чат-бот отвечает 24/7

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
    
    elif 17 <= current_hour < 21:
        greeting = """🌆 Добрый вечер!

Добро пожаловать в RoboSTEAMuL! 🤖

Мы помогаем детям 3-8 лет развивать творчество и логику.

⏰ Режим работы компании:
• Пн-Пт: 09:00-18:00
• Сб-Вс: Выходные
• 🤖 Чат-бот отвечает 24/7

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
    
    else:
        greeting = """🌙 Добрый ночи!

Добро пожаловать в RoboSTEAMuL! 🤖

Мы помогаем детям 3-8 лет развивать творчество и логику.
Наш чат-бот отвечает 24/7!

⏰ Режим работы компании:
• Пн-Пт: 09:00-18:00
• Сб-Вс: Выходные
• 🤖 Чат-бот отвечает 24/7

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
    
    return greeting

# ===== ФУНКЦИИ МЕНЮ =====

def get_programs():
    """Список программ"""
    response = """📚 НАШИ ПРОГРАММЫ:

🤖 РобоSTEAM (3-4 года)
   Возраст: 3-4 года | Время: 30 минут | Цена: 300 руб./занятие

🧱 РобоSTEAM Брик (5-6 лет)
   Возраст: 5-6 лет | Время: 60 минут | Цена: 300 руб./занятие

⚙️ РобоSTEAM Про (6-8 лет)
   Возраст: 6-8 лет | Время: 60 минут | Цена: 400 руб./занятие

💃 Хореография (3-8 лет)
   Возраст: 3-8 лет | Время: 30-60 минут | Цена: 350 руб./занятие

👶 Дошколёнок - Подготовка к школе (4-5 лет)
   Возраст: 4-5 лет | Время: 60 минут | Цена: 400 руб./занятие

👶 Дошколёнок - Подготовка к школе (6-7 лет)
   Возраст: 6-7 лет | Время: 60 минут | Цена: 400 руб./занятие

🗣️ Логопед (3-7 лет)
   Возраст: 3-7 лет | Время: 60 минут | Цена: 600 руб./занятие

📋 Диагностика
   Возраст: 3-7 лет | Цена: 800 руб.

👉 Напишите 'записаться' для регистрации!"""
    
    return response

def get_prices():
    """Таблица цен"""
    response = """💰 ТАБЛИЦА ЦЕН:

🤖 РобоSTEAM (3-4 года) - 300 руб./занятие (30 мин)
🧱 РобоSTEAM Брик (5-6 лет) - 300 руб./занятие (60 мин)
⚙️ РобоSTEAM Про (6-8 лет) - 400 руб./занятие (60 мин)
💃 Хореография (3-8 лет) - 350 руб./занятие (30-60 мин)
👶 Дошколёнок (4-5 лет) - 400 руб./занятие (60 мин)
👶 Дошколёнок (6-7 лет) - 400 руб./занятие (60 мин)
🗣️ Логопед (3-7 лет) - 600 руб./занятие (60 мин)
📋 Диагностика - 800 руб.

ℹ️ Первое занятие БЕСПЛАТНО! 🎁

📞 Вопросы о ценах? Свяжитесь с нами:
Наталья: +7 (922) 014-44-94
Ксения: +7 (904) 805-25-61
Жанна: +7 (951) 239-86-49"""
    
    return response

def get_contacts():
    """Контактная информация"""
    response = """📞 НАШИ КОНТАКТЫ:

👩‍💼 Наталья: +7 (922) 014-44-94
👩‍💼 Ксения: +7 (904) 805-25-61
👩‍💼 Жанна: +7 (951) 239-86-49

📧 Email: info@robosteamul.com
🌐 Сайт: robosteamul.com

⏰ Режим работы:
• Пн-Пт: 09:00-18:00
• Сб-Вс: Выходные
• 🤖 Чат-бот отвечает 24/7

✅ Готовы к записи? Напишите 'записаться'"""
    
    return response

def get_branches():
    """Список филиалов"""
    response = "📍 НАШИ ФИЛИАЛЫ:\n\n"
    
    for i, branch in enumerate(BRANCHES_LIST, 1):
        response += f"{i}. {branch['name']}\n"
    
    response += f"\n👉 Напишите номер (1-{len(BRANCHES_LIST)}) или название филиала"
    
    return response

# ===== ФУНКЦИИ ЗАПИСИ =====

def start_registration(user_id):
    """Начало записи"""
    set_user_state(user_id, 'waiting_child_name', {})
    
    response = """✏️ ЗАПИСЬ НА ЗАНЯТИЕ

Спасибо за интерес! 😊

Давайте оформим вашу запись.

1️⃣ Как зовут вашего ребенка? (Просто напишите имя)

Или напишите 'отмена' для отмены записи"""
    
    return response

def find_similar_word(word, word_list, threshold=0.6):
    """Поиск похожего слова"""
    best_match = None
    best_ratio = threshold
    
    for w in word_list:
        ratio = SequenceMatcher(None, word, w).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = w
    
    return best_match

def handle_registration(user_id, text, state, data):
    """Обработка процесса записи"""
    text_lower = text.lower().strip()
    
    if state == 'waiting_child_name':
        data['child_name'] = text
        set_user_state(user_id, 'waiting_child_age', data)
        
        return f"""✅ Спасибо, {text}!

2️⃣ Сколько лет вашему ребенку? (Напишите число, например: 5)"""
    
    elif state == 'waiting_child_age':
        try:
            age = int(text_lower)
            if 2 <= age <= 10:
                data['child_age'] = age
                set_user_state(user_id, 'waiting_program', data)
                
                programs_list = "3️⃣ Какую программу вы выбираете?\n\n"
                for i, (key, prog) in enumerate(PROGRAMS_INFO.items(), 1):
                    programs_list += f"{i}. {prog['name']} ({prog['duration']})\n"
                
                programs_list += f"\n👉 Напишите номер программы (1-{len(PROGRAMS_INFO)})"
                
                return programs_list
            else:
                return "❌ Возраст должен быть от 2 до 10 лет. Попробуйте еще раз:"
        except ValueError:
            return "❌ Пожалуйста, введите число. Например: 5"
    
    elif state == 'waiting_program':
        try:
            if text_lower.isdigit():
                num = int(text_lower)
                programs_list = list(PROGRAMS_INFO.values())
                
                if 1 <= num <= len(programs_list):
                    program = programs_list[num - 1]
                    data['program'] = program['name']
                    set_user_state(user_id, 'waiting_branch', data)
                    
                    branches_response = "4️⃣ Выберите филиал:\n\n"
                    for i, branch in enumerate(BRANCHES_LIST, 1):
                        branches_response += f"{i}. {branch['name']}\n"
                    
                    branches_response += f"\n👉 Напишите номер филиала (1-{len(BRANCHES_LIST)})"
                    
                    return branches_response
                else:
                    return f"❌ Номер должен быть от 1 до {len(PROGRAMS_INFO)}. Попробуйте еще раз:"
        except ValueError:
            pass
        
        return "❌ Пожалуйста, выберите программу по номеру"
    
    elif state == 'waiting_branch':
        if text_lower.isdigit():
            try:
                num = int(text_lower)
                if 1 <= num <= len(BRANCHES_LIST):
                    branch = BRANCHES_LIST[num - 1]
                    data['branch'] = branch['name']
                    set_user_state(user_id, 'waiting_phone', data)
                    
                    return f"""✅ Выбран филиал: {branch['name']}

5️⃣ И последнее - ваш номер телефона? 📱

Форма: +7 (XXX) XXX-XX-XX"""
                else:
                    return f"❌ Номер филиала должен быть от 1 до {len(BRANCHES_LIST)}"
            except ValueError:
                return "❌ Пожалуйста, введите номер филиала"
        
        # Поиск по названию
        text_lower = text.lower()
        for branch in BRANCHES_LIST:
            if text_lower in branch['name'].lower():
                data['branch'] = branch['name']
                set_user_state(user_id, 'waiting_phone', data)
                
                return f"""✅ Выбран филиал: {branch['name']}

5️⃣ И последнее - ваш номер телефона? 📱

Форма: +7 (XXX) XXX-XX-XX"""
        
        suggestion = find_similar_word(text_lower, [b['name'] for b in BRANCHES_LIST], 0.65)
        if suggestion:
            return f"🤔 Вы имели в виду: {suggestion}?\n\nНапишите его номер или полное название:"
        
        return f"🤔 Филиал '{text}' не найден 😕\n\nНапишите номер (1-{len(BRANCHES_LIST)}) или название филиала:"
    
    elif state == 'waiting_phone':
        data['phone'] = text
        
        # Сохраняем запись
        if save_registration(
            user_id,
            data.get('child_name'),
            data.get('child_age'),
            data.get('program'),
            data.get('branch'),
            data.get('phone')
        ):
            set_user_state(user_id, 'default', {})
            
            confirmation = f"""🎉🎉🎉 ЗАПИСЬ УСПЕШНО ПОДТВЕРЖДЕНА! 🎉🎉🎉

Спасибо, что выбрали RoboSTEAMuL! 💙

Вот краткая информация вашей записи:

👶 Ребенок: {data.get('child_name')} ✨
🎂 Возраст: {data.get('child_age')} лет 🎈
🎯 Программа: {data.get('program')} 🚀
📍 Филиал: {data.get('branch')} 🏫
📱 Телефон: {data.get('phone')} ☎️

⏰ Что дальше?
🔔 Мы позвоним вам в течение 24 часов!
✅ Первое занятие БЕСПЛАТНО! 🎁

📞 Если у вас есть вопросы:
• Наталья: +7 (922) 014-44-94
• Ксения: +7 (904) 805-25-61
• Жанна: +7 (951) 239-86-49

💪 Спасибо за доверие! До скорого! 🚀"""
            
            return confirmation
        else:
            set_user_state(user_id, 'default', {})
            return "⚠️ Ой! Ошибка при сохранении записи 😕\n\nПожалуйста, попробуйте позже или позвоните нам напрямую:\n+7 (922) 014-44-94"
    
    return "🤔 Что-то пошло не так... Напишите 'записаться' 📝 чтобы начать заново!"

def handle_message(text, user_id):
    """Обработка сообщения"""
    text_lower = text.lower().strip()
    
    logger.info(f"📨 Сообщение от {user_id}: '{text}'")
    
    # Проверяем состояние пользователя
    state, data = get_user_state(user_id)
    
    # Если пользователь в процессе записи
    if state != 'default':
        # Если захотел отменить
        if text_lower in ['отмена', 'cancel', 'нет']:
            set_user_state(user_id, 'default', {})
            return "❌ Запись отменена.\n\nНапишите 'привет' для меню"
        
        # Обработать запись
        return handle_registration(user_id, text, state, data)
    
    # Приветствие
    if text_lower in ['привет', 'hi', 'hello', 'привет!', 'хай', 'начать', 
                      'добрый день', 'доброе утро', 'добрый вечер', 'добрая ночь',
                      'здравствуйте', 'здравствуй', 'пока', 'привет привет', 'меню']:
        return get_greeting()
    
    # Программы
    elif text_lower in ['программы', 'programs', 'курсы', 'обучение', 'программа']:
        return get_programs()
    
    # Филиалы
    elif text_lower in ['филиалы', 'branches', 'где', 'адреса', 'центры', 'филиал']:
        return get_branches()
    
    # Цены
    elif text_lower in ['цены', 'price', 'стоимость', 'сколько', 'цена']:
        return get_prices()
    
    # Контакты
    elif text_lower in ['контакты', 'contacts', 'телефон', 'phone', 'звоните', 'контакт']:
        return get_contacts()
    
    # Запись на занятие
    elif text_lower in ['записаться', 'запись', 'register', 'запись на занятие', 'хочу записаться']:
        return start_registration(user_id)
    
    # Выбор филиала по номеру
    elif text_lower.isdigit():
        try:
            num = int(text_lower)
            if 1 <= num <= len(BRANCHES_LIST):
                branch = BRANCHES_LIST[num - 1]
                response = f"""✅ ВЫБРАН: {branch['name']}

📚 ДОСТУПНЫЕ ПРОГРАММЫ:
"""
                for prog in branch['programs']:
                    response += f"• {prog}\n"
                
                response += f"""\n📞 ДЛЯ ЗАПИСИ:
{get_contacts()}"""
                return response
            else:
                return f"❌ Номер неверный. Укажите от 1 до {len(BRANCHES_LIST)}"
        except ValueError:
            logger.error(f"Ошибка преобразования номера: {text_lower}")
    
    # Поиск по названию филиала
    elif any(kw in text_lower for kw in ['доу', 'гимназия', 'школа']):
        for branch in BRANCHES_LIST:
            if text_lower in branch['name'].lower():
                response = f"""✅ ВЫБРАН: {branch['name']}

📚 ДОСТУПНЫЕ ПРОГРАММЫ:
"""
                for prog in branch['programs']:
                    response += f"• {prog}\n"
                
                response += f"""\n📞 ДЛЯ ЗАПИСИ:
{get_contacts()}"""
                return response
        
        return f"❌ Филиал не найден\n\nНапишите 'филиалы' для полного списка"
    
    # По умолчанию - попытка найти похожую команду
    else:
        commands = ['программы', 'филиалы', 'цены', 'контакты', 'записаться']
        similar_command = find_similar_word(text_lower, commands, threshold=0.65)
        
        if similar_command:
            return f"""🤔 Вы имели в виду: '{similar_command}'?

📌 Доступные команды:
• программы 📚 - наши курсы
• филиалы 📍 - где заниматься  
• цены 💰 - стоимость занятий
• контакты 📞 - как записаться
• записаться ✏️ - начать запись на занятие
• привет ☀️ - главное меню"""
        
        return """🤔 Мм, я вас не совсем понял! 😊

Что вас интересует? Напишите:

📚 программы - наши курсы
📍 филиалы - где заниматься  
💰 цены - стоимость занятий
📞 контакты - как записаться
✏️ записаться - начать запись на занятие
🎉 привет - главное меню

Или просто напишите что-нибудь из этого! 👆"""

# ===== FLASK ROUTES =====

@app.route('/', methods=['GET'])
def home():
    """Главная страница"""
    logger.info("✅ Запрос к главной странице")
    return jsonify({
        'status': 'running',
        'bot': BOT_NAME,
        'version': BOT_VERSION,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья"""
    return jsonify({
        'status': 'healthy',
        'bot': BOT_NAME
    }), 200

@app.route('/callback', methods=['POST'])
def callback():
    """Обработчик вебхуков от VK - БОТ ОТВЕЧАЕТ ТОЛЬКО НА ВХОДЯЩИЕ СООБЩЕНИЯ"""
    try:
        data = request.json
        
        if not data:
            logger.warning("⚠️ Пустой запрос")
            return jsonify({'ok': True}), 200
        
        logger.info(f"📩 Вебхук получен: {data.get('type')}")
        
        if VK_SECRET_KEY and data.get('secret') != VK_SECRET_KEY:
            logger.warning("⚠️ Неверный секретный ключ")
            return jsonify({'ok': True}), 200
        
        event_type = data.get('type')
        
        if event_type == 'confirmation':
            logger.info("✅ Confirmation request")
            return VK_CONFIRMATION_CODE, 200
        
        # БОТ ОТВЕЧАЕТ ТОЛЬКО НА message_new
        if event_type == 'message_new':
            message = data.get('object', {}).get('message', {})
            user_id = message.get('from_id')
            text = message.get('text', '')
            
            # Игнорируем сообщения от сервисов и пустые
            if user_id < 0:
                logger.info("ℹ️ Сообщение от сервиса, игнорируем")
                return jsonify({'ok': True}), 200
            
            if not text or not text.strip():
                logger.info("ℹ️ Пустое сообщение, игнорируем")
                return jsonify({'ok': True}), 200
            
            logger.info(f"📨 Сообщение от {user_id}: {text}")
            response = handle_message(text, user_id)
            send_message(user_id, response)
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"❌ Ошибка в callback: {e}", exc_info=True)
        return jsonify({'ok': True}), 200

@app.route('/stats', methods=['GET'])
def stats():
    """Статистика"""
    return jsonify({
        'bot': BOT_NAME,
        'version': BOT_VERSION,
        'group_id': GROUP_ID,
        'branches': len(BRANCHES_LIST),
        'programs': len(PROGRAMS_INFO),
        'status': 'active'
    })

@app.errorhandler(404)
def not_found(error):
    logger.warning("⚠️ 404 Not Found")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"❌ 500 Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ===== MAIN =====

if __name__ == '__main__':
    init_registrations_db()
    
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Запуск {BOT_NAME} v{BOT_VERSION}")
    logger.info(f"🔗 http://0.0.0.0:{port}")
    logger.info(f"📍 Филиалов: {len(BRANCHES_LIST)}")
    logger.info(f"📚 Программ: {len(PROGRAMS_INFO)}")
    logger.info("⚠️ БОТ ОТВЕЧАЕТ ТОЛЬКО НА ВХОДЯЩИЕ СООБЩЕНИЯ (нет лишних отправок)")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
