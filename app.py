# -*- coding: utf-8 -*-
from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

PROGRAMS = {
    'robo_34': {
        'name': 'Робототехника РобоСТЕАМ',
        'age': '3-4 года',
        'description': 'Первые шаги в мир робототехники. Развитие логического мышления и мелкой моторики.',
        'price': '300 руб за занятие',
        'short': 'robo_34'
    },
    'brick': {
        'name': 'Робототехника РобоСТЕАМ Брик',
        'age': '5-6 лет',
        'description': 'Построение и программирование роботов. Основы конструирования и алгоритмики.',
        'price': '300 руб за занятие',
        'short': 'brick'
    },
    'pro': {
        'name': 'Робототехника РобоСТЕАМ Про',
        'age': '6-8 лет',
        'description': 'Продвинутое программирование и создание сложных роботов. Участие в соревнованиях.',
        'price': '400 руб за занятие',
        'short': 'pro'
    },
    'dance': {
        'name': 'Хореография',
        'age': '3-8 лет',
        'description': 'Развитие танца, ритма и координации. Творческие номера и выступления.',
        'price': '350 руб за занятие',
        'short': 'dance'
    },
    'logoped': {
        'name': 'Логопед и развитие речи',
        'age': '3-7 лет',
        'description': 'Коррекция звукопроизношения и развитие речи. Индивидуальные занятия.',
        'price': '600 руб за занятие (диагностика +800 руб)',
        'short': 'logoped'
    },
    'school_2': {
        'name': 'Дошколёнок за два года до Школы',
        'age': '4-5 лет',
        'description': 'Комплексная подготовка к школе. Грамота, арифметика, познавательно-речевое развитие.',
        'price': '350 руб за занятие',
        'short': 'school_2'
    },
    'school_1': {
        'name': 'Дошколёнок За год до Школы',
        'age': '6-7 лет',
        'description': 'Интенсивная подготовка в выпускной год. Освоение школьных навыков и самодисциплины.',
        'price': '375 руб за занятие',
        'short': 'school_1'
    }
}

def get_all_programs():
    text = 'Все программы РобоСТЕАМ:\n\n'
    
    text += '1. ' + PROGRAMS['robo_34']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['robo_34']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['robo_34']['price'] + '\n\n'
    
    text += '2. ' + PROGRAMS['brick']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['brick']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['brick']['price'] + '\n\n'
    
    text += '3. ' + PROGRAMS['pro']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['pro']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['pro']['price'] + '\n\n'
    
    text += '4. ' + PROGRAMS['dance']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['dance']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['dance']['price'] + '\n\n'
    
    text += '5. ' + PROGRAMS['logoped']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['logoped']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['logoped']['price'] + '\n\n'
    
    text += '6. ' + PROGRAMS['school_2']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['school_2']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['school_2']['price'] + '\n\n'
    
    text += '7. ' + PROGRAMS['school_1']['name'] + '\n'
    text += '   Возраст: ' + PROGRAMS['school_1']['age'] + '\n'
    text += '   Цена: ' + PROGRAMS['school_1']['price'] + '\n\n'
    
    text += 'Напишите название программы для подробной информации.\n'
    text += 'Например: robo_34, brick, pro, dance, logoped, school_2, school_1\n'
    text += "Или напишите 'контакты' для записи"
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    text = program['name'] + '\n\n'
    text += 'Возраст: ' + program['age'] + '\n'
    text += 'Цена: ' + program['price'] + '\n\n'
    text += 'Описание:\n' + program['description'] + '\n\n'
    text += "Для записи напишите 'контакты' или позвоните нам"
    
    return text

def get_programs_by_age(age_text):
    age_lower = age_text.lower().strip()
    matching = []
    
    for key, program in PROGRAMS.items():
        if age_lower in program['age'].lower():
            matching.append(program['name'] + ' (' + program['age'] + ') - ' + program['price'])
    
    if not matching:
        return 'Программ для этого возраста не найдено. Напишите "программы" для полного списка.'
    
    text = 'Программы для возраста ' + age_text + ':\n\n'
    for prog in matching:
        text += '- ' + prog + '\n'
    
    text += '\nНапишите название программы для деталей'
    return text

