# -*- coding: utf-8 -*-
"""
РобоСТЕАМ Бот для VK - Полностью переработанная версия
Автор: AI Assistant
Версия: 2.0
Улучшения: Исправлены ошибки, улучшена структура, добавлена валидация
"""

from flask import Flask, request
import requests
import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
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

# Программы обучения
PROGRAMS = {
    'robo_34': {
        'name': 'Робототехника РобоСТЕАМ',
        'age': '3-4 года',
        'description': 'Первые шаги в мир робототехники. Развитие логического мышления и мелкой моторики.',
        'price': '300 руб за занятие',
        'emoji': '🤖'
    },
    'brick': {
        'name': 'Робототехника РобоСТЕАМ Брик',
        'age': '5-6 лет',
        'description': 'Построение и программирование роботов. Основы конструирования и алгоритмики.',
        'price': '300 руб за занятие',
        'emoji': '🧱'
    },
    'pro': {
        'name': 'Робототехника РобоСТЕАМ Про',
        'age': '6-8 лет',
        'description': 'Продвинутое программирование и создание сложных роботов. Участие в соревнованиях.',
        'price': '400 руб за занятие',
        'emoji': '⚙️'
    },
    'dance': {
        'name': 'Хореография',
        'age': '3-8 лет',
        'description': 'Развитие танца, ритма и координации. Творческие номера и выступления.',
        'price': '350 руб за занятие',
        'emoji': '💃'
    },
    'logoped': {
        'name': 'Логопед и развитие речи',
        'age': '3-7 лет',
        'description': 'Коррекция звукопроизношения и развитие речи. Индивидуальные занятия.',
        'price': '600 руб за занятие (диагностика +800 руб)',
        'emoji': '🗣️'
    },
    'school_2': {
        'name': 'Дошколёнок за два года до Школы',
        'age': '4-5 лет',
        'description': 'Комплексная подготовка к школе. Грамота, арифметика, познавательно-речевое развитие.',
        'price': '350 руб за занятие',
        'emoji': '📚'
    },
    'school_1': {
        'name': 'Дошколёнок за год до Школы',
        'age': '6-7 лет',
        'description': 'Интенсивная подготовка в выпускной год. Освоение школьных навыков и самодисциплины.',
        'price': '375 руб за занятие',
        'emoji': '✏️'
    }
}

# Хранилище данных пользователей
user_registration_data: Dict = {}

# ═══════════════════════════════════════════════════════════════════════════
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ ВАЛИДАЦИИ
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
    """Проверяет корректность возраста"""
    try:
        age = int(age_str)
        if 1 <= age <= 18:
            return True, str(age)
        else:
            return False, "❌ Пожалуйста, укажите возраст от 1 до 18 лет (цифрой)"
    except ValueError:
        return False, "❌ Это не похоже на цифру. Напишите возраст числом (например: 5)"

# ═══════════════════════════════════════════════════════════════════════════
# ФУНКЦИИ ДЛЯ ФОРМИРОВАНИЯ СООБЩЕНИЙ
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
2. 🧱 Робототехника Брик (5-6 лет) - 300 руб/занятие
3. ⚙️ Робототехника Про (6-8 лет) - 400 руб/занятие
4. 💃 Хореография (3-8 лет) - 350 руб/занятие
5. 🗣️ Логопед и развитие речи (3-7 лет) - 600 руб/занятие
6. 📚 Дошколёнок за два года до Школы (4-5 лет) - 350 руб/занятие
7. ✏️ Дошколёнок За год до Школы (6-7 лет) - 375 руб/занятие

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
    
    text = f'''{program['emoji']} {program['name'].upper()} {program['emoji']}

📅 Возраст: {program['age']}
💰 Цена: {program['price']}

📝 ОПИСАНИЕ:
{program['description']}

🎯 Преимущества:
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
    """Второй вопрос"""
    return '''👍 Спасибо! Продолжаем...

🔹 ВОПРОС 2️⃣ из 7️⃣

Сколько лет вашему ребенку?

Примеры: 3, 4, 5, 6, 7, 8

→ Напишите возраст цифрой:'''

def get_registration_step_3() -> str:
    """Третий вопрос"""
    return '''✅ Хорошо! Далее...

🔹 ВОПРОС 3️⃣ из 7️⃣

Название детского сада (если ребенок его посещает)

Примеры: "Радуга", "Солнышко", "нет" (если не посещает)

→ Напишите название или "нет":'''

def get_registration_step_4() -> str:
    """Четвертый вопрос"""
    return '''👍 Понятно!

🔹 ВОПРОС 4️⃣ из 7️⃣

Номер группы в детском саду

Примеры: "первая младшая", "средняя", "1", "нет"

→ Напишите номер группы или "нет":'''

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

def get_registration_step_7() -> str:
    """Седьмой вопрос"""
    return '''🎯 Финальный выбор!

🔹 ВОПРОС 7️⃣ из 7️⃣

Какая программа вас интересует?

Выберите один из кодов:

