#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 RoboSTEAMuL VK Bot - Premium Version 2.1 with AI Methodist
Автор: RoboSTEAMuL
Версия: 2.1 Premium + AI Методист
Описание: Бот с ИИ методистом для сотрудников + расширенный словарь для клиентов
"""

import os
import json
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.utils import get_random_id
from datetime import datetime
import anthropic
import sqlite3
import threading
import random

# ===== ИНИЦИАЛИЗАЦИЯ ЛОГГЕРА =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== ЗАГРУЗКА ПЕРЕМЕННЫХ =====
load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
API_VERSION = os.getenv('API_VERSION', '5.131')
VK_SECRET_KEY = os.getenv('VK_SECRET_KEY', '')
VK_CONFIRMATION_CODE = os.getenv('VK_CONFIRMATION_CODE', '')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')

# ===== ПРОВЕРКА ПЕРЕМЕННЫХ =====
if not VK_TOKEN or not GROUP_ID:
    logger.error("❌ VK_TOKEN или GROUP_ID не установлены!")
    raise ValueError("VK_TOKEN и GROUP_ID обязательны")

logger.info("✅ VK_TOKEN загружен")
logger.info(f"✅ GROUP_ID: {GROUP_ID}")
if ANTHROPIC_API_KEY:
    logger.info("✅ ANTHROPIC_API_KEY загружена")

# ===== ИНИЦИАЛИЗАЦИЯ FLASK =====
app = Flask(__name__)

# ===== ИНИЦИАЛИЗАЦИЯ VK API =====
vk = None
try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    logger.info("✅ VK API успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации VK API: {e}")

# ===== ИНИЦИАЛИЗАЦИЯ ANTHROPIC API =====
ai_client = None
if ANTHROPIC_API_KEY:
    try:
        ai_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        logger.info("✅ Anthropic API успешно инициализирован")
    except Exception as e:
        logger.error(f"⚠️ Ошибка инициализации Anthropic API: {e}")
        ai_client = None

# ===== БОТ ИНФОРМАЦИЯ =====
BOT_NAME = "RoboSTEAMuL Консультант"
BOT_VERSION = "2.1 Premium + AI Методист"
SCHOOL_WEBSITE = "robosteamul.com"
SCHOOL_EMAIL = "info@robosteamul.com"

# ===== КОНТАКТЫ СОТРУДНИКОВ =====
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

# ===== РЕЖИМЫ БОТА =====
BOT_MODES = {
    'CLIENT': 'client',
    'METHODIST': 'methodist'
}

# ===== БАЗА ДАННЫХ СОТРУДНИКОВ =====
EMPLOYEES_DB = 'employees.db'

def init_employees_db():
    """Инициализировать базу данных сотрудников"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                branch TEXT NOT NULL,
                access_level TEXT DEFAULT 'employee',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS methodist_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_context (
                user_id INTEGER PRIMARY KEY,
                mode TEXT DEFAULT 'client',
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")

# ===== ИНФОРМАЦИЯ О ФИЛИАЛАХ И ПРОГРАММАХ =====
BRANCHES_LIST = [
    {'name': 'ДОУ №30', 'programs': ['Робототехника', 'Хореография', 'Подготовка к школе', 'Логопед']},
    {'name': 'ДОУ №30СП', 'programs': ['Робототехника', 'Хореография', 'Подготовка к школе', 'Логопед']},
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
    {'name': 'ДОУ №369', 'programs': ['Робототехника', 'Подготовка к школе']},
    {'name': 'ДОУ №413', 'programs': ['Робототехника']},
    {'name': 'ДОУ №416', 'programs': ['Робототехника']},
    {'name': 'ДОУ №418', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №421', 'programs': ['Робототехника']},
    {'name': 'ДОУ №428', 'programs': ['Робототехника']},
    {'name': 'ДОУ №444', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'ДОУ №448', 'programs': ['Робототехника']},
    {'name': 'ДОУ №448СП', 'programs': ['Робототехника', 'Хореография', 'Подготовка к школе']},
    {'name': 'ДОУ №450', 'programs': ['Робототехника']},
    {'name': 'ДОУ №475', 'programs': ['Робототехника', 'Хореография']},
    {'name': 'Гимназия №76', 'programs': ['Робототехника']}
]

PROGRAMS_INFO = {
    'robossteam': {
        'name': '🤖 РобоSTEAM (3-4 года)',
        'age': '3-4 года',
        'price': '300 руб./занятие',
        'duration': '30 минут',
        'group_size': '6-8 человек',
    },
    'brik': {
        'name': '🧱 РобоSTEAM Брик (5-6 лет)',
        'age': '5-6 лет',
        'price': '300 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
    },
    'pro': {
        'name': '⚙️ РобоSTEAM Про (6-8 лет)',
        'age': '6-8 лет',
        'price': '400 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
    },
    'choreography': {
        'name': '💃 Хореография (3-8 лет)',
        'age': '3-8 лет',
        'price': '350 руб./занятие',
        'duration': '30-60 минут',
        'group_size': '8-12 человек',
    },
    'speech': {
        'name': '🗣️ Логопедия (3-7 лет)',
        'age': '3-7 лет',
        'price': '600 руб./занятие',
        'duration': '60 минут',
        'group_size': 'Индивидуально',
    },
}

# ===== МЕТОДИЧЕСКИЕ МАТЕРИАЛЫ ДЛЯ ИИ =====
METHODIST_KNOWLEDGE_BASE = """
# 📚 МЕТОДИЧЕСКАЯ БАЗА ЗНАНИЙ RoboSTEAMuL

## Структура компании
- Компания: RoboSTEAMuL (Центр детского развития)
- Сайт: robosteamul.com
- Email: info@robosteamul.com
- Филиалов: 26
- Возраст детей: 3-8 лет

## Контакты для записи
- Наталья: +7 (922) 014-44-94
- Ксения: +7 (904) 805-25-61
- Жанна: +7 (951) 239-86-49
- Email: info@robosteamul.com

## Режим работы
- Пн-Пт: 09:00-18:00
- Сб-Вс: Выходные

## Программы обучения

### 1. Робототехника
- РобоSTEAM (3-4 года): 30 мин, 300 руб./занятие
- РобоSTEAM Брик (5-6 лет): 60 мин, 300 руб./занятие
- РобоSTEAM Про (6-8 лет): 60 мин, 400 руб./занятие

### 2. Хореография
- Возраст: 3-8 лет
- Продолжительность: 30-60 мин
- Цена: 350 руб./занятие

### 3. Развитие речи и логопедия
- Возраст: 3-7 лет
- Диагностика: 800 руб.
- Занятия: 600 руб./занятие
- Продолжительность: 60 мин

## Преимущества компании
- Опытные преподаватели (10+ лет опыта)
- Маленькие группы (6-8 человек)
- Современное оборудование
- 26 филиалов по городу
- Первое занятие БЕСПЛАТНО

## Спецпредложения
- Запись на полугодие: скидка 5%
- Запись на учебный год: скидка 10%
"""

# ===== ФУНКЦИИ УПРАВЛЕНИЯ БАЗОЙ ДАННЫХ =====

def add_employee(user_id, name, role, branch):
    """Добавить сотрудника в базу (без дублирования)"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        
        # Проверить, существует ли уже
        c.execute('SELECT user_id FROM employees WHERE user_id = ?', (user_id,))
        if c.fetchone():
            logger.info(f"⚠️ Сотрудник {user_id} уже существует, обновляю...")
        
        c.execute('''
            INSERT OR REPLACE INTO employees (user_id, name, role, branch)
            VALUES (?, ?, ?, ?)
        ''', (user_id, name, role, branch))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка добавления сотрудника: {e}")
        return False

def get_employee(user_id):
    """Получить информацию о сотруднике"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        c.execute('SELECT * FROM employees WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result
    except Exception as e:
        logger.error(f"❌ Ошибка получения данных: {e}")
        return None

def get_user_mode(user_id):
    """Получить режим пользователя (безопасно от дублирования)"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        c.execute('SELECT mode FROM user_context WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        
        if result:
            mode = result[0]
            conn.close()
            return mode
        
        # Если нет записи, создать новую
        if get_employee(user_id):
            mode = BOT_MODES['METHODIST']
        else:
            mode = BOT_MODES['CLIENT']
        
        c.execute('''
            INSERT OR REPLACE INTO user_context (user_id, mode)
            VALUES (?, ?)
        ''', (user_id, mode))
        conn.commit()
        conn.close()
        return mode
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return BOT_MODES['CLIENT']

def save_chat_history(user_id, role, content):
    """Сохранить сообщение в историю (защита от дублирования)"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        
        # Проверить, не является ли это дублем (одинаковое сообщение в последние 5 сек)
        c.execute('''
            SELECT COUNT(*) FROM methodist_chats 
            WHERE user_id = ? AND role = ? AND content = ?
            AND datetime(created_at) > datetime('now', '-5 seconds')
        ''', (user_id, role, content))
        
        if c.fetchone()[0] > 0:
            logger.warning(f"⚠️ Дубль сообщения от {user_id} предотвращен")
            conn.close()
            return True
        
        c.execute('''
            INSERT INTO methodist_chats (user_id, role, content)
            VALUES (?, ?, ?)
        ''', (user_id, role, content))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения: {e}")
        return False

def get_chat_history(user_id, limit=10):
    """Получить историю чата"""
    try:
        conn = sqlite3.connect(EMPLOYEES_DB)
        c = conn.cursor()
        c.execute('''
            SELECT role, content FROM methodist_chats 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (user_id, limit))
        results = c.fetchall()
        conn.close()
        return list(reversed(results))
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return []

# ===== ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ =====

def send_message(user_id, message):
    """Отправить сообщение пользователю (один раз)"""
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

# ===== ФУНКЦИИ ИИ МЕТОДИСТА =====

def get_ai_methodist_response(user_id, user_message):
    """Получить ответ от ИИ методиста"""
    if not ai_client:
        return "❌ ИИ методист временно недоступен. Пожалуйста, обратитесь к руководству."
    
    try:
        chat_history = get_chat_history(user_id, limit=10)
        employee = get_employee(user_id)
        employee_info = ""
        
        if employee:
            employee_info = f"\n\nСотрудник: {employee[1]} (Должность: {employee[2]}, Филиал: {employee[3]})"
        
        system_prompt = f"""Вы - опытный методист и куратор по развитию педагогов в компании RoboSTEAMuL.

{METHODIST_KNOWLEDGE_BASE}

{employee_info}

Ваша задача:
1. Помогать педагогам улучшать методику преподавания
2. Давать советы по работе с детьми разных возрастов
3. Объяснять программы и подходы компании
4. Помогать в организации занятий
5. Отвечать на вопросы о материалах и оборудовании
6. Поддерживать профессиональное развитие

Будьте дружелюбны, поддерживайте, давайте практические советы.
Все ответы на русском языке."""

        messages = []
        
        for role, content in chat_history:
            if role == 'user':
                messages.append({"role": "user", "content": content})
            else:
                messages.append({"role": "assistant", "content": content})
        
        messages.append({"role": "user", "content": user_message})
        
        response = ai_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            system=system_prompt,
            messages=messages
        )
        
        ai_response = response.content[0].text
        
        save_chat_history(user_id, 'user', user_message)
        save_chat_history(user_id, 'assistant', ai_response)
        
        logger.info(f"✅ Ответ ИИ методиста для {user_id}")
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return f"❌ Ошибка: {str(e)}"

# ===== РАСШИРЕННЫЙ СЛОВАРНЫЙ ЗАПАС ДЛЯ КЛИЕНТОВ =====

GREETING_VARIANTS = [
    """☀️ Доброе утро! 

🤖 Добро пожаловать в RoboSTEAMuL - центр развития вашего ребенка!

Я помогу вам узнать о наших программах, выбрать филиал и записаться на занятия.

Что вас интересует?
• программы - наши курсы
• филиалы - выберите ближайший детский сад
• цены - стоимость и скидки
• контакты - как записаться""",

    """🌤️ Добрый день! 

Рады видеть вас в RoboSTEAMuL! 👋

Мы помогаем детям 3-8 лет развивать творчество, логику и инженерное мышление.

Чем я могу помочь?
• программы - узнайте о курсах
• филиалы - найдите удобный филиал
• цены - информация о стоимости
• контакты - свяжитесь с нами""",

    """🌙 Добрый вечер! 

Спасибо, что посетили RoboSTEAMuL! 

Мы работаем с 09:00 до 18:00 пн-пт и будем рады вас видеть завтра!

Вам помочь?
• программы - описание курсов
• филиалы - адреса центров
• цены - стоимость занятий
• контакты - как с нами связаться"""
]

def get_greeting():
    """Приветствие с вариациями"""
    return random.choice(GREETING_VARIANTS)

def get_programs_menu():
    """Меню программ с большим словарным запасом"""
    variants = [
        """📚 НАШИ ПРОГРАММЫ:

🤖 РОБОТОТЕХНИКА (развиваем инженеров!)
• РобоSTEAM (3-4 года) - первые шаги в конструировании
• РобоSTEAM Брик (5-6 лет) - механика и творчество
• РобоSTEAM Про (6-8 лет) - роботика и программирование

💃 ХОРЕОГРАФИЯ (гибкость и артистизм)
• Возраст 3-8 лет
• Развитие координации, ритма и уверенности

🗣️ ЛОГОПЕДИЯ (красивая речь)
• Коррекция звукопроизношения
• Подготовка к школе
• Индивидуальный подход

🧠 ПОДГОТОВКА К ШКОЛЕ (готовим к учебе)
• Дошколёнок 4-5 и 6-7 лет
• Письмо, чтение, математика

✅ ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО для всех!""",

        """🎓 ВСЕ НАШИ КУРСЫ:

Мы предлагаем комплексное развитие детей 3-8 лет:

🤖 Робототехника - 3 уровня обучения
• Конструирование, инженерное мышление
• 300-400 руб./занятие

💃 Хореография - развитие творчества
• Танец, координация, выразительность
• 350 руб./занятие

🗣️ Логопедия - четкая речь
• Работа с дефектами, развитие речи
• 600 руб./занятие

🧠 Подготовка к школе - комплексная подготовка
• Все необходимое для успеха в школе
• 350-375 руб./занятие

💝 СПЕЦИАЛЬНОЕ ПРЕДЛОЖЕНИЕ:
✅ Первое занятие АБСОЛЮТНО БЕСПЛАТНО!
✅ Скидка 5% при записи на полугодие
✅ Скидка 10% при записи на год"""
    ]
    return random.choice(variants)

def get_branches_menu():
    """Меню филиалов"""
    menu = """📍 ВЫБЕРИТЕ УДОБНЫЙ ФИЛИАЛ:

У нас есть центры в 26 филиалах по городу!

Напишите число (1-26) или название детского сада:
"""
    for i, branch in enumerate(BRANCHES_LIST[:8], 1):
        programs_count = len(branch['programs'])
        menu += f"{i}️⃣  {branch['name']} ({programs_count} программ)\n"
    
    menu += f"\n... и еще {len(BRANCHES_LIST) - 8} филиалов\n\nПримеры:\n• напишите \"1\" для ДОУ №30\n• напишите \"ДОУ №448СП\""
    
    return menu

def get_prices_menu():
    """Прайс-лист с большим словарным запасом"""
    variants = [
        """💰 СТОИМОСТЬ ЗАНЯТИЙ:

🤖 РобоSTEAM (3-4 года, 30 мин) - 300 руб.
   Первое знакомство с конструированием

🧱 РобоSTEAM Брик (5-6 лет, 60 мин) - 300 руб.
   Сборка механизмов и творчество

⚙️ РобоSTEAM Про (6-8 лет, 60 мин) - 400 руб.
   Программирование и роботика

💃 Хореография (30-60 мин) - 350 руб.
   Танец для всех возрастов

🗣️ Логопедия (60 мин) - 600 руб./занятие
   Диагностика - 800 руб. (один раз)

🧠 Подготовка к школе:
   • 4-5 лет (60 мин) - 350 руб.
   • 6-7 лет (60 мин) - 375 руб.

🎁 ВЫГОДНЫЕ ПРЕДЛОЖЕНИЯ:
✅ Первое занятие совершенно бесплатно!
✅ На полугодие - скидка 5%
✅ На весь учебный год - скидка 10%

📝 Запишитесь прямо сейчас, позвоните нам!""",

        """💵 ЦЕНЫ И СКИДКИ:

Мы предлагаем доступное качественное образование:

Индивидуальные занятия:
- Робототехника: 300-400 руб.
- Хореография: 350 руб.
- Логопедия: 600 руб.
- Подготовка к школе: 350-375 руб.

Семейные скидки:
✅ Первое занятие бесплатно (пробный урок)
✅ Скидка 5% при покупке абонемента на полугодие
✅ Скидка 10% при покупке абонемента на учебный год

Почему это выгодно?
💚 Опытные преподаватели
💚 Маленькие группы (6-8 человек)
💚 Современное оборудование
💚 Первый результат уже через 2-3 занятия!

Хотите записаться? Позвоните прямо сейчас!"""
    ]
    return random.choice(variants)

def get_contacts_menu():
    """Контакты с полной информацией"""
    contacts_str = "📞 КОНТАКТЫ И ЗАПИСЬ:\n\n"
    
    contacts_str += "🏢 RoboSTEAMuL - Центр детского развития\n\n"
    
    contacts_str += "☎️ ПОЗВОНИТЕ НАМ:\n"
    for contact in CONTACTS.values():
        contacts_str += f"   📱 {contact['number']} ({contact['name']})\n"
    
    contacts_str += f"\n📧 Email: {SCHOOL_EMAIL}\n"
    contacts_str += f"🌐 Сайт: {SCHOOL_WEBSITE}\n\n"
    
    contacts_str += "🕐 РЕЖИМ РАБОТЫ:\n"
    contacts_str += f"   {WORK_SCHEDULE['weekdays']}: {WORK_SCHEDULE['time']}\n"
    contacts_str += f"   {WORK_SCHEDULE['weekends']}: {WORK_SCHEDULE['weekends']}\n\n"
    
    contacts_str += "📍 ВСЕ 26 ФИЛИАЛОВ ПО ГОРОДУ\n"
    contacts_str += "🎁 ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО!\n\n"
    
    contacts_str += "💡 Позвоните нашим специалистам - они подберут\n"
    contacts_str += "   оптимальную программу для вашего ребенка!"
    
    return contacts_str

def get_benefits_menu():
    """Преимущества с вариациями"""
    variants = [
        """⭐ ПОЧЕМУ РОДИТЕЛИ ВЫБИРАЮТ ROBOSSTEAMUL:

✅ КАЧЕСТВО ОБРАЗОВАНИЯ:
   • 10+ лет опыта в детском развитии
   • Проверенные методики обучения
   • Результаты видны уже через 2-3 занятия

✅ УДОБСТВО:
   • 26 филиалов по городу
   • Гибкое расписание (пн-пт 09:00-18:00)
   • Маленькие группы (6-8 человек)

✅ ДЛЯ РЕБЕНКА:
   • Развитие творчества и логики
   • Улучшение концентрации внимания
   • Подготовка к школе
   • Новые друзья и командный дух

✅ ДЛЯ РОДИТЕЛЕЙ:
   • Профессиональные педагоги
   • Современное оборудование
   • Безопасная среда обучения
   • Регулярная обратная связь

🏆 РЕЗУЛЬТАТЫ:
   • Призеры региональных соревнований
   • Отличные оценки в школе
   • Развитые способности
   • Уверенные в себе дети

⭐ ОТЗЫВЫ: 4.9/5.0 из 5
   Родители видят результаты и благодарны!

🎁 СПЕЦИАЛЬНО ДЛЯ ВАС:
   ✨ Первое занятие совершенно бесплатно
   ✨ Без обязательств и контрактов""",

        """🌟 ПОЧЕМУ ДЕТИ ОБОЖАЮТ ROBOSSTEAMUL:

Наша компания помогает раскрыть потенциал вашего ребенка:

🧠 ИНТЕЛЛЕКТУАЛЬНОЕ РАЗВИТИЕ:
   ✅ Логическое мышление
   ✅ Пространственное воображение
   ✅ Умение решать задачи
   ✅ Концентрация внимания

🎨 ТВОРЧЕСКИЕ СПОСОБНОСТИ:
   ✅ Инженерное воображение
   ✅ Художественное видение
   ✅ Креативный подход
   ✅ Самовыражение

💪 ЛИЧНОСТНОЕ РАЗВИТИЕ:
   ✅ Уверенность в себе
   ✅ Командная работа
   ✅ Лидерские качества
   ✅ Дружба со сверстниками

📊 ПРОВЕРЕННЫЕ РЕЗУЛЬТАТЫ:
   ✅ Улучшение успехов в школе
   ✅ Развитие речи и общения
   ✅ Гибкость и координация
   ✅ Готовность к школе

👨‍🏫 ПРОФЕССИОНАЛЬНАЯ КОМАНДА:
   ✅ Опытные преподаватели
   ✅ Постоянное обучение персонала
   ✅ Индивидуальный подход
   ✅ Забота о каждом ребенке"""
    ]
    return random.choice(variants)

def get_help_menu():
    """Справка по командам"""
    return """❓ ВСЕ КОМАНДЫ:

📍 ВЫБОР ФИЛИАЛА:
   • филиалы - список всех 26 центров
   • [номер] - выбрать по номеру ("1")
   • [название] - выбрать по названию ("ДОУ №30")

📚 ПРОГРАММЫ:
   • программы - описание всех курсов
   • роботехника / хореография / логопед - подробно

💰 ЦЕНЫ:
   • цены - стоимость занятий и скидки

📞 КОНТАКТЫ:
   • контакты - телефоны и режим работы
   • запись - как записаться

⭐ ИНФОРМАЦИЯ:
   • преимущества - почему выбрать нас
   • скидки - спецпредложения
   • первое занятие - как попробовать бесплатно

ℹ️ ПОМОЩЬ:
   • помощь - эта справка
   • привет - приветствие"""

def get_default_response():
    """Ответ на неизвестную команду"""
    variants = [
        """😊 Я вас не совсем понял, но я вам помогу! 

Вот что я могу сделать:
📍 филиалы - выбрать центр
📚 программы - узнать о курсах
💰 цены - стоимость занятий
📞 контакты - как записаться
❓ помощь - все команды""",

        """👋 Кажется, я не очень понял вас. Давайте попробуем еще раз!

Напишите:
• программы - наши курсы
• филиалы - где заниматься
• цены - стоимость
• контакты - как записаться
• помощь - все возможности""",

        """🤔 Прошу прощение, я не совсем разобрался в вопросе.

Я помогу вам узнать:
📚 программы - какие курсы есть
📍 филиалы - ближайший центр
💵 цены - сколько стоит
☎️ контакты - номера телефонов

Напишите одно из слов выше!"""
    ]
    return random.choice(variants)

# ===== ОСНОВНАЯ ОБРАБОТКА СООБЩЕНИЙ =====

def handle_message(text, user_id):
    """Основная обработка сообщения"""
    text_lower = text.lower().strip()
    
    logger.info(f"📨 Сообщение от {user_id}: '{text}'")
    
    user_mode = get_user_mode(user_id)
    
    # ===== РЕЖИМ МЕТОДИСТА =====
    if user_mode == BOT_MODES['METHODIST']:
        if text_lower in ['выход', 'exit', 'клиент', 'назад']:
            conn = sqlite3.connect(EMPLOYEES_DB)
            c = conn.cursor()
            c.execute('''
                INSERT OR REPLACE INTO user_context (user_id, mode)
                VALUES (?, ?)
            ''', (user_id, BOT_MODES['CLIENT']))
            conn.commit()
            conn.close()
            return get_greeting()
        
        elif text_lower in ['меню', 'помощь', 'help']:
            return """👋 Добро пожаловать, коллега!

🤖 Я ваш ИИ методист. Вам помочь с:
• Методикой преподавания
• Вопросами по программам
• Советами по работе с детьми
• Информацией о материалах
• Профессиональным развитием

Напишите свой вопрос! 💡"""
        
        else:
            return get_ai_methodist_response(user_id, text)
    
    # ===== РЕЖИМ КЛИЕНТА =====
    else:
        if text_lower in ['методист', 'педагог', 'сотрудник', 'staff']:
            employee = get_employee(user_id)
            if employee:
                conn = sqlite3.connect(EMPLOYEES_DB)
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO user_context (user_id, mode)
                    VALUES (?, ?)
                ''', (user_id, BOT_MODES['METHODIST']))
                conn.commit()
                conn.close()
                return """👋 Добро пожаловать в режим методиста!

🤖 Я готов помочь вам с любыми вопросами по методике преподавания.
Напишите свой вопрос!"""
            else:
                return "❓ Вы не зарегистрированы как сотрудник.\n\nЕсли вы сотрудник, свяжитесь с руководством."
        
        if text_lower in ['привет', 'hi', 'hello', 'привет!', 'хай', 'привет']:
            return get_greeting()
        
        elif text_lower in ['программы', 'programs', 'курсы', 'обучение']:
            return get_programs_menu()
        
        elif text_lower in ['филиалы', 'branches', 'где', 'адреса', 'центры']:
            return get_branches_menu()
        
        elif text_lower in ['цены', 'price', 'стоимость', 'сколько']:
            return get_prices_menu()
        
        elif text_lower in ['контакты', 'contacts', 'запись', 'телефон', 'phone']:
            return get_contacts_menu()
        
        elif text_lower in ['преимущества', 'advantages', 'почему', 'зачем']:
            return get_benefits_menu()
        
        elif text_lower in ['помощь', 'help', 'команды', 'что ты умеешь']:
            return get_help_menu()
        
        elif text_lower in ['скидки', 'скидка', 'акция', 'предложение']:
            return """🎁 СПЕЦПРЕДЛОЖЕНИЯ:

✅ ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО!
   Приходите без обязательств и пробуйте

✅ АБОНЕМЕНТ НА ПОЛУГОДИЕ
   Скидка 5% на всё обучение

✅ АБОНЕМЕНТ НА ГОД
   Скидка 10% - самое выгодное предложение!

💡 Чем раньше запишетесь, тем больше сэкономите!

☎️ Позвоните прямо сейчас:"""+ get_contacts_menu()
        
        elif text_lower in ['первое занятие', 'бесплатное', 'пробное']:
            return """🎉 ПЕРВОЕ ЗАНЯТИЕ БЕСПЛАТНО!

Это отличный способ познакомиться с нами:

✅ Полноценное занятие (30-60 мин)
✅ Опытный преподаватель
✅ Современное оборудование
✅ Никаких обязательств

🎯 ПРЯМО СЕЙЧАС:
1. Выберите программу (программы)
2. Выберите филиал (филиалы)
3. Позвоните нам (контакты)

☎️ Наши специалисты помогут подобрать оптимальное время!"""
        
        elif text_lower.isdigit():
            # Попытка выбрать филиал по номеру
            try:
                num = int(text_lower)
                if 1 <= num <= len(BRANCHES_LIST):
                    branch = BRANCHES_LIST[num - 1]
                    response = f"""✅ ВЫБРАН: {branch['name']}

📚 ДОСТУПНЫЕ ПРОГРАММЫ ({len(branch['programs'])}):
"""
                    for prog in branch['programs']:
                        response += f"• {prog}\n"
                    
                    response += f"""
☎️ ДЛЯ ЗАПИСИ:
{get_contacts_menu()}"""
                    return response
                else:
                    return f"❌ Номер филиала неверный. Укажите от 1 до {len(BRANCHES_LIST)}"
            except:
                pass
        
        elif any(kw in text_lower for kw in ['доу', 'гимназия', 'школа']):
            # Поиск по названию филиала
            for branch in BRANCHES_LIST:
                if text_lower in branch['name'].lower():
                    response = f"""✅ ВЫБРАН: {branch['name']}

📚 ДОСТУПНЫЕ ПРОГРАММЫ ({len(branch['programs'])}):
"""
                    for prog in branch['programs']:
                        response += f"• {prog}\n"
                    
                    response += f"""
📞 ДЛЯ ЗАПИСИ:
{get_contacts_menu()}"""
                    return response
            
            return f"""❌ Филиал не найден 😔

Напишите 'филиалы' для полного списка всех 26 центров"""
        
        else:
            return get_default_response()

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
        'bot': BOT_NAME,
        'uptime': 'running'
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
                # Отправляем сообщение ОДИН раз
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
        'ai_methodist': 'enabled' if ai_client else 'disabled',
        'branches': len(BRANCHES_LIST),
        'programs': len(PROGRAMS_INFO),
        'status': 'active'
    })

