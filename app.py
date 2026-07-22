#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 RoboSTEAMuL VK Bot - Premium Version 2.0
Автор: RoboSTEAMuL
Версия: 2.0
Описание: Премиум бот для Робостим с интерактивным меню и предложением сотрудничества
"""



import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("=== BOT RESTARTED ===")
logger.info("Current code version: 2.1")
logger.info("Working directory: %s", os.getcwd())

import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.utils import get_random_id
from datetime import datetime

# ===== ЗАГРУЗКА ПЕРЕМЕННЫХ =====
load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
API_VERSION = os.getenv('API_VERSION', '5.131')
VK_SECRET_KEY = os.getenv('SECRET', '')
VK_CONFIRMATION_CODE = os.getenv('CONFIRMATION_TOKEN', '')

# ===== ПРОВЕРКА ПЕРЕМЕННЫХ =====
if not VK_TOKEN or not GROUP_ID:
    logger.error("❌ VK_TOKEN или GROUP_ID не установлены!")
    raise ValueError("VK_TOKEN и GROUP_ID обязательны")

logger.info("✅ VK_TOKEN загружен")
logger.info(f"✅ GROUP_ID: {GROUP_ID}")

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

# ===== БОТ ИНФОРМАЦИЯ =====
BOT_NAME = "RoboSTEAMuL Консультант"
BOT_VERSION = "2.0 Premium"
BOT_AUTHOR = "RoboSTEAMuL"
SCHOOL_WEBSITE = "www.robostem.ru"
SCHOOL_PHONE = "+7 (XXX) XXX-XXXX"
SCHOOL_EMAIL = "info@robostem.ru"

# ===== ИНФОРМАЦИЯ О ФИЛИАЛАХ =====
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

# ===== ИНФОРМАЦИЯ О ПРОГРАММАХ =====
PROGRAMS_INFO = {
    'robossteam': {
        'name': '🤖 Программа по робототехнике РобоSTEAM',
        'age': '3-4 года',
        'price': '300 руб./занятие',
        'duration': '30 минут',
        'group_size': '6-8 человек',
        'description': 'Первое знакомство с инженерией и конструированием!\n\n✅ Что изучают:\n• Основы конструирования\n• Развитие мелкой моторики\n• Логическое мышление\n• Творческое воображение\n• Командная работа\n\n🏆 Результаты:\n• Развитие пространственного мышления\n• Уверенность в собственных силах\n• Интерес к техническим наукам'
    },
    'brik': {
        'name': '🧱 Программа по робототехнике РобоSTEAM Брик',
        'age': '5-6 лет',
        'price': '300 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
        'description': 'Инженерное мышление через практику!\n\n✅ Что изучают:\n• Сборка сложных механизмов\n• Анализ конструкций\n• Проектирование решений\n• Введение в физику\n• Основы механики\n\n🏆 Результаты:\n• Инженерное мышление\n• Умение решать задачи\n• Первые проекты'
    },
    'pro': {
        'name': '⚙️ Программа по робототехнике РробоSTEAM Про',
        'age': '6-8 лет',
        'price': '400 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
        'description': 'Профессиональная робототехника и программирование!\n\n✅ Что изучают:\n• Конструирование роботов\n• Введение в программирование\n• Проектная деятельность\n• Подготовка к соревнованиям\n• Работа в команде\n\n🏆 Результаты:\n• Реальные робототехнические проекты\n• Первый опыт программирования\n• Участие в соревнованиях'
    },
    'choreography': {
        'name': '💃 Хореография',
        'age': '3-8 лет',
        'price': '350 руб./занятие',
        'duration': '30-60 минут (в зависимости от возраста)',
        'group_size': '8-12 человек',
        'description': 'Развитие координации и артистизма!\n\n✅ Возрастные группы и продолжительность:\n• 3-4 года: 30 минут\n• 4-5 лет: 30 минут\n• 5-7 лет: 60 минут\n\n✅ Что изучают:\n• Базовые элементы танца\n• Развитие ритма\n• Гибкость и осанку\n• Выразительность движений\n• Артистическое мастерство'
    },
    'speech': {
        'name': '🗣️ Логопед и развитие речи',
        'age': '3-7 лет',
        'price': 'Диагностика 800 руб., Занятия 600 руб./занятие',
        'duration': '60 минут',
        'group_size': 'Индивидуально',
        'description': 'Коррекция речи и подготовка к школе!\n\n✅ Услуги:\n• Диагностика речи\n• Коррекция звукопроизношения\n• Развитие речи\n• Подготовка к школе\n• Индивидуальный подход\n\n🏆 Результаты:\n• Исправление дефектов речи\n• Развитая речь\n• Готовность к школе'
    },
    'junior': {
        'name': '🧠 Программа подготовки к школе Дошколёнок 4-5 лет',
        'age': '4-5 лет',
        'price': '350 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
        'description': 'Комплексное раннее развитие!\n\n✅ Что изучают:\n• Логическое мышление\n• Развитие памяти\n• Речевые навыки\n• Основы математики\n• Творчество и изобразительное искусство'
    },
    'school': {
        'name': '📚 Программа подготовки к школе Дошколёнок 6-7 лет',
        'age': '6-7 лет',
        'price': '375 руб./занятие',
        'duration': '60 минут',
        'group_size': '6-8 человек',
        'description': 'Полная подготовка к школе!\n\n✅ Что изучают:\n• Письмо и чтение\n• Математика\n• Развитие речи\n• Логика и внимание\n• Социальная адаптация'
    }
}

# ===== ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ =====

def send_message(user_id, message):
    """Отправить сообщение пользователю"""
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
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        return False

# ===== ФУНКЦИИ ОБРАБОТКИ КОМАНД =====

def get_greeting():
    """Приветствие"""
    hour = datetime.now().hour
    if hour < 12:
        greeting = "☀️ Доброе утро!"
    elif hour < 18:
        greeting = "🌤️ Добрый день!"
    else:
        greeting = "🌙 Добрый вечер!"
    
    return f"""{greeting} 

