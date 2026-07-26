from flask import Flask, request
import requests
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Переменные окружения (или установите прямо здесь для теста)
VK_TOKEN = os.getenv('VK_TOKEN', 'ваш_vk_token')
VK_SECRET = os.getenv('VK_SECRET', 'ваш_secret_key')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')
GROUP_ID = os.getenv('GROUP_ID', '192923833')

def check_signature(body, secret):
    """Проверка подписи от VK"""
    try:
        h = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        return h
    except:
        return None

def send_greeting(user_id):
    """Отправить приветствие новому подписчику"""
    greeting_text = """👋 Добро пожаловать в RoboSTEAMuL!

Здесь вы найдете:
🤖 Обновления о роботике
💡 Полезные советы и уроки
📚 Документацию и примеры кода
🎯 Новости проектов

Спасибо, что присоединились! 🚀"""
    
    try:
        response = requests.post(
            'https://api.vk.com/method/messages.send',
            {
                'access_token': VK_TOKEN,
                'user_id': user_id,
                'message': greeting_text,
                'v': '5.199',
                'random_id': 0
            }
        )
        if response.status_code == 200:
            print(f"✓ Сообщение отправлено пользователю {user_id}")
        else:
            print(f"✗ Ошибка при отправке: {response.text}")
    except Exception as e:
        print(f"✗ Исключение: {e}")

@app.route('/callback', methods=['POST'])
def callback():
    """Основной обработчик Callback API"""
    data = request.get_json()
    
    if data is None:
        return 'Invalid request', 400
    
    # Проверка типа события
    event_type = data.get('type')
    
    # Подтверждение сервера (при первой настройке)
    if event_type == 'confirmation':
        print("✓ Confirmation event received")
        return VK_CONFIRMATION_TOKEN
    
    # Обработка события подписки
    if event_type == 'wall_post_new':
        print("📝 New wall post")
        return 'ok'
    
    if event_type == 'user_subscribed':
        print(f"🔔 New subscriber event received")
        
        user_id = data.get('object', {}).get('user_id')
        if user_id:
            print(f"👤 User ID: {user_id}")
            send_greeting(user_id)
        
        return 'ok'
    
    # Для других типов событий
    print(f"Event type: {event_type}")
    return 'ok'

@app.route('/', methods=['GET'])
def home():
    """Главная страница для проверки что сервер работает"""
    return {
        'status': 'ok',
        'bot': 'RoboSTEAMuL VK Bot',
        'group_id': GROUP_ID
    }, 200

@app.route('/health', methods=['GET'])
def health():
    """Health check для Render"""
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    # Для локального тестирования
    app.run(host='0.0.0.0', port=5000, debug=True)