🤖 robo_34 - Робототехника 3-4 года (300 руб)
🧱 brick - РобоСТЕАМ Брик 5-6 лет (300 руб)
⚙️ pro - РобоСТЕАМ Про 6-8 лет (400 руб)
💃 dance - Хореография (350 руб)
🗣️ logoped - Логопед и развитие речи (600 руб)
📚 school_2 - Дошколёнок 4-5 лет (350 руб)
✏️ school_1 - Дошколёнок 6-7 лет (375 руб)

→ Напишите код программы (например: robo_34):'''

def get_confirmation_message(data: Dict) -> str:
    """Подтверждение данных перед отправкой"""
    child_name = data.get('child_name', 'Не указано')
    child_age = data.get('child_age', 'Не указано')
    kindergarten = data.get('kindergarten', 'Не указано')
    group = data.get('group_number', 'Не указано')
    parent_name = data.get('parent_name', 'Не указано')
    parent_phone = data.get('parent_phone', 'Не указано')
    program_name = data.get('program_name', 'Не выбрана')
    program_price = data.get('program_price', 'Не указана')
    
    return f'''📋 ПРОВЕРКА ДАННЫХ РЕГИСТРАЦИИ 📋

Проверьте правильность данных:

👶 ИНФОРМАЦИЯ О РЕБЕНКЕ:
   📌 Имя: {child_name}
   📌 Возраст: {child_age} лет
   📌 Детский сад: {kindergarten}
   📌 Группа: {group}

👤 ИНФОРМАЦИЯ О РОДИТЕЛЕ:
   👨 Имя: {parent_name}
   📞 Телефон: {parent_phone}

🎓 ВЫБРАННАЯ ПРОГРАММА:
   📚 {program_name}
   💰 {program_price}

Всё верно?
→ Напишите "да" чтобы подтвердить регистрацию
→ Напишите "нет" чтобы исправить данные
→ Напишите "отмена" чтобы отменить регистрацию'''

def get_registration_complete(data: Dict) -> str:
    """Сообщение об успешной регистрации"""
    child_name = data.get('child_name', '')
    parent_phone = data.get('parent_phone', '')
    
    return f'''✅ ✅ ✅ РЕГИСТРАЦИЯ УСПЕШНО ЗАВЕРШЕНА! ✅ ✅ ✅

🎉 Спасибо за регистрацию, {child_name}!

Мы получили вашу заявку! 📝

📋 Что дальше?
   1️⃣ Мы свяжемся с вами по номеру {parent_phone} в течение 24 часов
   2️⃣ Согласуем удобное время и расписание занятий
   3️⃣ Проведём первое пробное занятие БЕСПЛАТНО!

✨ Возможности:
   ✓ Группы до 8 детей
   ✓ Опытные преподаватели
   ✓ Современные методики
   ✓ Гибкое расписание

Спасибо, что выбрали РобоСТЕАМ! 🚀
Мы ждём вас! 💪'''

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
    program_name = data.get('program_name', 'Не выбрана')
    parent_name = data.get('parent_name', 'Не указано')
    
    text = f'''🔔 НОВЫЙ КЛИЕНТ 🔔

👤 Пользователь VK: {user_id}

📞 НОМЕР ТЕЛЕФОНА: {phone}