🤖 Добро пожаловать в RoboSTEAMuL!

Я ваш персональный консультант по образовательным программам для детей.

Напишите:
• программы - список всех курсов
• филиалы - интерактивное меню выбора детского сада
• программа [название] - подробная информация
• цены - стоимость обучения
• контакты - как записаться
• преимущества - почему выбирают нас
• помощь - все команды"""

def get_branches_menu():
    """Меню выбора филиалов"""
    menu = """📍 ВЫБЕРИТЕ БЛИЖАЙШИЙ ДЕТСКИЙ САД:

"""
    for i, branch in enumerate(BRANCHES_LIST, 1):
        programs_count = len(branch['programs'])
        menu += f"{i}️⃣  {branch['name']} ({programs_count} программ)\n"
    
    menu += f"""
Напишите номер (от 1 до {len(BRANCHES_LIST)}) или название детского сада.

Примеры:
• Напишите "1" для ДОУ №30
• Напишите "ДОУ №448СП"
• Напишите "Гимназия №76"

После выбора вы увидите все доступные программы и цены в этом филиале! 🎯"""
    
    return menu

def get_cooperation_offer():
    """Предложение сотрудничества для новых филиалов"""
    return f"""🚀 Вашего детского сада пока нет в RoboSTEAMuL?

Это отличная возможность стать нашим официальным представителем и помочь открыть занятия именно в вашем детском саду или школе! ❤️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ЧТО НУЖНО СДЕЛАТЬ:

1️⃣ 📍 Найдите детский сад или школу, где учится ваш ребёнок.

2️⃣ 🤝 Расскажите руководителю о программе RoboSTEAMuL и предложите организовать занятия у них.

3️⃣ 📞 Если директор заинтересуется, попросите разрешения чтобы компания RoboSTEAMuL связалась с нами или сообщите нам, что образовательное учреждение готово к сотрудничеству.

4️⃣ ✅ После заключения договора и открытия занятий вы получите бесплатный абонемент для своего ребёнка на весь период его обучения в RoboSTEAMuL.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 ЧТО ПОЛУЧАЕТ ВАШ РЕБЁНОК?

⭐ Бесплатные занятия на всём протяжении обучения в RoboSTEAMuL.

🏫 ЧТО ПОЛУЧАЕТ ДЕТСКИЙ САД ИЛИ ШКОЛА?

✅ Современные занятия по робототехнике, подготовке к школе, хореографии или развитию речи прямо на своей территории.

💙 ЧТО ПОЛУЧАЕТ КОМПАНИЯ ROBOSSTEAMUL?

Возможность подарить ещё большему количеству детей качественное дополнительное образование.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📩 НАПИШИТЕ НАМ:

Название детского сада или школы
ФИО руководителя (если знаете)
Контактный телефон учреждения

Мы самостоятельно проведём переговоры и организуем весь процесс.

💡 Возможно, именно благодаря вам занятия RoboSTEAMuL появятся в вашем детском саду, а ваш ребёнок сможет обучаться бесплатно! 🚀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Условия акции: бесплатный абонемент предоставляется после заключения договора между RoboSTEAMuL и образовательным учреждением и фактического открытия группы для занятий.

