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
        'description': 'Vvedenie v osnovy robototehniki. Sborka prostyh konstrukcij i pervye programmy na Scratch.',
        'duration': '8 nedel',
        'price': '4000 rub/mesyac'
    },
    'junior': {
        'name': 'Junior Robotics',
        'age': '9-11 let',
        'description': 'Programmirovanie robotov LEGO Mindstorms. Reshenie zadach i uchastie v sorevnovaniyah.',
        'duration': '12 nedel',
        'price': '5000 rub/mesyac'
    },
    'advanced': {
        'name': 'Advanced Robotics',
        'age': '12-15 let',
        'description': 'Python programmirovanie. Rabota s Arduino i mikrokontrollerami. Sozdanie sobstvennyh proektov.',
        'duration': '16 nedel',
        'price': '6000 rub/mesyac'
    },
    'professional': {
        'name': 'Pro Developer Track',
        'age': '16+ let',
        'description': 'Prodvignutaya robototehnika, mashinnoe obuchenie, IoT proekty. Podgotovka k ekzamenam.',
        'duration': '24 nedeli',
        'price': '7500 rub/mesyac'
    }
}

def get_programs_info():
    text = 'Programmy obucheniya RoboSTEAMuL:\n\n'
    
    for key, program in PROGRAMS.items():
        text += f"{program['name']}\n"
        text += f"Vozrast: {program['age']}\n"
        text += f"{program['description']}\n"
        text += f"Dlitelnost: {program['duration']}\n"
        text += f"Stoimost: {program['price']}\n\n"
    
    text += "Napishite nazvanie programmy dlya podrobnoy informacii (naprimep: beginner, junior, advanced, professional)\n"
    text += "Ili napishite 'kontakty' dlya polucheniya informacii o zapisi."
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    text = f"{program['name']}\n\n"
    text += f"Vozrast: {program['age']}\n"
    text += f"Opisanie: {program['description']}\n"
    text += f"Dlitelnost kursa: {program['duration']}\n"
    text += f"Stoimost: {program['price']}\n\n"
    text += "Dlya zapisi svyazites s nami cherez formu obratnoy svyazi v soobshchestve ili napishite 'kontakty'"
    
    return text

def get_contacts():
    text = "Kak s nami svyazatsya:\n\n"
    text += "Email: info@robosteamul.ru\n"
    text += "Telefon: +7 (XXX) XXX-XX-XX\n"
    text += "Sait: www.robosteamul.ru\n"
    text += "Adres: g. Moskva\n\n"
    text += "Ostavte zayavku v soobshchestve - nash menedzher svyazetsya s vami v techenie 24 chasov!"
    
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
    
    if any(word in msg_lower for word in ['programm', 'obucheni', 'kurs', 'pomoshch', 'privet', 'hi', 'hello', 'spisok']):
        response = get_programs_info()
    
    elif msg_lower in ['beginner', 'junior', 'advanced', 'professional']:
        response = get_program_details(msg_lower)
    
    elif any(word in msg_lower for word in ['kontakt', 'svyaz', 'telefon', 'adres', 'email', 'zapis']):
        response = get_contacts()
    
    else:
        response = "Spasibo za vopros!\n\n"
        response += "Napishite:\n"
        response += "- 'programmy' dlya spiska vsekh kursov\n"
        response += "- 'beginner', 'junior', 'advanced' ili 'professional' dlya detaley kursa\n"
        response += "- 'kontakty' dlya informacii o zapisi\n\n"
robosteamul.ru. Доменное имя продаётся
robosteamul.ru. Доменное имя продаётся
robosteamul.ru


nse += "Ili zadayte svoy vopros - my postaraemsya pomoct!"
    
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
            greeting = 'Dobro pozhalovat v RoboSTEAMuL!\n\nMy nauchim vashikh detey robototekhnike i programmirovaniyu.\n\nNapishite "programmy" chtoby uznat o nashikh kursakh, ili "kontakty" dlya zapisi.'
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
    app.run(host='0.0.0.0', port=5000, debug=False) respo
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run


