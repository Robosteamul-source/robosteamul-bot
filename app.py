#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 RoboSTEAMuL VK Bot - Простая версия
Функции: Приветствие, Программы, Филиалы, Цены, Контакты, Запись
"""

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.utils import get_random_id
from datetime import datetime
import random
import sqlite3
import json

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
BOT_VERSION = "1.0 Simple"
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
}

# ===== ФУНКЦИИ =====

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

def get_greeting():
    """Приветствие в зависимости от времени суток"""
    current_hour = datetime.now().hour
    
    # Определяем время суток
    if 5 <= current_hour < 12:
        # Утро
        greetings = [
            """🌅 Доброе утро!

Рады видеть вас в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество и логику.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться""",
            
            """☀️ Доброе утро!

Добро пожаловать в RoboSTEAMuL! 🤖

Начните день с интересного выбора курса для вашего ребенка.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
        ]
    
    elif 12 <= current_hour < 17:
        # День
        greetings = [
            """🌤️ Добрый день!

Добро пожаловать в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество и логику.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться""",
            
            """☀️ Добрый день!

Рады встречать вас в RoboSTEAMuL! 🤖

Выбирайте программу развития для вашего ребенка.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
        ]
    
    elif 17 <= current_hour < 21:
        # Вечер
        greetings = [
            """🌆 Добрый вечер!

Добро пожаловать в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество и логику.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться""",
            
            """🌙 Добрый вечер!

Спасибо, что посетили RoboSTEAMuL! 🤖

Мы работаем завтра с 09:00. Планируйте развитие вашего ребенка уже сейчас!

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
        ]
    
    else:
        # Ночь
        greetings = [
            """🌙 Здравствуйте!

Спасибо за интерес к RoboSTEAMuL! 🤖

Мы работаем с 09:00 до 18:00 (пн-пт).
Давайте подготовимся к записи на курсы!

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться""",
            
            """🌃 Добро пожаловать в RoboSTEAMuL!

Ночью мы не работаем, но вы можете узнать информацию. 🤖

Мы открываемся завтра в 09:00!

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший центр
• цены - стоимость занятий
• контакты - как записаться"""
        ]
    
    return random.choice(greetings)

def get_programs():
    """Программы"""
    return """📚 НАШИ ПРОГРАММЫ:

🤖 РОБОТОТЕХНИКА:
• РобоSTEAM (3-4 года) - 300 руб./занятие, 30 мин
• РобоSTEAM Брик (5-6 лет) - 300 руб./занятие, 60 мин
• РобоSTEAM Про (6-8 лет) - 400 руб./занятие, 60 мин

💃 ХОРЕОГРАФИЯ:
• Возраст 3-8 лет
• 350 руб./занятие

✅ ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО!"""

def get_branches():
    """Филиалы"""
    menu = """📍 НАШИ ФИЛИАЛЫ (26 центров):

Напишите число (1-26) или название:
"""
    for i, branch in enumerate(BRANCHES_LIST[:8], 1):
        programs_count = len(branch['programs'])
        menu += f"{i}. {branch['name']} ({programs_count} программ)\n"
    
    menu += f"\n... и еще {len(BRANCHES_LIST) - 8} филиалов\n\nПримеры:\n• напишите '1' для ДОУ №30\n• напишите 'ДОУ №448СП'"
    
    return menu

def get_prices():
    """Цены"""
    return """💰 СТОИМОСТЬ:

🤖 РобоSTEAM (3-4 года) - 300 руб./занятие (30 мин)
🧱 РобоSTEAM Брик (5-6 лет) - 300 руб./занятие (60 мин)
⚙️ РобоSTEAM Про (6-8 лет) - 400 руб./занятие (60 мин)
💃 Хореография - 350 руб./занятие

🎁 СКИДКИ:
✅ Первое занятие БЕСПЛАТНО!
✅ На полугодие - скидка 5%
✅ На год - скидка 10%"""

def get_contacts():
    """Контакты"""
    contacts_str = "📞 КОНТАКТЫ:\n\n"
    
    contacts_str += "☎️ ПОЗВОНИТЕ НАМ:\n"
    for contact in CONTACTS.values():
        contacts_str += f"{contact['number']} ({contact['name']})\n"
    
    contacts_str += f"\n📧 Email: {SCHOOL_EMAIL}\n"
    contacts_str += f"🌐 Сайт: {SCHOOL_WEBSITE}\n\n"
    
    contacts_str += "🕐 РЕЖИМ РАБОТЫ:\n"
    contacts_str += f"{WORK_SCHEDULE['weekdays']}: {WORK_SCHEDULE['time']}\n"
    contacts_str += f"{WORK_SCHEDULE['weekends']}: {WORK_SCHEDULE['weekends']}\n\n"
    
    contacts_str += "📍 26 ФИЛИАЛОВ ПО ГОРОДУ\n"
    contacts_str += "🎁 ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО!"
    
    return contacts_str