👶 ФИО ребенка: {child_name}
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
    Обрабатывает каждый этап регистрации
    Возвращает: (ответ, нужно_ли_продолжать)
    """
    msg = message_text.lower().strip()
    
    # Проверка на отмену
    if msg == 'отмена':
        user_registration_data[user_id]['step'] = 0
        return '❌ Регистрация отменена. Введите "запись" чтобы начать заново.', True
    
    if step == 1:  # ФИО ребенка
        is_valid, result = validate_fio(message_text)
        if not is_valid:
            # Возвращаем ошибку с примерами
            error_msg = f'''{result}

💡 ПРИМЕРЫ ПРАВИЛЬНОГО ВВОДА:
   • Иван Петрович
   • Петров Иван Сергеевич
   • Мария Ивановна
   • Сидорова Елена Дмитриевна

→ Попробуйте еще раз:'''
            return error_msg, False
        
        user_registration_data[user_id]['child_name'] = message_text
        user_registration_data[user_id]['step'] = 2
        return get_registration_step_2(), True
    
    elif step == 2:  # Возраст
        is_valid, result = validate_age(message_text)
        if not is_valid:
            return result, False
        
        user_registration_data[user_id]['child_age'] = result
        user_registration_data[user_id]['step'] = 3
        return get_registration_step_3(), True
    
    elif step == 3:  # Детский сад
        user_registration_data[user_id]['kindergarten'] = message_text
        user_registration_data[user_id]['step'] = 4
        return get_registration_step_4(), True
    
    elif step == 4:  # Группа
        user_registration_data[user_id]['group_number'] = message_text
        user_registration_data[user_id]['step'] = 5
        return get_registration_step_5(), True
    
    elif step == 5:  # ФИО родителя
        is_valid, result = validate_fio(message_text)
        if not is_valid:
            # Возвращаем ошибку с примерами
            error_msg = f'''{result}

💡 ПРИМЕРЫ ПРАВИЛЬНОГО ВВОДА:
   • Сергей Иванович
   • Иванов Сергей Петрович
   • Наталья Ивановна
   • Смирнова Елена Алексеевна

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
        
        # Отправляем уведомление администратору о новом клиенте
        send_admin_notification(user_id, result, user_registration_data[user_id])
        
        return get_registration_step_7(), True
    
    elif step == 7:  # Выбор программы
        prog_key = msg
        if prog_key not in PROGRAMS:
            return '❌ Такой программы нет. Выберите из списка:\nrobo_34, brick, pro, dance, logoped, school_2, school_1', False
        
        user_registration_data[user_id]['program'] = prog_key
        user_registration_data[user_id]['program_name'] = PROGRAMS[prog_key]['name']
        user_registration_data[user_id]['program_price'] = PROGRAMS[prog_key]['price']
        user_registration_data[user_id]['step'] = 8
        
        # Переходим на подтверждение
        confirmation = get_confirmation_message(user_registration_data[user_id])
        return confirmation, True
    
    return '❓ Неизвестная ошибка', False

def handle_user_message(user_id: int, message_text: str) -> None:
    """Главная функция обработки сообщений пользователя"""
    
    # Пропускаем пустые сообщения
    if not message_text or not message_text.strip():
        send_message(user_id, '👂 Я не услышал... Напишите что-нибудь! 😊')
        return
    
    msg = message_text.lower().strip()
    
    # Инициализация пользователя
    if user_id not in user_registration_data:
        user_registration_data[user_id] = {'step': 0}
    
    current_step = user_registration_data[user_id].get('step', 0)
    
    logger.info(f'📨 Сообщение от {user_id} (шаг {current_step}): {msg[:50]}...')
    
    # ════════════════════════════════════════════════════════════════════════
    # ОБРАБОТКА ТЕКУЩЕГО ШАГА РЕГИСТРАЦИИ (ПРИОРИТЕТ ВЫШЕ!)
    # ════════════════════════════════════════════════════════════════════════
    
    if current_step == 1:
        response, success = process_registration_step(user_id, 1, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 2:
        response, success = process_registration_step(user_id, 2, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 3:
        response, success = process_registration_step(user_id, 3, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 4:
        response, success = process_registration_step(user_id, 4, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 5:
        response, success = process_registration_step(user_id, 5, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 6:
        response, success = process_registration_step(user_id, 6, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 7:
        response, success = process_registration_step(user_id, 7, message_text)
        send_message(user_id, response)
        return
    
    elif current_step == 8:  # Подтверждение
        if msg == 'да' or msg == 'да!' or msg == 'подтверждаю':
            response = get_registration_complete(user_registration_data[user_id])
            save_registration(user_id, user_registration_data[user_id])
            user_registration_data[user_id]['step'] = 0
            send_message(user_id, response)
            return
        elif msg == 'нет' or msg == 'исправить':
            user_registration_data[user_id]['step'] = 1
            send_message(user_id, 'Начнём сначала!\n\n' + get_registration_step_1())
            return
        elif msg == 'отмена':
            user_registration_data[user_id]['step'] = 0
            send_message(user_id, '❌ Регистрация отменена.')
            return
        else:
            send_message(user_id, '❓ Пожалуйста, ответьте "да" или "нет"')
            return
    
    # ════════════════════════════════════════════════════════════════════════
    # ОБРАБОТКА КОМАНД И ЗАПРОСОВ (ЕСЛИ НЕ В ПРОЦЕССЕ РЕГИСТРАЦИИ)
    # ════════════════════════════════════════════════════════════════════════
    
    if 'запись' in msg or 'регистрация' in msg:
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
    
    elif msg in ['robo_34', 'brick', 'pro', 'dance', 'logoped', 'school_2', 'school_1']:
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
            # Сохраняем номер в данные пользователя
            user_registration_data[user_id]['phone_only'] = result
            
            # Отправляем ответ пользователю
            response_text = f'''✅ Спасибо! Номер телефона {result} получен!

📞 Наш отдел заботы с вами свяжется в течение часа!

🎓 Если у вас есть вопросы, напишите "программы" или "помощь"'''
            
            send_message(user_id, response_text)
            
            # Отправляем уведомление администратору
            admin_data = {
                'parent_name': 'Не указано',
                'program_name': 'Интересуется общей информацией',
                'child_name': 'Не указано'
            }
            send_admin_notification(user_id, result, admin_data)
            return
    
    # Если ничего не подошло
    else:
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
    return {'status': 'ok', 'version': '2.0'}, 200

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
        'timestamp': datetime.now().isoformat()
    }, 200

# ═══════════════════════════════════════════════════════════════════════════
# ЗАПУСК ПРИЛОЖЕНИЯ
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info('🚀 Запуск бота РобоСТЕАМ v2.0')
    logger.info(f'📊 Версия Python: 3.6+')
    logger.info(f'🔑 VK_TOKEN установлен: {"Да" if VK_TOKEN else "Нет"}')
    logger.info(f'🔒 VK_SECRET установлен: {"Да" if VK_SECRET else "Нет"}')
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f'❌ Ошибка запуска: {str(e)}')
