# -*- coding: utf-8 -*-
from flask import Flask, request
import requests
import os
import json
from datetime import datetime

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

user_registration_data = {}

def get_greeting():
    text = 'Добро пожаловать в РобоСТЕАМ!\n\n'
    text += 'Мы предлагаем 7 образовательных программ для детей от 3 до 8 лет:\n'
    text += '- Робототехника\n'
    text += '- Хореография\n'
    text += '- Развитие речи\n'
    text += '- Подготовка к школе\n\n'
    text += 'Напишите "программы" для полного списка,\n'
    text += 'или давайте запишем вашего ребенка на занятия!'
    return text

def get_all_programs():
    text = 'все программы компании RoboSTEAMuL:\n\n'
    
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
    text += "Или напишите 'запись' чтобы записать ребенка"
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    text = program['name'] + '\n\n'
    text += 'Возраст: ' + program['age'] + '\n'
    text += 'Цена: ' + program['price'] + '\n\n'
    text += 'Описание:\n' + program['description'] + '\n\n'
    text += "Для записи ребенка напишите 'запись'"
    
    return text

def get_registration_form():
    text = 'Отлично! Давайте запишем вашего ребенка на занятия.\n\n'
    text += 'Пожалуйста, ответьте на следующие вопросы:\n\n'
    text += '1. Как зовут вашего ребенка?\n\n'
    text += 'Напишите имя ребенка'
    return text

def ask_child_age():
    text = 'Спасибо! Теперь скажите:\n\n'
    text += '2. Сколько лет вашему ребенку?\n\n'
    text += 'Укажите возраст (например: 5 или 6)'
    return text

def ask_program_choice():
    text = 'Отлично! Какая программа вас интересует?\n\n'
    text += 'Напишите один из кодов:\n'
    text += 'robo_34 - Робототехника 3-4 года\n'
    text += 'brick - РобоСТЕАМ Брик 5-6 лет\n'
    text += 'pro - РобоСТЕАМ Про 6-8 лет\n'
    text += 'dance - Хореография\n'
    text += 'logoped - Логопед и развитие речи\n'
    text += 'school_2 - Дошколёнок 4-5 лет\n'
    text += 'school_1 - Дошколёнок 6-7 лет'
    return text

def ask_parent_contact():
    text = 'Спасибо за выбор!\n\n'
    text += '3. Укажите ваше имя и номер телефона для связи\n\n'
    text += 'Например: Иван +7 (9XX) XXX-XX-XX'
    return text

def confirm_registration(user_id, data):
    text = 'Спасибо за регистрацию!\n\n'
    text += 'Данные вашего ребенка:\n'
    text += 'Имя: ' + data.get('child_name', 'Не указано') + '\n'
    text += 'Возраст: ' + data.get('child_age', 'Не указано') + ' лет\n'
    text += 'Программа: ' + data.get('program_name', 'Не выбрана') + '\n'
    text += 'Ваши контакты: ' + data.get('parent_contact', 'Не указаны') + '\n\n'
    text += 'Мы свяжемся с вами в течение 24 часов для подтверждения записи.\n\n'
    text += 'Спасибо, что выбрали РобоСТЕАМ!'
    
    save_registration(user_id, data)
    return text

def save_registration(user_id, data):
    try:
        registration = {
            'user_id': user_id,
            'child_name': data.get('child_name', ''),
            'child_age': data.get('child_age', ''),
            'program': data.get('program', ''),
            'program_name': data.get('program_name', ''),
            'parent_contact': data.get('parent_contact', ''),
            'date': datetime.now().isoformat()
        }
        filename = '/tmp/registration_' + str(user_id) + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(registration, f, ensure_ascii=False)
        print('Регистрация сохранена для пользователя ' + str(user_id))
    except Exception as e:
        print('Ошибка сохранения: ' + str(e))

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
    
    text += '\nНапишите код программы для деталей'
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
    
    if user_id not in user_registration_data:
        user_registration_data[user_id] = {'step': 0}
    
    user_data = user_registration_data[user_id]
    current_step = user_data.get('step', 0)
    
    if 'запис' in msg:
        user_registration_data[user_id] = {'step': 1}
        response = get_registration_form()
    
    elif current_step == 1:
        user_registration_data[user_id]['child_name'] = message_text
        user_registration_data[user_id]['step'] = 2
        response = ask_child_age()
    
    elif current_step == 2:
        if message_text.isdigit():
            user_registration_data[user_id]['child_age'] = message_text
            user_registration_data[user_id]['step'] = 3
            response = ask_program_choice()
        else:
            response = 'Пожалуйста, укажите возраст цифрой (например: 5)'
    
    elif current_step == 3:
        prog_key = msg
        if prog_key in PROGRAMS:
            user_registration_data[user_id]['program'] = prog_key
            user_registration_data[user_id]['program_name'] = PROGRAMS[prog_key]['name']
            user_registration_data[user_id]['step'] = 4
            response = ask_parent_contact()
        else:
            response = 'Такой программы нет. Напишите правильный код:\nrobo_34, brick, pro, dance, logoped, school_2, school_1'
    
    elif current_step == 4:
        user_registration_data[user_id]['parent_contact'] = message_text
        response = confirm_registration(user_id, user_registration_data[user_id])
        user_registration_data[user_id]['step'] = 0
    
    elif 'программ' in msg or 'курс' in msg or 'что' in msg or 'какие' in msg:
        response = get_all_programs()
    
    elif msg in ['robo_34', 'brick', 'pro', 'dance', 'logoped', 'school_2', 'school_1']:
        response = get_program_details(msg)
    
    elif 'контакт' in msg or 'звон' in msg or 'адрес' in msg or 'email' in msg:
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
        response += '- "запись" для записи ребенка на занятия\n'
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
            greeting = get_greeting()
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
