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

def get_hello_response():
    text = 'Добрый день! Рады вас видеть!\n\n'
    text += 'Мы предлагаем 7 образовательных программ для детей от 3 до 8 лет:\n'
    text += '- Робототехника РобоСТЕАМ (3-4 года) - 300 руб\n'
    text += '- Робототехника РобоСТЕАМ Брик (5-6 лет) - 300 руб\n'
    text += '- Робототехника РобоСТЕАМ Про (6-8 лет) - 400 руб\n'
    text += '- Хореография (3-8 лет) - 350 руб\n'
    text += '- Логопед и развитие речи (3-7 лет) - 600 руб\n'
    text += '- Дошколёнок за два года до Школы (4-5 лет) - 350 руб\n'
    text += '- Дошколёнок За год до Школы (6-7 лет) - 375 руб\n\n'
    text += 'Напишите "запись" чтобы записать ребенка или "программы" для подробностей'
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
    text += '🔹 ВОПРОС 1 из 7\n\n'
    text += 'Полное имя ребенка (ФИО)\n\n'
    text += 'Напишите полное имя ребенка'
    return text

def ask_child_age():
    text = 'Спасибо! Продолжаем:\n\n'
    text += '🔹 ВОПРОС 2 из 7\n\n'
    text += 'Сколько лет вашему ребенку?\n\n'
    text += 'Укажите возраст (например: 5 или 6)'
    return text

def ask_kindergarten():
    text = 'Хорошо! Далее:\n\n'
    text += '🔹 ВОПРОС 3 из 7\n\n'
    text += 'Название детского сада (если посещает)\n\n'
    text += 'Напишите название или "нет" если не посещает'
    return text

def ask_group_number():
    text = 'Продолжаем:\n\n'
    text += '🔹 ВОПРОС 4 из 7\n\n'
    text += 'Номер группы в детском саду\n\n'
    text += 'Напишите номер группы или "нет" если не посещает'
    return text

def ask_parent_name():
    text = 'Отлично! Еще вопросы:\n\n'
    text += '🔹 ВОПРОС 5 из 7\n\n'
    text += 'Полное имя родителя (ФИО)\n\n'
    text += 'Напишите ваше полное имя'
    return text

def ask_parent_phone():
    text = 'Спасибо! Осталось:\n\n'
    text += '🔹 ВОПРОС 6 из 7\n\n'
    text += 'Номер телефона для связи\n\n'
    text += 'Напишите ваш номер телефона (например: +7 (921) 123-45-67)'
    return text

def ask_program_choice():
    text = 'Замечательно! Последний вопрос:\n\n'
    text += '🔹 ВОПРОС 7 из 7\n\n'
    text += 'Какая программа вас интересует?\n\n'
    text += 'Напишите один из кодов:\n'
    text += 'robo_34 - Робототехника 3-4 года (300 руб)\n'
    text += 'brick - РобоСТЕАМ Брик 5-6 лет (300 руб)\n'
    text += 'pro - РобоСТЕАМ Про 6-8 лет (400 руб)\n'
    text += 'dance - Хореография (350 руб)\n'
    text += 'logoped - Логопед и развитие речи (600 руб)\n'
    text += 'school_2 - Дошколёнок 4-5 лет (350 руб)\n'
    text += 'school_1 - Дошколёнок 6-7 лет (375 руб)'
    return text

def confirm_registration(user_id, data):
    text = '✅ РЕГИСТРАЦИЯ ЗАВЕРШЕНА!\n\n'
    text += 'Сведения о ребенке:\n'
    text += '📌 ФИО: ' + data.get('child_name', 'Не указано') + '\n'
    text += '📌 Возраст: ' + data.get('child_age', 'Не указано') + ' лет\n'
    text += '📌 Детский сад: ' + data.get('kindergarten', 'Не указано') + '\n'
    text += '📌 Группа: ' + data.get('group_number', 'Не указано') + '\n\n'
    text += 'Сведения о родителе:\n'
    text += '👤 ФИО: ' + data.get('parent_name', 'Не указано') + '\n'
    text += '📞 Телефон: ' + data.get('parent_phone', 'Не указано') + '\n\n'
    text += 'Выбранная программа:\n'
    text += '🎓 ' + data.get('program_name', 'Не выбрана') + '\n'
    text += '💰 ' + data.get('program_price', 'Не указана') + '\n\n'
    text += 'Мы свяжемся с вами в течение 24 часов!\n'
    text += 'Спасибо, что выбрали РобоСТЕАМ!'
    
    save_registration(user_id, data)
    return text

def save_registration(user_id, data):
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
        filename = '/tmp/registration_' + str(user_id) + '.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(registration, f, ensure_ascii=False, indent=2)
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
    
    print('DEBUG: user_id=' + str(user_id) + ', step=' + str(current_step) + ', msg=' + msg)
    
    if current_step == 1:
        user_registration_data[user_id]['child_name'] = message_text
        user_registration_data[user_id]['step'] = 2
        response = ask_child_age()
    
    elif current_step == 2:
        if message_text.isdigit():
            user_registration_data[user_id]['child_age'] = message_text
            user_registration_data[user_id]['step'] = 3
            response = ask_kindergarten()
        else:
            response = 'Пожалуйста, укажите возраст цифрой (например: 5)'
    
    elif current_step == 3:
        user_registration_data[user_id]['kindergarten'] = message_text
        user_registration_data[user_id]['step'] = 4
        response = ask_group_number()
    
    elif current_step == 4:
        user_registration_data[user_id]['group_number'] = message_text
        user_registration_data[user_id]['step'] = 5
        response = ask_parent_name()
    
    elif current_step == 5:
        user_registration_data[user_id]['parent_name'] = message_text
        user_registration_data[user_id]['step'] = 6
        response = ask_parent_phone()
    
    elif current_step == 6:
        user_registration_data[user_id]['parent_phone'] = message_text
        user_registration_data[user_id]['step'] = 7
        response = ask_program_choice()
    
    elif current_step == 7:
        prog_key = msg
        if prog_key in PROGRAMS:
            user_registration_data[user_id]['program'] = prog_key
            user_registration_data[user_id]['program_name'] = PROGRAMS[prog_key]['name']
            user_registration_data[user_id]['program_price'] = PROGRAMS[prog_key]['price']
            response = confirm_registration(user_id, user_registration_data[user_id])
            user_registration_data[user_id]['step'] = 0
        else:
            response = 'Такой программы нет. Напишите правильный код:\nrobo_34, brick, pro, dance, logoped, school_2, school_1'
    
    elif 'запис' in msg:
        user_registration_data[user_id] = {'step': 1}
        response = get_registration_form()
    
    elif 'добрый день' in msg or 'добрый вечер' in msg or 'доброе утро' in msg or 'здравствуйте' in msg or msg == 'привет' or msg == 'здравствуй' or msg == 'привет!' or msg == 'здравствуйте!':
        response = get_hello_response()
    
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
        response += '- "контакты" для информации о записи\n'
        response += '- или просто поздоровайтесь (добрый день, привет и т.д.)\n\n'
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
