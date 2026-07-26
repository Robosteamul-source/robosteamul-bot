from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

PROGRAMS = {
    'robo_34': {
        'name': 'Robototeknika RoboSTEAM',
        'age': '3-4 goda',
        'description': 'Pervye shagi v mir robototekniki. Razvitie logicheskogo myshleniya i melkoy motoriki.',
        'price': '300 rub za zanyatie',
        'short': 'robo_34'
    },
    'brick': {
        'name': 'Robototeknika RoboSTEAM Brick',
        'age': '5-6 let',
        'description': 'Postroenie i programmirovanie robotov. Osnovy konstruirovaniya i algoritmiki.',
        'price': '300 rub za zanyatie',
        'short': 'brick'
    },
    'pro': {
        'name': 'Robototeknika RoboSTEAM Pro',
        'age': '6-8 let',
        'description': 'Prodvinutoe programmirovanie i sozdanie slozhnyh robotov. Uchastie v sorevnovaniyakh.',
        'price': '400 rub za zanyatie',
        'short': 'pro'
    },
    'dance': {
        'name': 'Horeografiya',
        'age': '3-8 let',
        'description': 'Razvitie tanca, ritma i koordinacii. Tvorcheskie nomera i vyestaleniya.',
        'price': '350 rub za zanyatie',
        'short': 'dance'
    },
    'logoped': {
        'name': 'Logoped i razvitie rechi',
        'age': '3-7 let',
        'description': 'Korrekciya zvukoporoiznosheniya i razvitie rechi. Individualnye zanyatiya.',
        'price': '600 rub za zanyatie (diagnostika +800 rub)',
        'short': 'logoped'
    },
    'school_2': {
        'name': 'Doshkolenok za dva goda do Shkoly',
        'age': '4-5 let',
        'description': 'Kompleksnaya podgotovka k shkole. Gramota, arifmetika, poznavatelno-rechevoe razvitie.',
        'price': '350 rub za zanyatie',
        'short': 'school_2'
    },
    'school_1': {
        'name': 'Doshkolenok Za god do Shkoly',
        'age': '6-7 let',
        'description': 'Intensivnaya podgotovka v vypusknoy god. Osvoeniya shkol\'nykh navykov i samodisipliny.',
        'price': '375 rub za zanyatie',
        'short': 'school_1'
    }
}

def get_all_programs():
    text = 'Vse programmy RoboSTEAM:\n\n'
    
    for key, program in PROGRAMS.items():
        text += '1. ' + program['name'] + '\n'
        text += '   Vozrast: ' + program['age'] + '\n'
        text += '   Cena: ' + program['price'] + '\n\n'
    
    text += 'Napishite nazvanie ili nomer programmy dlya podrobnoy informacii.\n'
    text += 'Naprimep: robo_34, brick, pro, dance, logoped, school_2, school_1\n'
    text += "Ili 'kontakty' dlya zapisi"
    
    return text

def get_program_details(program_key):
    program = PROGRAMS.get(program_key.lower())
    
    if not program:
        return None
    
    text = program['name'] + '\n\n'
    text += 'Vozrast: ' + program['age'] + '\n'
    text += 'Cena: ' + program['price'] + '\n\n'
    text += 'Opisanie:\n' + program['description'] + '\n\n'
    text += "Dlya zapisi ili voprosov napishite 'kontakty' ili 'zvonite'"
    
    return text

def get_programs_by_age(age_text):
    age_lower = age_text.lower().strip()
    matching = []
    
    for key, program in PROGRAMS.items():
        if age_lower in program['age'].lower():
            matching.append(f"{program['name']} ({program['age']}) - {program['price']}")
    
    if not matching:
        return 'Programmam dlya etogo vozrasta ne nayden. Napishite "programmy" dlya polnogo spiska.'
    
    text = 'Programmy dlya vozrasta ' + age_text + ':\n\n'
    for prog in matching:
        text += '- ' + prog + '\n'
    
    text += '\nNapishite nazvanie programmy dlya detaley'
    return text

def get_contacts():
    text = 'Kontakty RoboSTEAM:\n\n'
    text += 'Email: info@robosteam.ru\n'
    text += 'Telefon: +7 (XXX) XXX-XX-XX\n'
    text += 'Adres: Moskva\n'
    text += 'Sait: www.robosteam.ru\n\n'
    text += 'Dlya zapisi v gruppakh:\n'
    text += '- Pishite nam v messenger\n'
    text += '- Zvonite po telefonu\n'
    text += '- Prihodite k nam v ofis\n\n'
    text += 'Dostupna besplatnaya pervaya konsultaciya!'
    
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
    
    if 'programm' in msg or 'kurs' in msg or 'chto' in msg or 'kakiye' in msg:
        response = get_all_programs()
    
    elif msg in ['robo_34', 'brick', 'pro', 'dance', 'logoped', 'school_2', 'school_1']:
        response = get_program_details(msg)
    
    elif 'kontakt' in msg or 'zapis' in msg or 'zvon' in msg or 'adres' in msg or 'email' in msg:
        response = get_contacts()
    
    elif 'vozrast' in msg or 'let' in msg or 'goda' in msg:
        words = msg.split()
        for word in words:
            if word.isdigit():
                age = word
                response = get_programs_by_age(age)
                send_message(user_id, response)
                return
        response = 'Ukazhite vozrast (naprimep: 5, 6, 7)'
    
    else:
        response = 'Spasibo za vopros!\n\n'
        response += 'Napishite:\n'
        response += '- "programmy" dlya spiska vsekh kursov\n'
        response += '- "robo_34", "brick", "pro", "dance", "logoped", "school_2", "school_1" dlya detaley\n'
        response += '- vozrast (naprimep: 5 let) dlya programm po vozrastu\n'
        response += '- "kontakty" dlya informacii o zapisi\n\n'
        response += 'Ili zadayte lyuboy vopros - my postaraemsya pomoch!'
    
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
            greeting = 'Dobro pozhalovat v RoboSTEAM!\n\n'
            greeting += 'My predlagaem 7 obrazovatelnyh programm dlya detey ot 3 do 8 let:\n'
            greeting += '- Robototeknika\n'
            greeting += '- Horeografiya\n'
            greeting += '- Razvitie rechi\n'
            greeting += '- Podgotovka k shkole\n\n'
            greeting += 'Napishite "programmy" dlya polnogo spiska,\n'
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
