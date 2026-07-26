from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

PROGRAMS = {
    'beginner': {
        'name': 'Robotika dlya nachinayushchikh',
        'age': '6-8 let',
        'description': 'Vvedenie v osnovy robototekniki. Sborka prostykh konstruktsiy i pervye programmy na Scratch.',
        'duration': '8 nedel',
        'price': '4000 rub/mesyats'
    },
    'junior': {
        'name': 'Junior Robotics',
        'age': '9-11 let',
        'description': 'Programmirovanie robotov LEGO Mindstorms. Reshenie zadach i uchastie v sorevnovaniyakh.',
        'duration': '12 nedel',
        'price': '5000 rub/mesyats'
    },
    'advanced': {
        'name': 'Advanced Robotics',
        'age': '12-15 let',
        'description': 'Python programmirovanie. Rabota s Arduino i mikrokontrollerami. Sozdanie sobstvennykh proektov.',
        'duration': '16 nedel',
        'price': '6000 rub/mesyats'
    },
    'professional': {
        'name': 'Pro Developer Track',
        'age': '16+ let',
        'description': 'Prodvinutaya robototeknika, mashinnoe obuchenie, IoT proekty. Podgotovka k ekzamenam.',
        'duration': '24 nedeli',
        'price': '7500 rub/mesyats'
    }
}

def get_programs_info():
    text = 'Programmy obucheniya RoboSTEAMuL:\n\n'
    
    for key, program in PROGRAMS.items():
        text += program['name'] + '\n'
        text += 'Vozrast: ' + program['age'] + '\n'
        text += program['description'] + '\n'
        text += 'Prodolzhitelnost: ' + program['duration'] + '\n'
        text += 'Stoimost: ' + program['price'] + '\n\n'
    
    text += "Napishite nazvanie: beginner, junior, advanced, professional\n"
    text += "Ili 'kontakty' dlya informatsii o zapisi"
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return 'Programma ne naidena. Poprobuite snova.'
    
    text = program['name'] + '\n\n'
    text += 'Vozrast: ' + program['age'] + '\n'
    text += 'Opisanie: ' + program['description'] + '\n'
    text += 'Prodolzhitelnost kursa: ' + program['duration'] + '\n'
    text += 'Stoimost: ' + program['price'] + '\n\n'
    text += "Dlya zapisi svyazites s nami - napishite 'kontakty'"
    
    return text

def get_contacts():
    text = 'Kontakty RoboSTEAMuL:\n\n'
    text += 'Email: info@robosteamul.ru\n'
    text += 'Telefon: +7 (XXX) XXX-XX-XX\n'
    text += 'Sait: www.robosteamul.ru\n'
    text += 'Adres: g. Moskva\n\n'
    text += 'Svyazites s nami dlya zapisi v gruppakh!'
    
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
        print('Message sent to ' + str(user_id))
        return True
    except Exception as e:
        print('Error: ' + str(e))
        return False

def handle_user_message(user_id, message_text):
    msg = message_text.lower().strip()
    
    if 'programm' in msg or 'kurs' in msg or 'privet' in msg or 'hello' in msg:
        response = get_programs_info()
    elif msg in ['beginner', 'junior', 'advanced', 'professional']:
        response = get_program_details(msg)
    elif 'kontakt' in msg or 'zapis' in msg or 'telefon' in msg or 'email' in msg:
        response = get_contacts()
    else:
        response = 'Spasibo za vopros!\n\n'
        response += 'Napishite:\n'
        response += '- "programmy" dlya spiska vsekh kursov\n'
        response += '- "beginner", "junior", "advanced" ili "professional" dlya detaley\n'
        response += '- "kontakty" dlya informatsii o zapisi'
    
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
            greeting = 'Dobro pozhalovat v RoboSTEAMuL!\n\n'
            greeting += 'My nauchim vashikh detey robototekniki i programmirovaniyu.\n\n'
            greeting += 'Napishite "programmy" chtoby uznat o nashikh kursakh,\n'
            greeting += 'ili "kontakty" dlya zapisi.'
            send_message(user_id, greeting)
        
        return 'ok', 200
    
    if event_type == 'message_new':
        obj = data.get('object', {})
        message_obj = obj.get('message', {})
        user_id = message_obj.get('from_id')
        message_text = message_obj.get('text', '')
        
        if user_id and message_text:
            print('Message from ' + str(user_id) + ': ' + message_text)
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