def get_contacts():
    text = 'Контакты РобоСТЕАМ:\n\n'
    text += 'Email: info@robosteam.ru\n'
    text += 'Телефон: +7 (XXX) XXX-XX-XX\n'
    text += 'Адрес: Москва\n'
    text += 'Сайт: www.robosteam.ru\n\n'
    text += 'Для записи в группах:\n'
    text += '- Пишите нам в мессенджер\n'
    text += '- Звоните по телефону\n'
    text += '- Приходите к нам в офис\n\n'
    text += 'Доступна бесплатная первая консультация!'
    
    return text

def send_message(user_id, text):
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'access_token': VK_TOKEN,
        'user_id': user_id,
        'message': text,
        'v': '5.199',
        'random_id': 0
    }
    try:
        response = requests.post(url, data=params)
        print('Сообщение отправлено пользователю ' + str(user_id))
        return True
    except Exception as e:
        print('Ошибка: ' + str(e))
        return False

def handle_user_message(user_id, message_text):
    msg = message_text.lower().strip()
    
    if 'программ' in msg or 'курс' in msg or 'что' in msg or 'какие' in msg:
        response = get_all_programs()
    
    elif msg in ['robo_34', 'brick', 'pro', 'dance', 'logoped', 'school_2', 'school_1']:
        response = get_program_details(msg)
    
    elif 'контакт' in msg or 'запис' in msg or 'звон' in msg or 'адрес' in msg or 'email' in msg:
        response = get_contacts()
    
    elif 'возраст' in msg or 'лет' in msg or 'года' in msg or 'годиков' in msg:
        words = msg.split()
        for word in words:
            if word.isdigit():
                age = word
                response = get_programs_by_age(age)
                send_message(user_id, response)
                return
        response = 'Укажите возраст (например: 5, 6, 7)'
    
    else:
        response = 'Спасибо за вопрос!\n\n'
        response += 'Напишите:\n'
        response += '- "программы" для списка всех курсов\n'
        response += '- "robo_34", "brick", "pro", "dance", "logoped", "school_2", "school_1" для деталей\n'
        response += '- возраст (например: 5 лет) для программ по возрасту\n'
        response += '- "контакты" для информации о записи\n\n'
        response += 'Или задайте любой вопрос - мы постараемся помочь!'
    
    send_message(user_id, response)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    
    if not data:
        return 'ok', 200
    
    event_type = data.get('type')
    
    if event_type == 'confirmation':
        print('Событие подтверждения получено')
        return VK_CONFIRMATION_TOKEN
    
    if event_type == 'user_subscribed':
        obj = data.get('object', {})
        user_id = obj.get('user_id')
        
        if user_id:
            greeting = 'Добро пожаловать в РобоСТЕАМ!\n\n'
            greeting += 'Мы предлагаем 7 образовательных программ для детей от 3 до 8 лет:\n'
            greeting += '- Робототехника\n'
            greeting += '- Хореография\n'
            greeting += '- Развитие речи\n'
            greeting += '- Подготовка к школе\n\n'
            greeting += 'Напишите "программы" для полного списка,\n'
            greeting += 'или "контакты" для записи.'
            send_message(user_id, greeting)
        
        return 'ok', 200
    
    if event_type == 'message_new':
        obj = data.get('object', {})
        message_obj = obj.get('message', {})
        user_id = message_obj.get('from_id')
        message_text = message_obj.get('text', '')
        
        if user_id and message_text:
            print('Сообщение от ' + str(user_id) + ': ' + message_text)
            handle_user_message(user_id, message_text)
        
        return 'ok', 200
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return {'status': 'ok'}, 200

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