📞 КОНТАКТЫ:
☎️ Телефон: {SCHOOL_PHONE}
📧 Email: {SCHOOL_EMAIL}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📍 Напишите 'филиалы' для выбора другого детского сада"""

def get_branch_programs(branch_input):
    """Получить информацию о программах в выбранном филиале"""
    branch_input = branch_input.strip().lower()
    
    try:
        branch_num = int(branch_input)
        if 1 <= branch_num <= len(BRANCHES_LIST):
            branch = BRANCHES_LIST[branch_num - 1]
        else:
            return f"""❌ Такого номера нет в списке (доступны номера 1-{len(BRANCHES_LIST)})

Однако! 👇

""" + get_cooperation_offer()
    except ValueError:
        branch = None
        for b in BRANCHES_LIST:
            if branch_input in b['name'].lower():
                branch = b
                break
        
        if not branch:
            return f"""❌ К сожалению, в нашем списке нет детского сада с названием "{branch_input.title()}"

Однако! 👇

""" + get_cooperation_offer()
    
    programs_text = f"""✅ {branch['name']}

📚 ДОСТУПНЫЕ ПРОГРАММЫ:

"""
    
    for program in branch['programs']:
        if program == 'Робототехника':
            programs_text += """🤖 ПРОГРАММА ПО РОБОТОТЕХНИКЕ

Три уровня обучения:
1️⃣ РобоSTEAM (3-4 года) - 300 руб./занятие, 30 мин
   Первое знакомство с инженерией и конструированием.

2️⃣ РобоSTEAM Брик (5-6 лет) - 300 руб./занятие, 60 мин
   Инженерное мышление, сборка сложных механизмов.

3️⃣ РобоSTEAM Про (6-8 лет) - 400 руб./занятие, 60 мин
   Робототехника, основы программирования.

"""
        
        elif program == 'Хореография':
            programs_text += """💃 ХОРЕОГРАФИЯ

💰 350 руб./занятие

Возрастные группы:
• 3-4 года: 30 минут
• 4-5 лет: 30 минут
• 5-7 лет: 60 минут

"""
        
        elif program == 'Подготовка к школе':
            programs_text += """🧠 ПОДГОТОВКА К ШКОЛЕ

1️⃣ Дошколёнок 4-5 лет - 350 руб./занятие, 60 мин
2️⃣ Дошколёнок 6-7 лет - 375 руб./занятие, 60 мин

"""
        
        elif program == 'Логопед':
            programs_text += """🗣️ ЛОГОПЕД И РАЗВИТИЕ РЕЧИ

💰 Диагностика: 800 руб.
💰 Занятия: 600 руб./занятие
⏱️ 60 минут

"""
    
    programs_text += f"""
🎁 СПЕЦПРЕДЛОЖЕНИЯ:
✅ Первое занятие БЕСПЛАТНО
✅ Запись на полугодие: скидка 5%
✅ Запись на учебный год: скидка 10%

📞 ЗАПИСЬ:
☎️ Телефон: {SCHOOL_PHONE}
📧 Email: {SCHOOL_EMAIL}

📍 Напишите 'филиалы' для выбора другого детского сада"""
    
    return programs_text

def get_all_programs():
    """Список всех программ"""
    return """📚 ВСЕ НАШИ ПРОГРАММЫ:

1️⃣ Программа по робототехнике РобоSTEAM (3-4 года) - 300 руб., 30 мин
2️⃣ Программа по робототехнике РобоSTEAM Брик (5-6 лет) - 300 руб., 60 мин
3️⃣ Программа по робототехнике РобоSTEAM Про (6-8 лет) - 400 руб., 60 мин
4️⃣ Хореография (3-8 лет) - 350 руб., 30-60 мин
5️⃣ Логопед и развитие речи (3-7 лет) - 600 руб., 60 мин
6️⃣ Дошколёнок 4-5 лет - 350 руб., 60 мин
7️⃣ Дошколёнок 6-7 лет - 375 руб., 60 мин

📍 Напишите 'филиалы' для выбора места занятий!
📞 Напишите 'контакты' для записи!"""

def get_prices():
    """Стоимость обучения"""
    return """💰 СТОИМОСТЬ ОБУЧЕНИЯ:

🤖 РобоSTEAM (30 мин): 300 руб./занятие
🧱 РобоSTEAM Брик (60 мин): 300 руб./занятие
⚙️ РобоSTEAM Про (60 мин): 400 руб./занятие
💃 Хореография (30-60 мин): 350 руб./занятие
🗣️ Логопед (60 мин): Диагностика 800 руб., Занятия 600 руб.
🧠 Дошколёнок 4-5 (60 мин): 350 руб./занятие
📚 Дошколёнок 6-7 (60 мин): 375 руб./занятие

🎁 СПЕЦПРЕДЛОЖЕНИЯ:
✅ Первое занятие БЕСПЛАТНО
✅ Запись на полугодие: скидка 5%
✅ Запись на учебный год: скидка 10%