# ===== ФУНКЦИИ ЗАПИСИ =====

def get_user_state(user_id):
    """Получить состояние пользователя"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        c.execute('SELECT state, registration_data FROM user_state WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            state, data = result
            return state, json.loads(data) if data else {}
        return 'default', {}
    except Exception as e:
        logger.error(f"❌ Ошибка получения состояния: {e}")
        return 'default', {}

def set_user_state(user_id, state, data=None):
    """Установить состояние пользователя"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        data_json = json.dumps(data) if data else None
        c.execute('''
            INSERT OR REPLACE INTO user_state (user_id, state, registration_data)
            VALUES (?, ?, ?)
        ''', (user_id, state, data_json))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"❌ Ошибка установки состояния: {e}")

def save_registration(user_id, child_name, child_age, program, branch, phone):
    """Сохранить запись на занятие"""
    try:
        conn = sqlite3.connect(REGISTRATIONS_DB)
        c = conn.cursor()
        c.execute('''
            INSERT INTO registrations (user_id, child_name, child_age, program, branch, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, child_name, child_age, program, branch, phone))
        conn.commit()
        conn.close()
        logger.info(f"✅ Запись сохранена: {child_name}, {program}, {branch}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения записи: {e}")
        return False

def start_registration(user_id):
    """Начать процесс записи"""
    set_user_state(user_id, 'waiting_name', {})
    return """📝 ЗАПИСЬ НА ЗАНЯТИЕ

Отлично! Давайте запишем вашего ребенка на занятие! 🎉

Сначала напишите: Как зовут вашего ребенка?

Пример: Маша"""

def handle_registration(user_id, text, state, data):
    """Обработка процесса записи"""
    text_lower = text.lower().strip()
    
    if state == 'waiting_name':
        data['child_name'] = text
        set_user_state(user_id, 'waiting_age', data)
        return """Спасибо! 😊

Сколько лет вашему ребенку?

Пример: 5"""
    
    elif state == 'waiting_age':
        try:
            age = int(text_lower)
            if 3 <= age <= 8:
                data['child_age'] = age
                set_user_state(user_id, 'waiting_program', data)
                
                programs_list = """Какая программа вас интересует?

Напишите номер:
1️⃣ РобоSTEAM (3-4 года) - 300 руб.
2️⃣ РобоSTEAM Брик (5-6 лет) - 300 руб.
3️⃣ РобоSTEAM Про (6-8 лет) - 400 руб.
4️⃣ Хореография (3-8 лет) - 350 руб."""
                
                return programs_list
            else:
                return "❌ Возраст должен быть от 3 до 8 лет.\n\nПопробуйте еще раз:"
        except:
            return "❌ Пожалуйста, напишите число (например: 5)"
    
    elif state == 'waiting_program':
        programs_map = {
            '1': 'РобоSTEAM (3-4 года)',
            '2': 'РобоSTEAM Брик (5-6 лет)',
            '3': 'РобоSTEAM Про (6-8 лет)',
            '4': 'Хореография'
        }
        
        if text_lower in programs_map:
            data['program'] = programs_map[text_lower]
            set_user_state(user_id, 'waiting_branch', data)
            
            branches_list = """Выберите филиал. Напишите номер (1-26) или название:

1️⃣ ДОУ №30
2️⃣ ДОУ №30СП
3️⃣ ДОУ №10 Копейск
4️⃣ ДОУ №18СП
5️⃣ ДОУ №24 Копейск

Напишите номер или название филиала:"""
            
            return branches_list
        else:
            return "❌ Пожалуйста, выберите номер от 1 до 4"
    
    elif state == 'waiting_branch':
        # Поиск филиала по номеру
        if text_lower.isdigit():
            try:
                num = int(text_lower)
                if 1 <= num <= len(BRANCHES_LIST):
                    branch = BRANCHES_LIST[num - 1]
                    data['branch'] = branch['name']
                    set_user_state(user_id, 'waiting_phone', data)
                    return f"""Отлично! Вы выбрали: {branch['name']}

Теперь напишите номер телефона родителя:

Пример: +7 (900) 123-45-67"""
                else:
                    return f"❌ Номер должен быть от 1 до {len(BRANCHES_LIST)}"
            except:
                pass
        
        # Поиск по названию
        for branch in BRANCHES_LIST:
            if text_lower in branch['name'].lower():
                data['branch'] = branch['name']
                set_user_state(user_id, 'waiting_phone', data)
                return f"""Отлично! Вы выбрали: {branch['name']}

Теперь напишите номер телефона родителя:

Пример: +7 (900) 123-45-67"""
        
        return "❌ Филиал не найден. Напишите номер (1-26) или название"
    
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
            
            confirmation = f"""✅ ЗАПИСЬ ПОДТВЕРЖДЕНА!

Спасибо! Вот ваша запись:

📝 Ребенок: {data.get('child_name')}
🎂 Возраст: {data.get('child_age')} лет
🎯 Программа: {data.get('program')}
📍 Филиал: {data.get('branch')}
📱 Телефон: {data.get('phone')}

🎉 Скоро мы с вами свяжемся!

Спасибо за выбор RoboSTEAMuL! 💪"""
            
            return confirmation
        else:
            set_user_state(user_id, 'default', {})
            return "❌ Ошибка при сохранении записи. Пожалуйста, попробуйте позже."
    
    return "Что-то пошло не так. Напишите 'записаться' чтобы начать заново."

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
                      'здравствуйте', 'здравствуй', 'привет!', 'пока', 'привет привет']:
        return get_greeting()
    
    # Программы
    elif text_lower in ['программы', 'programs', 'курсы', 'обучение']:
        return get_programs()
    
    # Филиалы
    elif text_lower in ['филиалы', 'branches', 'где', 'адреса', 'центры']:
        return get_branches()
    
    # Цены
    elif text_lower in ['цены', 'price', 'стоимость', 'сколько']:
        return get_prices()
    
    # Контакты
    elif text_lower in ['контакты', 'contacts', 'запись', 'телефон', 'phone']:
        return get_contacts()
    
    # Запись на занятие
    elif text_lower in ['записаться', 'запись', 'register', 'запись на занятие', 'хочу записаться']:
        return start_registration(user_id)
    """Обработка сообщения"""
    text_lower = text.lower().strip()
    
    logger.info(f"📨 Сообщение от {user_id}: '{text}'")
    
    # Приветствие
    if text_lower in ['привет', 'hi', 'hello', 'привет!', 'хай', 'начать', 
                      'добрый день', 'доброе утро', 'добрый вечер', 'добрая ночь',
                      'здравствуйте', 'здравствуй', 'привет!', 'пока', 'привет привет']:
        return get_greeting()
    
    # Программы
    elif text_lower in ['программы', 'programs', 'курсы', 'обучение']:
        return get_programs()
    
    # Филиалы
    elif text_lower in ['филиалы', 'branches', 'где', 'адреса', 'центры']:
        return get_branches()
    
    # Цены
    elif text_lower in ['цены', 'price', 'стоимость', 'сколько']:
        return get_prices()
    
    # Контакты
    elif text_lower in ['контакты', 'contacts', 'запись', 'телефон', 'phone']:
        return get_contacts()
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
        except:
            pass
    
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
    
    # По умолчанию
    else:
        return """😊 Я вас не совсем понял!

Напишите:
• программы - наши курсы
• филиалы - где заниматься
• цены - стоимость
• контакты - как записаться
• записаться - начать запись на занятие"""

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
    """Обработчик вебхуков от VK"""
    try:
        data = request.json
        
        if not data:
            logger.warning("⚠️ Пустой запрос")
            return jsonify({'error': 'Empty request'}), 400
        
        logger.info(f"📩 Вебхук получен: {data.get('type')}")
        
        if VK_SECRET_KEY and data.get('secret') != VK_SECRET_KEY:
            logger.warning("⚠️ Неверный секретный ключ")
            return jsonify({'error': 'Invalid secret'}), 403
        
        event_type = data.get('type')
        
        if event_type == 'confirmation':
            logger.info("✅ Confirmation request")
            return VK_CONFIRMATION_CODE, 200
        
        if event_type == 'message_new':
            message = data.get('object', {}).get('message', {})
            user_id = message.get('from_id')
            text = message.get('text', '')
            
            if user_id < 0:
                logger.info("ℹ️ Сообщение от сервиса, игнорируем")
                return jsonify({'ok': True}), 200
            
            if text.strip():
                logger.info(f"📨 Сообщение от {user_id}: {text}")
                response = handle_message(text, user_id)
                send_message(user_id, response)
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"❌ Ошибка в callback: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
