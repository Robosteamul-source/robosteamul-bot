# -*- coding: utf-8 -*-
"""
РобоСТЕАМ Бот для VK - Улучшенная версия 3.0
Автор: AI Assistant
Версия: 3.0
Новые возможности:
- Улучшенная обработка возраста (цифры, слова, диапазоны)
- Умные рекомендации программ по возрасту
- Расширенное мышление бота с контекстным анализом
- Предложение программ на основе данных ребенка
"""

from flask import Flask, request
import requests
import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple, List
import re

# ═══════════════════════════════════════════════════════════════════════════
# КОНФИГУРАЦИЯ И КОНСТАНТЫ
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__)

# Получение токенов из переменных окружения
VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

# ID администратора для отправки уведомлений
ADMIN_ID = 441534266

# Контакты отдела заботы
CARE_TEAM = [
    {'name': 'Наталья', 'phone': '+7 (922) 014-44-94'},
    {'name': 'Ксения', 'phone': '+7 (904) 805-25-61'},
    {'name': 'Жанна', 'phone': '+7 (951) 239-86-49'}
]

# Логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Константы для этапов регистрации
REGISTRATION_STEPS = {
    0: 'start',
    1: 'child_name',
    2: 'child_age',
    3: 'kindergarten',
    4: 'group_number',
    5: 'parent_name',
    6: 'parent_phone',
    7: 'program_choice',
    8: 'completed'
}

# Программы обучения С РАСШИРЕННОЙ ИНФОРМАЦИЕЙ
PROGRAMS = {
    'robo_34': {
        'name': 'Робототехника РобоСТЕАМ',
        'age': '3-4 года',
        'age_range': (3, 4),
        'description': 'Первые шаги в мир робототехники. Развитие логического мышления и мелкой моторики.',
        'price': '300 руб за занятие',
        'emoji': '🤖',
        'benefits': ['Логическое мышление', 'Мелкая моторика', 'Первичные навыки конструирования']
    },
    'brick': {
        'name': 'Робототехника РобоСТЕАМ Брик',
        'age': '4-5 лет',
        'age_range': (4, 5),
        'description': 'Построение и программирование роботов. Основы конструирования и алгоритмики.',
        'price': '300 руб за занятие',
        'emoji': '🧱',
        'benefits': ['Программирование основы', 'Конструирование', 'Пространственное мышление']
    },
    'pro': {
        'name': 'Робототехника РобоСТЕАМ Про',
        'age': '5-6 лет',
        'age_range': (5, 6),
        'description': 'Продвинутое программирование и создание сложных роботов. Участие в соревнованиях.',
        'price': '400 руб за занятие',
        'emoji': '⚙️',
        'benefits': ['Продвинутое программирование', 'Участие в соревнованиях', 'Решение сложных задач']
    },
    'pro_plus': {
        'name': 'Робототехника РобоСТЕАМ Про+',
        'age': '6-12 лет',
        'age_range': (6, 12),
        'description': 'Профессиональный уровень программирования и робототехники. Сложные проекты и соревнования.',
        'price': '450 руб за занятие',
        'emoji': '🏆',
        'benefits': ['Профессиональное программирование', 'Создание сложных систем', 'Подготовка к олимпиадам', 'Работа в команде']
    },
    'dance': {
        'name': 'Хореография',
        'age': '3-8 лет',
        'age_range': (3, 8),
        'description': 'Развитие танца, ритма и координации. Творческие номера и выступления.',
        'price': '350 руб за занятие',
        'emoji': '💃',
        'benefits': ['Координация', 'Ритм', 'Творческое самовыражение', 'Сценическое мастерство']
    },
    'logoped': {
        'name': 'Логопед и развитие речи',
        'age': '3-7 лет',
        'age_range': (3, 7),
        'description': 'Коррекция звукопроизношения и развитие речи. Индивидуальные занятия.',
        'price': '600 руб за занятие (диагностика +800 руб)',
        'emoji': '🗣️',
        'benefits': ['Коррекция речи', 'Развитие речи', 'Индивидуальный подход']
    },
    'school_2': {
        'name': 'Дошколёнок за два года до Школы',
        'age': '4-5 лет',
        'age_range': (4, 5),
        'description': 'Комплексная подготовка к школе. Грамота, арифметика, познавательно-речевое развитие.',
        'price': '350 руб за занятие',
        'emoji': '📚',
        'benefits': ['Подготовка к школе', 'Грамотность', 'Основы математики', 'Развитие памяти']
    },
    'school_1': {
        'name': 'Дошколёнок за год до Школы',
        'age': '6-7 лет',
        'age_range': (6, 7),
        'description': 'Интенсивная подготовка в выпускной год. Освоение школьных навыков и самодисциплины.',
        'price': '375 руб за занятие',
        'emoji': '✏️',
        'benefits': ['Интенсивная подготовка', 'Школьные навыки', 'Самодисциплина', 'Психологическая готовность']
    }
}

# Словарь для преобразования текста в числа
AGE_WORDS = {
    'три': 3, 'три года': 3, 'трех лет': 3,
    'четыре': 4, 'четыре года': 4, 'четырех лет': 4,
    'пять': 5, 'пять лет': 5, 'пяти лет': 5,
    'шесть': 6, 'шесть лет': 6, 'шести лет': 6,
    'семь': 7, 'семь лет': 7, 'семи лет': 7,
    'восемь': 8, 'восемь лет': 8, 'восьми лет': 8,
    'девять': 9, 'девять лет': 9, 'девяти лет': 9,
    'десять': 10, 'десять лет': 10, 'десяти лет': 10,
}

# ═══════════════════════════════════════════════════════════════════════════
# БАЗА ДЕТСКИХ САДОВ ROBOSTEA MUL
# ═══════════════════════════════════════════════════════════════════════════