📍 Напишите 'филиалы' для выбора места занятий!"""

def get_contacts():
    """Контактная информация и запись"""
    return f"""📞 КОНТАКТЫ И ЗАПИСЬ:

🏢 РобоSTEAMuL - Центр детского развития

☎️ Телефон: {SCHOOL_PHONE}
📧 Email: {SCHOOL_EMAIL}
🌐 Сайт: {SCHOOL_WEBSITE}

🕐 РЕЖИМ РАБОТЫ:
Пн-Пт: 09:00-20:00
Сб-Вс: 10:00-18:00

📱 КАК ЗАПИСАТЬСЯ:
1️⃣ Позвоните нам
2️⃣ Напишите Email
3️⃣ Выберите филиал (напишите 'филиалы')

🎁 Первое занятие БЕСПЛАТНО!

📍 Есть занятия в 26 филиалах по городу!"""

def get_benefits():
    """Преимущества и достижения"""
    return """⭐ ПОЧЕМУ ВЫБИРАЮТ РОБОСТИМ:

✅ Опытные преподаватели (10+ лет опыта)
✅ Проверенная система обучения
✅ Маленькие группы (6-8 человек)
✅ Современное оборудование
✅ 26 филиалов по городу
✅ Удобное расписание
✅ Первое занятие БЕСПЛАТНО

✅ РЕЗУЛЬТАТЫ:
🏆 Призёры соревнований
🏆 Высокие оценки в школе
🏆 Развитие способностей ребёнка

⭐ ОТЗЫВЫ: 4.9/5.0

📍 Напишите 'филиалы' для выбора места!"""

def get_help():
    """Справка по командам"""
    return f"""❓ ВСЕ КОМАНДЫ:

📍 ВЫБОР ДЕТСКОГО САДА:
• филиалы - меню всех {len(BRANCHES_LIST)} детских садов
• [номер] - выбор по номеру (напишите "1")
• [название] - выбор по названию (напишите "ДОУ №30")

📚 ПРОГРАММЫ:
• программы - список всех курсов

💰 ЦЕНЫ:
• цены - стоимость обучения

📞 КОНТАКТЫ:
• контакты - как записаться

⭐ ИНФОРМАЦИЯ:
• преимущества - почему выбирают нас

🤖 ОБЩЕЕ:
• привет - приветствие
• помощь - эта справка"""

def get_default_response():
    """Ответ на неизвестную команду"""
    return """😊 Я вас не совсем понял...

Вот что я умею:
📍 филиалы - выбор детского сада
📚 программы - список курсов
💰 цены - стоимость
📞 контакты - как записаться
❓ помощь - все команды"""

# ===== ОСНОВНАЯ ОБРАБОТКА СООБЩЕНИЙ =====

def handle_message(text, user_id):
    """Основная обработка сообщения"""
    text_lower = text.lower().strip()
    
    logger.info(f"📨 Сообщение от {user_id}: '{text}'")
    
    if text_lower in ['привет', 'hi', 'hello', 'привет!', 'хай']:
        return get_greeting()
    elif text_lower in ['программы', 'programs', 'программы!', 'курсы']:
        return get_all_programs()
    elif text_lower in ['филиалы', 'branches', 'где', 'адреса', 'адрес', 'меню', 'выбрать']:
        return get_branches_menu()
    elif text_lower.isdigit():
        return get_branch_programs(text_lower)
    elif any(kw in text_lower for kw in ['доу', 'гимназия', 'дошкольное']):
        return get_branch_programs(text_lower)
    elif text_lower in ['цены', 'price', 'стоимость', 'сколько стоит', 'цены!']:
        return get_prices()
    elif text_lower in ['контакты', 'contacts', 'запись', 'как записаться', 'контакты!']:
        return get_contacts()
    elif text_lower in ['преимущества', 'advantages', 'почему', 'почему вы', 'зачем']:
        return get_benefits()
    elif text_lower in ['помощь', 'help', 'команды', 'что ты умеешь', 'помощь!']:
        return get_help()
    elif text_lower in ['инфо', 'info', 'информация', 'о боте', 'о себе']:
        return f"🤖 RoboSTEAMuL Bot v{BOT_VERSION}\n\n📍 Выберите детский сад\n📚 Узнайте о программах\n💰 Цены и скидки\n📞 Запись на занятия\n\nНапишите 'филиалы' для начала! 😊"
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
        'programs_count': len(PROGRAMS_INFO),
        'branches_count': len(BRANCHES_LIST),
        'status': 'active'
    })

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
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Запуск {BOT_NAME} v{BOT_VERSION}")
    logger.info(f"🔗 http://0.0.0.0:{port}")
    logger.info(f"📊 Программ доступно: {len(PROGRAMS_INFO)}")
    logger.info(f"📍 Филиалов доступно: {len(BRANCHES_LIST)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        use_reloader=False
    )
