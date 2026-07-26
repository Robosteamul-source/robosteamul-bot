from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

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
    except Exception as e:
        print(f'Error: {e}')

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    
    if not data:
        return 'ok', 200
    
    event_type = data.get('type')
    
    if event_type == 'confirmation':
        return VK_CONFIRMATION_TOKEN
    
    if event_type == 'user_subscribed':
        obj = data.get('object', {})
        user_id = obj.get('user_id')
        
        if user_id:
            greeting = 'Welcome to RoboSTEAMuL! Thanks for subscribing!'
            send_message(user_id, greeting)
        
        return 'ok', 200
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run


from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')

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
    except Exception as e:
        print(f'Error: {e}')

@app.route('/callback', methods=['POST'])
def callback():
    data = request.get_json()
    
    if not data:
        return 'ok', 200
    
    event_type = data.get('type')
    
    if event_type == 'confirmation':
        return VK_CONFIRMATION_TOKEN
    
    if event_type == 'user_subscribed':
        obj = data.get('object', {})
        user_id = obj.get('user_id')
        
        if user_id:
            greeting = 'Welcome to RoboSTEAMuL! Thanks for subscribing!'
            send_message(user_id, greeting)
        
        return 'ok', 200
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return {'status': 'ok'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run