@app.route('/admin/add-employee', methods=['POST'])
def admin_add_employee():
    """Добавить сотрудника (требует admin token)"""
    try:
        data = request.json
        admin_token = request.headers.get('Authorization', '')
        
        if admin_token != f"Bearer {os.getenv('ADMIN_TOKEN', 'secret')}":
            return jsonify({'error': 'Unauthorized'}), 403
        
        user_id = data.get('user_id')
        name = data.get('name')
        role = data.get('role')
        branch = data.get('branch')
        
        if not all([user_id, name, role, branch]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if add_employee(user_id, name, role, branch):
            return jsonify({'status': 'success', 'message': 'Employee added'}), 200
        else:
            return jsonify({'error': 'Failed to add employee'}), 500
    
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"⚠️ 404 Not Found")
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"❌ 500 Server Error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ===== MAIN =====

if __name__ == '__main__':
    init_employees_db()
    
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Запуск {BOT_NAME} v{BOT_VERSION}")
    logger.info(f"🔗 http://0.0.0.0:{port}")
    logger.info(f"🤖 ИИ Методист: {'✅ Активен' if ai_client else '⚠️ Отключен'}")
    logger.info(f"📍 Филиалов: {len(BRANCHES_LIST)}")
    logger.info(f"📚 Программ: {len(PROGRAMS_INFO)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
