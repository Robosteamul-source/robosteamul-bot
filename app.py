from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

PROGRAMS = {
    'beginner': {
        'name': 'Робоника для начинающих',
        'age': '6-8 лет',
        'description': 'Введение в основы робототехники. Сборка простых конструкций и первые программы на Scratch.',
        'duration': '8 недель',
        'price': '4000 руб/месяц'
    },
    'junior': {
        'name': 'Junior Robotics',
        'age': '9-11 лет',
        'description': 'Программирование роботов LEGO Mindstorms. Решение задач и участие в соревнованиях.',
        'duration': '12 недель',
        'price': '5000 руб/месяц'
    },
    'advanced': {
        'name': 'Advanced Robotics',
        'age': '12-15 лет',
        'description': 'Python программирование. Работа с Arduino и микроконтроллерами. Создание собственных проектов.',
        'duration': '16 недель',
        'price': '6000 руб/месяц'
    },
    'professional': {
        'name': 'Pro Developer Track',
        'age': '16+ лет',
        'description': 'Продвинутая робототехника, машинное обучение, IoT проекты. Подготовка к экзаменам.',
        'duration': '24 недели',
        'price': '7500 руб/месяц'
    }
}

def get_programs_info():
    text = '📚 Программы обучения RoboSTEAMuL:\n\n'
    
    for key, program in PROGRAMS.items():
        text += f"🤖 {program['name']}\n"
        text += f"👶 Возраст: {program['age']}\n"
        text += f"📝 {program['description']}\n"
        text += f"⏱ Длительность: {program['duration']}\n"
        text += f"💰 Стоимость: {program['price']}\n\n"
    
    text += "Напишите название программы для подробной информации (например: beginner, junior, advanced, professional)\n"
    text += "Или напишите 'контакты' для получения информации о записи."
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    text = f"📌 {program['name']}\n\n"
    text += f"👶 Возраст: {program['age']}\n"
    text += f"📝 Описание: {program['description']}\n"
    text += f"⏱ Длительность курса: {program['duration']}\n"
    text += f"💰 Стоимость: {program['price']}\n\n"
    text += "Для записи свяжитесь с нами через форму обратной связи в сообществе или напишите 'контакты'"
    
    return text

def get_contacts():
    text = "📞 Как с нами связаться:\n\n"
    text += "📧 Email: info@robosteamul.ru\n"
    text += "📱 Телефон: +7 (XXX) XXX-XX-XX\n"
    text += "🌐 Сайт: www.robosteamul.ru\n"
    text += "📍 Адрес: г. Москва\n\n"
    text += "Оставьте заявку в сообществе - наш менеджер свяжется с вами в течение 24 часов!"
    
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
        print(f'Message sent to {user_id}')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False

def handle_user_message(user_id, message_text):
    msg_lower = message_text.lower().strip()
    
    if any(word in msg_lower for word in ['программ', 'обучени', 'курс', 'помощь', 'привет', 'hi', 'hello', 'список']):
        response = get_programs_info()
    
    elif msg_lower in ['beginner', 'junior', 'advanced', 'professional']:
        response = get_program_details(msg_lower)
    
    elif any(word in msg_lower for word in ['контакт', 'связь', 'телефон', 'адрес', 'email', 'запис']):
        response = get_contacts()
    
    else:
        response = "👋 Спасибо за вопрос!\n\n"
        response += "Напишите:\n"
        response += "- 'программы' для списка всех курсов\n"
        response += "- 'beginner', 'junior', 'advanced' или 'professional' для деталей курса\n"
        response += "- 'контакты' для информации о записи\n\n"
        response +=
robosteamul.ru. Доменное имя продаётся
robosteamul.ru. Доменное имя продаётся
robosteamul.ru


ли задайте свой вопрос - мы постараемся помочь! 😊"
    
    send_message(user_id, response)

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    
    if not data:
        return 'ok', 200
    
    event_type = data.get('type')
    
    if event_type == 'confirmation':
        print('Confirmation event received')
        return VK_CONFIRMATION_TOKEN
    
    if event_type == 'user_subscribed':
        obj = data.get('object', {})
        user_id = obj.get('user_id')
        
        if user_id:
            greeting = 'Добро пожаловать в RoboSTEAMuL! 🤖\n\nМы научим ваших детей робототехнике и программированию.\n\nНапишите "программы" чтобы узнать о наших курсах, или "контакты" для записи.'
            send_message(user_id, greeting)
        
        return 'ok', 200
    
    if event_type == 'message_new':
        obj = data.get('object', {})
        message_obj = obj.get('message', {})
        user_id = message_obj.get('from_id')
        message_text = message_obj.get('text', '')
        
        if user_id and message_text:
            print(f'Message from {user_id}: {message_text}')
            handle_user_message(user_id, message_text)
        
        return 'ok', 200
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)"И
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run