KINDERGARTENS = {
    30: {
        'name': 'ДОУ №30',
        'address': 'Зальцмана 24',
        'location': 'Центр',
        'programs': ['robo_34', 'brick', 'pro', 'logoped', 'dance', 'school_2', 'school_1']
    },
    30.1: {
        'name': 'ДОУ №30СП',
        'address': 'Зальцмана 38',
        'location': 'Центр',
        'programs': ['robo_34', 'brick', 'pro', 'logoped', 'dance', 'school_2', 'school_1']
    },
    44: {
        'name': 'ДОУ №44',
        'address': 'Конструктора Духова 25',
        'location': 'Северо-Восток',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    44.1: {
        'name': 'ДОУ №44СП',
        'address': 'Конструктора Духова 9',
        'location': 'Северо-Восток',
        'programs': ['dance']
    },
    475: {
        'name': 'ДОУ №475',
        'address': 'Салютная 17а',
        'location': 'Юг',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    475.1: {
        'name': 'ДОУ №475',
        'address': 'Горького 25а',
        'location': 'Юго-Восток',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    416: {
        'name': 'ДОУ №416',
        'address': 'Культуры 59а',
        'location': 'Восток',
        'programs': ['robo_34', 'brick', 'pro']
    },
    413: {
        'name': 'ДОУ №413',
        'address': 'Доватора 18а',
        'location': 'Запад',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    369: {
        'name': 'ДОУ №369',
        'address': 'Танкистов 152Б',
        'location': 'Юго-Запад',
        'programs': ['robo_34', 'brick', 'pro', 'school_2', 'school_1']
    },
    221: {
        'name': 'ДОУ №221СП',
        'address': 'Бажова 24а',
        'location': 'Центр-Запад',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    418: {
        'name': 'ДОУ №418',
        'address': 'Шуменская 8',
        'location': 'Север',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    262: {
        'name': 'ДОУ №262',
        'address': 'Шуменская 45',
        'location': 'Север',
        'programs': ['robo_34', 'brick', 'pro']
    },
    351: {
        'name': 'ДОУ №351',
        'address': 'Артиллерийская 61а',
        'location': 'Северо-Запад',
        'programs': ['robo_34', 'brick', 'pro']
    },
    421: {
        'name': 'ДОУ №421',
        'address': 'Руставели 4а',
        'location': 'Центр-Восток',
        'programs': ['robo_34', 'brick', 'pro', 'dance']
    },
    448: {
        'name': 'ДОУ №448',
        'address': 'Агалакова 50а',
        'location': 'Запад',
        'programs': ['robo_34', 'brick', 'pro']
    },
    448.1: {
        'name': 'ДОУ №448СП',
        'address': 'Гранитная 4',
        'location': 'Запад',
        'programs': ['robo_34', 'brick', 'pro', 'dance', 'school_2', 'school_1']
    },
    10: {
        'name': 'ДОУ №10 (Копейск)',
        'address': 'Международная 76а',
        'location': 'Копейск',
        'programs': ['robo_34', 'brick', 'pro']
    },
    48: {
        'name': 'ДОУ №48',
        'address': 'Маршала Чуйкова 25Б',
        'location': 'Северо-Запад',
        'programs': ['robo_34', 'brick', 'pro']
    },
    18: {
        'name': 'ДОУ №18',
        'address': 'Скульптура Головницкого 18',
        'location': 'Центр',
        'programs': ['robo_34', 'brick', 'pro']
    },
    18.1: {
        'name': 'ДОУ №18СП',
        'address': 'Бейвеля 38',
        'location': 'Центр',
        'programs': ['robo_34', 'brick', 'pro']
    }
}

# Территории для быстрого поиска
TERRITORIES = {
    'центр': [30, 30.1, 221, 18, 18.1, 421],
    'север': [418, 262],
    'северо-запад': [351, 48],
    'северо-восток': [44, 44.1],
    'восток': [416],
    'юго-восток': [475.1],
    'юг': [475],
    'юго-запад': [369],
    'запад': [413, 448, 448.1],
    'центр-запад': [221],
    'центр-восток': [421],
    'копейск': [10]
}

# Хранилище данных пользователей
user_registration_data: Dict = {}

# ═══════════════════════════════════════════════════════════════════════════
# РАСШИРЕННЫЕ ФУНКЦИИ ВАЛИДАЦИИ И АНАЛИЗА
# ═══════════════════════════════════════════════════════════════════════════

def validate_fio(name: str) -> Tuple[bool, str]:
    """Проверяет корректность ФИО (улучшенная версия с распознаванием имен)"""
    name = name.strip()
    
    # Список распространенных русских имен для распознавания
    COMMON_NAMES = {
        'иван', 'алексей', 'сергей', 'петр', 'павел', 'андрей', 'дмитрий', 'владимир',
        'константин', 'геннадий', 'виктор', 'юрий', 'борис', 'игорь', 'леонид', 'валентин',
        'анатолий', 'николай', 'евгений', 'александр', 'максим', 'денис', 'олег', 'михаил',
        'мария', 'анна', 'елена', 'екатерина', 'наталья', 'ирина', 'валентина', 'ольга',
        'татьяна', 'александра', 'дарья', 'юлия', 'виктория', 'полина', 'софья', 'карина',
        'кристина', 'марина', 'лариса', 'светлана', 'зоя', 'галина', 'лилия', 'вероника',
        'евгения', 'людмила', 'тамара', 'раиса', 'надежда', 'маргарита', 'жанна', 'ксения',
        'никита', 'илья', 'артем', 'кирилл', 'станислав', 'ростислав', 'владислав', 'игнат',
        'глеб', 'матвей', 'тимур', 'саша', 'маша', 'ваня', 'коля', 'вова', 'гена', 'кристя'
    }
    
    # Список распространенных русских фамилий
    COMMON_SURNAMES = {
        'петров', 'сидоров', 'смирнов', 'иванов', 'соколов', 'волков', 'морозов', 'попов',
        'кузнецов', 'лебедев', 'новиков', 'федоров', 'павлов', 'денисов', 'суздальцев',
        'крылов', 'трифонов', 'комаров', 'охотников', 'никитин', 'третьяков', 'орлов',
        'козлов', 'александров', 'сергеев', 'константинов', 'виноградов', 'зайцев',
        'животов', 'соловьев', 'богданов', 'шустов', 'пушкин', 'лермонтов', 'чехов',
        'толстой', 'достоевский', 'тургенев', 'бунин', 'цветаева', 'ахматова', 'берг',
        'сизов', 'фёдоров', 'щербаков', 'еремин', 'проценко', 'антипов', 'серебряков'
    }
    
    # Проверяем базовые условия
    if len(name) < 2:
        return False, "❌ Имя слишком короткое. Напишите полное имя ребенка (минимум 2 символа)"
    
    # Проверяем что это не только цифры и спецсимволы
    if not any(c.isalpha() for c in name):
        return False, "❌ Имя должно содержать буквы. Напишите имя ребенка буквами"
    
    # Проверяем кириллицу (русские символы)
    if not all(c.isalpha() or c.isspace() or c == '-' for c in name):
        return False, "❌ Пожалуйста используйте русские буквы. Пример: Иван Петров"
    
    # Разделяем на слова
    words = name.split()
    
    # Если одно слово - проверяем что это хотя бы известное имя или фамилия
    if len(words) == 1:
        word_lower = words[0].lower()
        if word_lower in COMMON_NAMES or word_lower in COMMON_SURNAMES:
            return True, name
        else:
            # Если не распознали, просим добавить еще слово, но не отказываем
            return True, name
    
    # Если два и больше слов - проверяем что хотя бы одно слово это известное имя
    has_known_name = False
    for word in words:
        word_lower = word.lower()
        if word_lower in COMMON_NAMES or word_lower in COMMON_SURNAMES:
            has_known_name = True
            break
    
    # Даже если не распознали имена, принимаем если больше одного слова
    return True, name

def validate_child_fio_step1(name: str) -> Tuple[bool, str]:
    """
    СТРОГАЯ валидация ФИО ребенка для шага 1 регистрации.
    
    Требования:
    - 2-4 слова (фамилия + имя, или имя + отчество, или фамилия + имя + отчество)
    - Только русские буквы, пробелы и дефисы
    - Нормализованный регистр (первая буква каждого слова заглавная)
    
    Возвращает: (is_valid, normalized_name_or_error_message)
    """
    name = name.strip()
    
    # Проверка 1: Не пуста
    if not name:
        return False, '''❌ Пожалуйста, напишите фамилию и имя ребенка

📝 Примеры правильного ввода:
   • Иван Петрович
   • Петров Иван
   • Сидорова Мария Ивановна

→ Попробуйте еще раз:'''
    
    # Проверка 2: Только русские буквы, пробелы и дефисы
    if not all(c.isalpha() or c.isspace() or c == '-' for c in name):
        return False, '''❌ Используйте только русские буквы, пробелы и дефисы

Не допускаются: числа, английские буквы, спецсимволы (!, @, #, и т.д.)

📝 Примеры правильного ввода:
   • Иван Петрович
   • Петров Иван
   • Сидорова-Петрова Мария

→ Попробуйте еще раз:'''
    
    # Проверка 3: Хотя бы одна буква
    if not any(c.isalpha() for c in name):
        return False, '''❌ Имя должно содержать буквы

📝 Примеры правильного ввода:
   • Иван Петрович
   • Петров Иван
   • Сидорова Мария Ивановна

→ Попробуйте еще раз:'''
    
    # Проверка 4: Количество слов (2-4)
    words = [w for w in name.split() if w]  # Убираем пустые элементы
    
    if len(words) < 2:
        return False, '''❌ Напишите хотя бы ДВА слова: фамилию и имя

📝 Правильные примеры:
   • Иван Петрович (имя + отчество)
   • Петров Иван (фамилия + имя)
   • Сидорова Мария Ивановна (фамилия + имя + отчество)

→ Попробуйте еще раз:'''
    
    if len(words) > 4:
        return False, '''❌ Слишком много слов! Напишите максимум 4 слова

📝 Правильные примеры:
   • Иван Петрович (имя + отчество)
   • Петров Иван (фамилия + имя)
   • Сидорова Мария Ивановна (фамилия + имя + отчество)

→ Попробуйте еще раз:'''
    
    # Проверка 5: Каждое слово содержит хотя бы 2 символа (кроме дефисных)
    for word in words:
        # Убираем дефисы и проверяем остаток
        word_clean = word.replace('-', '')
        if len(word_clean) < 1:
            return False, '''❌ Каждое слово должно содержать хотя бы одну букву

Примеры: Иван, Петров, О-Мария (О-Мария - с дефисом, это нормально)

→ Попробуйте еще раз:'''
    
    # Нормализация: заглавная первая буква каждого слова
    normalized_words = []
    for word in words:
        # Разбиваем по дефисам (для имен типа Мария-Анна)
        parts = word.split('-')
        normalized_parts = []
        for part in parts:
            if part:
                # Первая буква заглавная, остальные строчные
                normalized = part[0].upper() + part[1:].lower()
                normalized_parts.append(normalized)
        normalized_words.append('-'.join(normalized_parts))
    
    normalized_name = ' '.join(normalized_words)
    
    # ✅ Все проверки пройдены
    return True, normalized_name

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Проверяет корректность номера телефона"""
    # Удаляем все не-цифры
    digits = re.sub(r'\D', '', phone)
    
    # Проверяем длину (обычно от 10 до 12 цифр для России)
    if len(digits) < 10:
        return False, "❌ Номер телефона слишком короткий. Напишите полный номер (например: +7 (921) 123-45-67)"
    
    if len(digits) > 15:
        return False, "❌ Номер телефона слишком длинный. Проверьте и напишите заново"
    
    return True, phone

def validate_age(age_str: str) -> Tuple[bool, str]:
    """
    УЛУЧШЕННАЯ функция для проверки возраста.
    Теперь понимает: цифры, слова, диапазоны!
    """
    age_str = age_str.lower().strip()
    
    # 1️⃣ Попытка прямого преобразования в цифру
    try:
        age = int(age_str)
        if 1 <= age <= 18:
            return True, str(age)
        else:
            return False, "❌ Возраст должен быть от 1 до 18 лет"
    except ValueError:
        pass
    
    # 2️⃣ Проверка словаря возраста (три, четыре, пять и т.д.)
    if age_str in AGE_WORDS:
        age = AGE_WORDS[age_str]
        return True, str(age)
    
    # 3️⃣ Попытка извлечь цифру из текста
    digit_match = re.search(r'\b([1-9]|1[0-8])\b', age_str)
    if digit_match:
        age = int(digit_match.group(1))
        return True, str(age)
    
    # 4️⃣ Проверка на диапазон (например "от 5 до 6")
    range_match = re.search(r'(?:от\s+)?([1-9]|1[0-8])\s*(?:до|-|по)\s*([1-9]|1[0-8])', age_str)
    if range_match:
        age1, age2 = int(range_match.group(1)), int(range_match.group(2))
        avg_age = (age1 + age2) // 2
        return True, str(avg_age)
    
    # Если ничего не подошло
    return False, """❌ Не понимаю возраст. Напишите одним из способов:
📌 Цифрой: 5, 6, 7
📌 Словом: три, четыре, пять, шесть
📌 Диапазоном: от 5 до 6, 5-6

→ Попробуйте еще раз:"""

def get_recommended_programs(age: int) -> List[str]:
    """
    УМНЫЙ АНАЛИЗ: Рекомендует программы на основе возраста ребенка
    """
    recommended = []
    for key, program in PROGRAMS.items():
        min_age, max_age = program['age_range']
        if min_age <= age <= max_age:
            recommended.append((key, program))
    
    # Сортируем по релевантности (точное совпадение сначала)
    return sorted(recommended, key=lambda x: (abs(x[1]['age_range'][0] - age), x[0]))

def analyze_user_context(user_id: int) -> Dict:
    """
    РАСШИРЕННОЕ МЫШЛЕНИЕ: Анализирует контекст пользователя
    """
    if user_id not in user_registration_data:
        return {}
    
    data = user_registration_data[user_id]
    age = int(data.get('child_age', 0))
    
    context = {
        'age': age,
        'name': data.get('child_name', ''),
        'kindergarten': data.get('kindergarten', ''),
        'recommended_programs': get_recommended_programs(age)
    }
    
    return context

# ═══════════════════════════════════════════════════════════════════════════
# ФУНКЦИИ ДЛЯ ФОРМИРОВАНИЯ СООБЩЕНИЙ (УЛУЧШЕННЫЕ)
# ═══════════════════════════════════════════════════════════════════════════

def get_main_menu() -> str:
    """Главное меню приветствия"""
    return '''🎓 Добро пожаловать в РобоСТЕАМ! 🎓

Мы предлагаем 7 образовательных программ для детей от 3 до 8 лет:
• 🤖 Робототехника
• 💃 Хореография
• 🗣️ Развитие речи
• 📚 Подготовка к школе

Что вам интересно?
→ Напишите "программы" для полного списка
→ Напишите "запись" для регистрации ребенка
→ Напишите "помощь" для подробной информации'''

def get_hello_response() -> str:
    """Ответ на приветствие"""
    return '''🎉 Добрый день! Мы рады вас видеть! 🎉

📋 Наши программы:
1. 🤖 Робототехника РобоСТЕАМ (3-4 года) - 300 руб/занятие
2. 🧱 Робототехника Брик (4-5 лет) - 300 руб/занятие
3. ⚙️ Робототехника Про (5-6 лет) - 400 руб/занятие
4. 🏆 Робототехника Про+ (6-12 лет) - 450 руб/занятие
5. 💃 Хореография (3-8 лет) - 350 руб/занятие
6. 🗣️ Логопед и развитие речи (3-7 лет) - 600 руб/занятие
7. 📚 Дошколёнок за два года до Школы (4-5 лет) - 350 руб/занятие
8. ✏️ Дошколёнок За год до Школы (6-7 лет) - 375 руб/занятие

Чем мы можем помочь?
→ "программы" - узнать подробнее о каждой программе
→ "запись" - записать ребенка на занятия
→ "контакты" - наши реквизиты'''

def get_all_programs() -> str:
    """Полный список всех программ"""
    text = '''📚 ВСЕ ПРОГРАММЫ КОМПАНИИ ROBOSTEAMUL 📚

'''
    for i, (key, prog) in enumerate(PROGRAMS.items(), 1):
        text += f'''{i}. {prog['emoji']} {prog['name']}
   📅 Возраст: {prog['age']}
   💰 Цена: {prog['price']}
   📝 {prog['description']}\n\n'''
    
    text += '''📞 Для более подробной информации оставьте номер телефона свой и наш отдел заботы с вами свяжется!

Или напишите "запись" чтобы записать ребенка на занятия! 🎯

☎️ Также вы можете позвонить нам прямо сейчас!

📱 ОТДЕЛ ЗАБОТЫ:
   📞 +7 (922) 014-44-94 - Наталья
   📞 +7 (904) 805-25-61 - Ксения
   📞 +7 (951) 239-86-49 - Жанна'''
    return text

def get_program_details(program_key: str) -> Optional[str]:
    """Информация о конкретной программе"""
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    # УЛУЧШЕНО: Добавлены преимущества программы
    benefits_text = '\n   '.join([f"✅ {b}" for b in program.get('benefits', [])])
    
    text = f'''{program['emoji']} {program['name'].upper()} {program['emoji']}

📅 Возраст: {program['age']}
💰 Цена: {program['price']}

📝 ОПИСАНИЕ:
{program['description']}

🎯 Преимущества программы:
   {benefits_text}

✨ ДОПОЛНИТЕЛЬНО:
   ✓ Профессиональные педагоги
   ✓ Современные методики обучения
   ✓ Группы до 8 детей
   ✓ Первое занятие - бесплатное!

📞 Для более подробной информации оставьте номер телефона свой и наш отдел заботы с вами свяжется!

☎️ Также вы можете позвонить нам прямо сейчас!

📱 ОТДЕЛ ЗАБОТЫ:
   📞 +7 (922) 014-44-94 - Наталья
   📞 +7 (904) 805-25-61 - Ксения
   📞 +7 (951) 239-86-49 - Жанна

Хотите записать ребенка на эту программу?
→ Напишите "запись" или "регистрация"'''
    
    return text

def get_contacts() -> str:
    """Контактная информация"""
    return '''📞 КОНТАКТЫ ROBOSTEAMUL 📞

📧 Email: info@robosteam.ru
📱 Телефон: +7 (XXX) XXX-XX-XX
📍 Адрес: Москва
🌐 Сайт: www.robosteam.ru

Как записать ребенка?
   1️⃣ Напишите "запись" в этом чате
   2️⃣ Заполните простую форму регистрации
   3️⃣ Мы позвоним вам в течение 24 часов

Дополнительно:
✅ Бесплатная первая консультация
✅ Возможна пробная неделя
✅ Гибкое расписание занятий
✅ Группы по возрастам и уровням'''

def get_help() -> str:
    """Справка по командам"""
    return '''❓ СПРАВКА ПО КОМАНДАМ ❓

Вот что я умею:

📋 ИНФОРМАЦИЯ:
   • "программы" - все наши курсы
   • "контакты" - контактная информация
   • "помощь" - эта справка

📝 РЕГИСТРАЦИЯ:
   • "запись" или "регистрация" - начать заполнение анкеты
   • "отмена" - отменить текущую регистрацию

📞 КОНСУЛЬТАЦИЯ:
   • "контакты" - свяжитесь с нами по телефону
   • Оставьте номер телефона - мы вам перезвоним!

💬 ОБЩЕНИЕ:
   • "привет", "здравствуйте" и т.д. - мой ответ
   • "спасибо" - пожалуйста! 😊

Нужна помощь? Просто напишите вопрос! 💬'''

def get_registration_step_1() -> str:
    """Первый вопрос анкеты"""
    return '''✍️ НАЧИНАЕМ РЕГИСТРАЦИЮ! ✍️

Заполните пожалуйста все поля (всего 7 вопросов)

🔹 ВОПРОС 1️⃣ из 7️⃣

Фамилия Имя Отчество ребенка

Примеры: Петров Иван Сергеевич, Смирнова Мария Ивановна, Козлов Алексей

→ Напишите фамилию, имя и отчество ребенка:'''

def get_registration_step_2() -> str:
    """
    УЛУЧШЕННЫЙ вопрос номер 2 о возрасте ребенка
    Теперь с подробными инструкциями и возможностью ввода по-разному
    """
    return '''👍 Спасибо! Продолжаем...

🔹 ВОПРОС 2️⃣ из 7️⃣

Сколько лет вашему ребенку? 👶

Напишите возраст любым способом:
📌 Цифрой: 3, 4, 5, 6, 7, 8
📌 Словом: три, четыре, пять, шесть
📌 Фразой: "три года", "4 года", "пяти лет"

💡 ℹ️ Это поможет нам подобрать идеальную программу!

→ Напишите возраст ребенка:'''

def get_registration_step_2_with_recommendations(age: int, child_name: str = "") -> str:
    """
    УМНАЯ версия шага 2 с рекомендациями программ
    """
    name_text = f" {child_name}," if child_name else ""
    recommended = get_recommended_programs(age)
    
    recommendations_text = ""
    if recommended:
        recommendations_text = "\n\n🎯 РЕКОМЕНДУЕМЫЕ ПРОГРАММЫ ДЛЯ ВОЗРАСТА " + str(age) + " ЛЕТ:\n"
        for key, prog in recommended[:3]:  # Показываем топ 3
            recommendations_text += f"   {prog['emoji']} {prog['name']} - {prog['age']}\n"
        recommendations_text += "\n(Расскажу подробнее на следующем шаге!)\n"
    
    return f'''✨ Отлично{name_text} сохранил возраст!

Возраст ребенка: {age} лет
{recommendations_text}
Продолжим дальше...

🔹 ВОПРОС 3️⃣ из 7️⃣

Название детского сада (если ребенок его посещает)

Примеры: "Радуга", "Солнышко", "нет" (если не посещает)

→ Напишите название или "нет":'''

def find_kindergartens_by_territory(territory: str) -> List[Tuple[int, Dict]]:
    """
    Поиск детских садов по территории
    """
    territory = territory.lower().strip()
    
    # Проверяем точное совпадение
    if territory in TERRITORIES:
        kgs = []
        for kg_id in TERRITORIES[territory]:
            if kg_id in KINDERGARTENS:
                kgs.append((kg_id, KINDERGARTENS[kg_id]))
        return kgs
    
    # Поиск по частичному совпадению (если в названии территории есть слово)
    results = []
    for kg_id, kg_info in KINDERGARTENS.items():
        if territory in kg_info['location'].lower():
            results.append((kg_id, kg_info))
    
    return results

def get_kindergarten_info(kg_id) -> Optional[Dict]:
    """Получить информацию о детском саде"""
    try:
        kg_id_float = float(kg_id) if '.' in str(kg_id) else int(kg_id)
        return KINDERGARTENS.get(kg_id_float)
    except:
        return None

def get_registration_step_3() -> str:
    """
    УЛУЧШЕННЫЙ третий вопрос с подбором детского сада
    """
    territories_text = ', '.join([
        'Центр', 'Север', 'Юг', 'Восток', 'Запад',
        'Северо-Запад', 'Северо-Восток', 'Юго-Запад', 'Юго-Восток'
    ])
    
    return f'''✅ Хорошо! Далее...

🔹 ВОПРОС 3️⃣ из 7️⃣

Номер детского сада или улицу, где находится детский сад

Мы подберем вам подходящий из наших учреждений! 🏫

Напишите одно из:
📌 Номер сада (например: 30, 44, 475)
📌 Улицу или адрес (например: Зальцмана, Духова, Конструктора Духова)
📌 Территорию проживания (например: Центр, Север, Юг)
📌 "Нет" - если не посещает ДОУ

Доступные территории:
{territories_text}

→ Напишите номер сада, улицу, территорию или "нет":'''

def get_available_kindergartens_list() -> str:
    """Получить полный список доступных садов"""
    text = '''🏫 ВСЕ ДЕТСКИЕ САДЫ ROBOSTEA MUL 🏫

'''
    for kg_id in sorted([k for k in KINDERGARTENS.keys() if isinstance(k, int) or k == int(k)]):
        if kg_id in KINDERGARTENS:
            kg = KINDERGARTENS[kg_id]
            programs_list = ', '.join([PROGRAMS[p]['emoji'] for p in kg['programs'] if p in PROGRAMS])
            text += f'''🏢 {kg['name']}
   📍 Адрес: {kg['address']}
   🗺️ Территория: {kg['location']}
   📚 Программы: {programs_list}

'''
    return text

def get_registration_step_4() -> str:
    """Четвертый вопрос"""
    return '''👍 Понятно!

🔹 ВОПРОС 4️⃣ из 7️⃣

Номер детского сада или адрес детского сада

Уточните, какой конкретно детский сад посещает ребенок.

Напишите одно из:
📌 Номер (например: 30, 44, 475)
📌 Адрес или улицу (например: Зальцмана 24, ул. Духова 25)

→ Напишите номер или адрес детского сада:'''

def get_registration_step_5() -> str:
    """Пятый вопрос"""
    return '''✨ Отлично! Информация о родителе...

🔹 ВОПРОС 5️⃣ из 7️⃣

Фамилия Имя Отчество родителя (опекуна)

Примеры: Иванов Сергей Петрович, Смирнова Елена Алексеевна, Петров Иван

→ Напишите ваше ФИО:'''

def get_registration_step_6() -> str:
    """Шестой вопрос"""
    return '''📞 Спасибо! Осталось совсем немного...

🔹 ВОПРОС 6️⃣ из 7️⃣

Номер телефона для связи

Примеры: +7 (921) 123-45-67, 89211234567, 8 (921) 123-45-67

→ Напишите ваш номер телефона:'''

def get_registration_step_7(age: int = 0) -> str:
    """
    Седьмой вопрос с УМНЫМИ рекомендациями на основе возраста
    """
    base_text = '''🎯 Финальный выбор!

🔹 ВОПРОС 7️⃣ из 7️⃣

Какая программа вас интересует?'''
    
    if age > 0:
        recommended = get_recommended_programs(age)
        if recommended:
            base_text += f"\n\n💡 РЕКОМЕНДУЕМ для вашего ребенка (возраст {age} лет):\n"
            for key, prog in recommended[:2]:
                base_text += f"   ⭐ {key} - {prog['name']} ({prog['age']})\n"
            base_text += "\n"
    
    base_text += '''
Выберите один из кодов:

🤖 robo_34 - Робототехника 3-4 года (300 руб)
🧱 brick - РобоСТЕАМ Брик 4-5 лет (300 руб)
⚙️ pro - РобоСТЕАМ Про 5-6 лет (400 руб)
🏆 pro_plus - РобоСТЕАМ Про+ 6-12 лет (450 руб)
💃 dance - Хореография (350 руб)
🗣️ logoped - Логопед и развитие речи (600 руб)
📚 school_2 - Дошколёнок 4-5 лет (350 руб)
✏️ school_1 - Дошколёнок 6-7 лет (375 руб)

→ Напишите код программы (например: robo_34):'''
    
    return base_text

def get_confirmation_message(data: Dict) -> str:
    """Подтверждение данных перед отправкой"""
    child_name = data.get('child_name', 'Не указано')
    child_age = data.get('child_age', 'Не указано')
    kindergarten = data.get('kindergarten', 'Не указано')
    kindergarten_address = data.get('kindergarten_address', '')
    group = data.get('group_number', 'Не указано')
    parent_name = data.get('parent_name', 'Не указано')
    parent_phone = data.get('parent_phone', 'Не указано')
    program_name = data.get('program_name', 'Не выбрана')
    program_price = data.get('program_price', 'Не указана')
    
    # Форматируем информацию о саде
    if kindergarten_address:
        kindergarten_info = f"{kindergarten}\n      {kindergarten_address}"
    else:
        kindergarten_info = kindergarten
    
    return f'''✅ ПРОВЕРЬТЕ ДАННЫЕ ПЕРЕД ОТПРАВКОЙ ✅

📋 ИНФОРМАЦИЯ О РЕБЕНКЕ:
   👶 Имя: {child_name}
   📅 Возраст: {child_age} лет
   🏫 Детский сад: {kindergarten_info}
   👥 Группа: {group}

👨‍👩‍👧 ИНФОРМАЦИЯ О РОДИТЕЛЕ:
   👤 Имя: {parent_name}
   📞 Телефон: {parent_phone}

📚 ВЫБРАННАЯ ПРОГРАММА:
   🎓 Программа: {program_name}
   💰 Стоимость: {program_price}

❓ Все верно?
   "да" - да, отправить данные
   "нет" - исправить данные
   "отмена" - отменить регистрацию'''

def get_registration_complete(data: Dict) -> str:
    """Сообщение об успешной регистрации"""
    child_name = data.get('child_name', 'Не указано')
    program_name = data.get('program_name', 'Не выбрана')
    
    return f'''🎉 ПОЗДРАВЛЯЕМ! РЕГИСТРАЦИЯ ЗАВЕРШЕНА! 🎉

Спасибо, {child_name}! Вы выбрали программу:
⭐ {program_name}

📞 Наш отдел заботы свяжется с вами в течение 24 часов!

☎️ Если не хотите ждать, звоните:
   📞 +7 (922) 014-44-94 - Наталья
   📞 +7 (904) 805-25-61 - Ксения
   📞 +7 (951) 239-86-49 - Жанна

✨ СПЕЦПРЕДЛОЖЕНИЕ:
   🎁 Первое занятие БЕСПЛАТНОЕ!
   📅 Гибкое расписание
   👥 Группы до 8 детей

Спасибо за доверие! До скорых встреч! 👋'''

# ═══════════════════════════════════════════════════════════════════════════
# ОСНОВНЫЕ ФУНКЦИИ ЛОГИКИ БОТА
# ═══════════════════════════════════════════════════════════════════════════

def save_registration(user_id: int, data: Dict) -> bool:
    """Сохраняет данные регистрации"""
    try:
        registration = {
            'user_id': user_id,
            'child_name': data.get('child_name', ''),
            'child_age': data.get('child_age', ''),
            'kindergarten': data.get('kindergarten', ''),
            'group_number': data.get('group_number', ''),
            'parent_name': data.get('parent_name', ''),
            'parent_phone': data.get('parent_phone', ''),
            'program': data.get('program', ''),
            'program_name': data.get('program_name', ''),
            'program_price': data.get('program_price', ''),
            'date': datetime.now().isoformat()
        }
        
        # Сохранение в JSON файл
        filename = f'/tmp/registration_{user_id}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(registration, f, ensure_ascii=False, indent=2)
        
        logger.info(f'✅ Регистрация сохранена для пользователя {user_id}')
        return True
    except Exception as e:
        logger.error(f'❌ Ошибка сохранения регистрации: {str(e)}')
        return False

def send_message(user_id: int, text: str) -> bool:
    """Отправляет сообщение пользователю через VK API"""
    if not VK_TOKEN:
        logger.error('❌ VK_TOKEN не установлен!')
        return False
    
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'access_token': VK_TOKEN,
        'user_id': user_id,
        'message': text,
        'v': '5.199',
        'random_id': 0
    }
    
    try:
        response = requests.post(url, data=params, timeout=10)
        response_data = response.json()
        
        if 'error' in response_data:
            logger.error(f'❌ Ошибка VK API: {response_data["error"]}')
            return False
        
        logger.info(f'✅ Сообщение отправлено пользователю {user_id}')
        return True
    except Exception as e:
        logger.error(f'❌ Ошибка отправки сообщения: {str(e)}')
        return False

def send_admin_notification(user_id: int, phone: str, data: Dict) -> bool:
    """Отправляет уведомление администратору о новом клиенте"""
    if not VK_TOKEN:
        logger.error('❌ VK_TOKEN не установлен!')
        return False
    
    child_name = data.get('child_name', 'Не указано')
    child_age = data.get('child_age', 'Не указано')
    kindergarten = data.get('kindergarten', 'Не посещает')
    kindergarten_address = data.get('kindergarten_address', '')
    group = data.get('group_number', 'Не указано')
    program_name = data.get('program_name', 'Не выбрана')
    parent_name = data.get('parent_name', 'Не указано')
    
    # Форматируем информацию о саде
    kg_info = f"{kindergarten}"
    if kindergarten_address:
        kg_info += f", {kindergarten_address}"
    
    text = f'''🔔 НОВЫЙ КЛИЕНТ 🔔

👤 Пользователь VK: {user_id}

📞 НОМЕР ТЕЛЕФОНА: {phone}

👶 ФИО ребенка: {child_name}
📅 Возраст ребенка: {child_age} лет
🏫 Детский сад: {kg_info}
👥 Группа: {group}
👨 ФИО родителя: {parent_name}
🎓 Интересует программу: {program_name}

⚠️ ДЕЙСТВИЕ ТРЕБУЕТСЯ:
→ Позвоните клиенту как можно скорее!
→ Предложите пробное занятие
→ Завершите регистрацию

Время: {datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'''
    
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'access_token': VK_TOKEN,
        'user_id': ADMIN_ID,
        'message': text,
        'v': '5.199',
        'random_id': 0
    }
    
    try:
        response = requests.post(url, data=params, timeout=10)
        response_data = response.json()
        
        if 'error' in response_data:
            logger.error(f'❌ Ошибка отправки уведомления администратору: {response_data["error"]}')
            return False
        
        logger.info(f'✅ Уведомление отправлено администратору (номер: {phone})')
        return True
    except Exception as e:
        logger.error(f'❌ Ошибка отправки уведомления: {str(e)}')
        return False

def process_registration_step(user_id: int, step: int, message_text: str) -> Tuple[str, bool]:
    """
    УЛУЧШЕННАЯ версия обработки этапов регистрации
    С расширенным анализом и рекомендациями
    """
    msg = message_text.lower().strip()
    
    # Проверка на отмену
    if msg == 'отмена':
        user_registration_data[user_id]['step'] = 0
        return '❌ Регистрация отменена. Введите "запись" чтобы начать заново.', True
    
    if step == 1:  # ФИО ребенка
        is_valid, result = validate_child_fio_step1(message_text)
        if not is_valid:
            # result уже содержит полное сообщение об ошибке с примерами
            return result, False
        
        # Сохраняем нормализованное ФИО
        user_registration_data[user_id]['child_name'] = result
        user_registration_data[user_id]['step'] = 2
        
        # Подтверждение сохранения
        confirm_msg = f'''✅ Спасибо! ФИО ребенка сохранено: {result}

Продолжим...

{get_registration_step_2()}'''
        return confirm_msg, True
    
    elif step == 2:  # Возраст - УЛУЧШЕНО
        is_valid, result = validate_age(message_text)
        if not is_valid:
            return result, False
        
        age = int(result)
        user_registration_data[user_id]['child_age'] = result
        user_registration_data[user_id]['step'] = 3
        
        # НОВОЕ: Используем умную версию следующего шага с рекомендациями
        child_name = user_registration_data[user_id].get('child_name', '')
        return get_registration_step_2_with_recommendations(age, child_name), True
    
    elif step == 3:  # Детский сад - УЛУЧШЕНО
        msg = message_text.lower().strip()
        
        # Если пользователь написал "нет"
        if msg == 'нет' or msg == 'нет сада' or msg == 'не посещает':
            user_registration_data[user_id]['kindergarten'] = 'Не посещает'
            user_registration_data[user_id]['kindergarten_id'] = 'none'
            user_registration_data[user_id]['step'] = 4
            return get_registration_step_4(), True
        
        # Если пользователь запросил список
        if msg == 'список' or msg == 'все сады' or msg == 'какие сады':
            return get_available_kindergartens_list() + '\n\n→ Напишите номер сада, территорию или "нет":', False
        
        found_kgs = []
        
        # Сначала пытаемся найти по номеру
        try:
            kg_id_float = float(message_text) if '.' in message_text else int(message_text)
            kg = get_kindergarten_info(kg_id_float)
            if kg:
                found_kgs = [(kg_id_float, kg)]
        except:
            pass
        
        # Если не найдено по номеру, ищем по территории
        if not found_kgs:
            found_kgs = find_kindergartens_by_territory(msg)
        
        # Если не найдено, пытаемся найти по адресу
        if not found_kgs:
            for kg_id, kg_info in KINDERGARTENS.items():
                if msg in kg_info['address'].lower():
                    found_kgs.append((kg_id, kg_info))
        
        # Если ничего не найдено
        if not found_kgs:
            response = f'''❌ Сад не найден: "{message_text}"

Попробуйте одно из:
📌 Номер сада (30, 44, 475)
📌 Территорию (Центр, Север, Юг)
📌 Адрес (Зальцмана, Духова)
📌 "список" - показать все сады
📌 "нет" - не посещает ДОУ

→ Напишите еще раз:'''
            return response, False
        
        # Если найден один сад
        if len(found_kgs) == 1:
            kg_id, kg_info = found_kgs[0]
            user_registration_data[user_id]['kindergarten'] = kg_info['name']
            user_registration_data[user_id]['kindergarten_address'] = kg_info['address']
            user_registration_data[user_id]['kindergarten_id'] = str(kg_id)
            user_registration_data[user_id]['step'] = 4
            
            # Показываем найденный сад
            programs_emoji = ', '.join([PROGRAMS[p]['emoji'] for p in kg_info['programs'] if p in PROGRAMS])
            response = f'''✅ Отлично! Нашли ваш сад:

🏢 {kg_info['name']}
📍 {kg_info['address']}
🗺️ {kg_info['location']}
📚 Наши программы: {programs_emoji}

Продолжим...

{get_registration_step_4()}'''
            return response, True
        
        # Если найдено несколько садов
        if len(found_kgs) <= 5:
            response = f'''✅ Найдено {len(found_kgs)} садов в этой территории!

Выберите ваш:
'''
            for kg_id, kg_info in found_kgs:
                response += f'\n🏢 {kg_info["name"]} - {kg_info["address"]}\n   (Напишите номер {int(kg_id) if kg_id == int(kg_id) else kg_id})'
            
            response += '\n\n→ Напишите номер сада или территорию поточнее:'
            return response, False
        
        # Слишком много результатов
        response = f'''📍 Найдено {len(found_kgs)} садов! Уточните:
- Номер сада (30, 44, 475)
- Адрес
- Территорию поточнее

→ Напишите еще раз:'''
        return response, False
    
    elif step == 4:  # Номер или адрес детского сада
        msg = message_text.lower().strip()
        
        # Попытка найти сад по номеру
        try:
            kg_id_float = float(message_text) if '.' in message_text else int(message_text)
            kg = get_kindergarten_info(kg_id_float)
            if kg:
                user_registration_data[user_id]['kindergarten'] = kg['name']
                user_registration_data[user_id]['kindergarten_address'] = kg['address']
                user_registration_data[user_id]['kindergarten_id'] = str(kg_id_float)
                user_registration_data[user_id]['step'] = 5
                return get_registration_step_5(), True
        except:
            pass
        
        # Если не найдено по номеру, ищем по адресу
        found_kg = None
        for kg_id, kg_info in KINDERGARTENS.items():
            if msg in kg_info['address'].lower():
                found_kg = (kg_id, kg_info)
                break
        
        if found_kg:
            kg_id, kg_info = found_kg
            user_registration_data[user_id]['kindergarten'] = kg_info['name']
            user_registration_data[user_id]['kindergarten_address'] = kg_info['address']
            user_registration_data[user_id]['kindergarten_id'] = str(kg_id)
            user_registration_data[user_id]['step'] = 5
            return get_registration_step_5(), True
        
        # Если ничего не найдено
        return f'''❌ Сад не найден: "{message_text}"

Напишите:
📌 Номер (например: 30, 44, 475)
📌 Адрес (например: Зальцмана, Духова)

→ Попробуйте еще раз:''', False
    
    elif step == 5:  # ФИО родителя
        is_valid, result = validate_fio(message_text)
        if not is_valid:
            error_msg = f'''{result}

→ Попробуйте еще раз:'''
            return error_msg, False
        
        user_registration_data[user_id]['parent_name'] = message_text
        user_registration_data[user_id]['step'] = 6
        return get_registration_step_6(), True
    
    elif step == 6:  # Телефон
        is_valid, result = validate_phone(message_text)
        if not is_valid:
            return result, False
        
        user_registration_data[user_id]['parent_phone'] = result
        user_registration_data[user_id]['step'] = 7
        
        # НОВОЕ: Используем умную версию с рекомендациями
        age = int(user_registration_data[user_id].get('child_age', 0))
        return get_registration_step_7(age), True
    
    elif step == 7:  # Программа
        program = PROGRAMS.get(msg)
        if not program:
            return '''❌ Программа не найдена. Выберите из списка:

🤖 robo_34 | 🧱 brick | ⚙️ pro | 💃 dance | 🗣️ logoped | 📚 school_2 | ✏️ school_1

→ Напишите код программы:''', False
        
        user_registration_data[user_id]['program'] = msg
        user_registration_data[user_id]['program_name'] = program['name']
        user_registration_data[user_id]['program_price'] = program['price']
        user_registration_data[user_id]['step'] = 8
        
        return get_confirmation_message(user_registration_data[user_id]), True
    
    return '❌ Неизвестный шаг регистрации', False

def handle_user_message(user_id: int, message_text: str):
    """
    ПЕРЕРАБОТАННЫЙ обработчик сообщений с правильной маршрутизацией.
    
    КЛЮЧЕВОЙ ПРИНЦИП:
    Если пользователь находится в процессе регистрации (шаг > 0),
    его сообщения обрабатываются ТОЛЬКО обработчиком регистрации.
    Общий AI-обработчик вызывается ТОЛЬКО при отсутствии активного сценария.
    """
    if not message_text:
        return
    
    msg = message_text.lower().strip()
    
    # Инициализация пользователя
    if user_id not in user_registration_data:
        user_registration_data[user_id] = {'step': 0}
    
    current_step = user_registration_data[user_id].get('step', 0)
    
    logger.info(f'📨 Сообщение от {user_id} (шаг {current_step}): {msg[:50]}...')
    
    # ════════════════════════════════════════════════════════════════════════
    # ПРИОРИТЕТ 1: КОМАНДЫ УПРАВЛЕНИЯ (работают на ЛЮБОМ шаге регистрации)
    # ════════════════════════════════════════════════════════════════════════
    
    if current_step > 0:  # Если пользователь в процессе регистрации
        
        if msg in ['отмена', 'отмена!', 'выход']:
            user_registration_data[user_id]['step'] = 0
            send_message(user_id, '''❌ РЕГИСТРАЦИЯ ОТМЕНЕНА

Если хотите начать регистрацию заново, напишите "запись"
или выберите команду из справки - "помощь"''')
            return
        
        if msg in ['назад', 'назад!', '<<<']:
            new_step = current_step - 1
            if new_step < 1:
                new_step = 1
                send_message(user_id, '⚠️ Вы уже на первом вопросе!')
                return
            
            user_registration_data[user_id]['step'] = new_step
            
            # Вернуть на нужный шаг
            if new_step == 1:
                send_message(user_id, get_registration_step_1())
            elif new_step == 2:
                send_message(user_id, get_registration_step_2())
            elif new_step == 3:
                send_message(user_id, get_registration_step_3())
            elif new_step == 4:
                send_message(user_id, get_registration_step_4())
            elif new_step == 5:
                send_message(user_id, get_registration_step_5())
            elif new_step == 6:
                send_message(user_id, get_registration_step_6())
            elif new_step == 7:
                age = int(user_registration_data[user_id].get('child_age', 0))
                send_message(user_id, get_registration_step_7(age))
            
            return
        
        if msg in ['начать заново', 'начать с начала', 'заново', 'заново!']:
            user_registration_data[user_id] = {'step': 1}
            send_message(user_id, get_registration_step_1())
            return
    
    # ════════════════════════════════════════════════════════════════════════
    # ПРИОРИТЕТ 2: ОБРАБОТКА АКТИВНОГО СЦЕНАРИЯ РЕГИСТРАЦИИ
    # ════════════════════════════════════════════════════════════════════════
    
    if current_step >= 1 and current_step <= 8:
        response, success = process_registration_step(user_id, current_step, message_text)
        send_message(user_id, response)
        return
    
    # ════════════════════════════════════════════════════════════════════════
    # ПРИОРИТЕТ 3: ОБЩИЕ КОМАНДЫ (только если НЕ в регистрации)
    # ════════════════════════════════════════════════════════════════════════
    
    if 'запись' in msg or 'регистрация' in msg or 'зарегистрировать' in msg:
        user_registration_data[user_id]['step'] = 1
        send_message(user_id, get_registration_step_1())
        return
    
    elif msg in ['привет', 'привет!', 'здравствуйте', 'здравствуйте!', 'здравствуй', 'добрый день', 'добрый вечер', 'доброе утро']:
        send_message(user_id, get_hello_response())
        return
    
    elif msg == 'помощь' or msg == 'помощь!' or msg == '?':
        send_message(user_id, get_help())
        return
    
    elif 'программ' in msg or msg == 'программы':
        send_message(user_id, get_all_programs())
        return
    
    elif msg in ['robo_34', 'brick', 'pro', 'pro_plus', 'dance', 'logoped', 'school_2', 'school_1']:
        details = get_program_details(msg)
        if details:
            send_message(user_id, details)
        else:
            send_message(user_id, '❌ Программа не найдена')
        return
    
    elif 'контакт' in msg or msg == 'контакты':
        send_message(user_id, get_contacts())
        return
    
    elif 'спасибо' in msg:
        send_message(user_id, '😊 Пожалуйста! Чем я еще могу помочь?')
        return
    
    # Проверка на номер телефона (если пользователь просто пишет номер)
    if re.search(r'\d{10,15}', message_text) and current_step == 0:
        is_valid, result = validate_phone(message_text)
        if is_valid:
            user_registration_data[user_id]['phone_only'] = result
            
            response_text = f'''✅ Спасибо! Номер телефона {result} получен!

📞 Наш отдел заботы с вами свяжется в течение часа!

🎓 Если у вас есть вопросы, напишите "программы" или "помощь"'''
            
            send_message(user_id, response_text)
            
            admin_data = {
                'parent_name': 'Не указано',
                'program_name': 'Интересуется общей информацией',
                'child_name': 'Не указано',
                'child_age': 'Не указано'
            }
            send_admin_notification(user_id, result, admin_data)
            return
    
    # Если ничего не подошло
    send_message(user_id, f'''❓ Я не совсем понимаю: "{message_text}"

Напишите:
📋 "помощь" - справка по командам
📚 "программы" - все наши курсы  
✍️ "запись" - регистрация ребенка
📞 "контакты" - как с нами связаться

Или напишите свой вопрос - постараюсь помочь! 💬''')
    return

# ═══════════════════════════════════════════════════════════════════════════
# FLASK ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/callback', methods=['POST'])
def callback():
    """Обработчик webhook'a от VK"""
    data = request.get_json()
    
    if not data:
        return 'ok', 200
    
    event_type = data.get('type')
    
    # Подтверждение webhook'a
    if event_type == 'confirmation':
        logger.info('✅ Событие подтверждения получено')
        return VK_CONFIRMATION_TOKEN, 200
    
    # Подписка нового пользователя
    if event_type == 'user_subscribed':
        obj = data.get('object', {})
        user_id = obj.get('user_id')
        
        if user_id:
            logger.info(f'👤 Новый пользователь подписался: {user_id}')
            send_message(user_id, get_main_menu())
        
        return 'ok', 200
    
    # Новое сообщение
    if event_type == 'message_new':
        obj = data.get('object', {})
        message_obj = obj.get('message', {})
        user_id = message_obj.get('from_id')
        message_text = message_obj.get('text', '')
        
        if user_id and message_text:
            logger.info(f'💬 Новое сообщение от {user_id}: {message_text[:50]}')
            handle_user_message(user_id, message_text)
        
        return 'ok', 200
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    """Проверка здоровья сервера"""
    return {'status': 'ok', 'version': '3.0', 'features': ['smart_age_detection', 'program_recommendations', 'context_analysis']}, 200

@app.route('/health', methods=['GET'])
def health():
    """Эндпоинт здоровья"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}, 200

@app.route('/stats', methods=['GET'])
def stats():
    """Статистика бота"""
    return {
        'status': 'ok',
        'active_users': len(user_registration_data),
        'timestamp': datetime.now().isoformat(),
        'bot_version': '3.0',
        'features_enabled': ['smart_age_detection', 'program_recommendations', 'context_aware_responses']
    }, 200

# ═══════════════════════════════════════════════════════════════════════════
# ЗАПУСК ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info('🚀 Запуск бота РобоСТЕАМ v3.0 (Улучшенная версия)')
    logger.info(f'📊 Версия Python: 3.6+')
    logger.info(f'🔑 VK_TOKEN установлен: {"Да" if VK_TOKEN else "Нет"}')
    logger.info(f'🔒 VK_SECRET установлен: {"Да" if VK_SECRET else "Нет"}')
    logger.info(f'✨ Новые возможности: умное определение возраста, рекомендации программ, расширенное мышление')
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f'❌ Ошибка запуска: {str(e)}')
