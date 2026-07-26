from flask import Flask, request
import requests
import os

app = Flask(__name__)

VK_TOKEN = os.getenv('VK_TOKEN', '')
VK_SECRET = os.getenv('VK_SECRET', '')
VK_CONFIRMATION_TOKEN = os.getenv('VK_CONFIRMATION_TOKEN', '43a38a83')
GROUP_ID = os.getenv('GROUP_ID', '192923833')

def send_greeting(user_id):
    """Send greeting message to new subscriber"""
    message = """Hello, welcome to RoboSTEAMuL!
    
Here you will find:
- Robotics updates
- Useful tips and tutorials
- Documentation and code examples
- Project news

Thank you for joining us!"""
    
    try:
        response = requests.post(
            'https://api.vk.com/method/messages.send',
            {
                'access_token': VK_TOKEN,
                'user_id': user_id,
                'message': message,
                'v': '5.199',
                'random_id': 0
            }
        )
        print(f"Message sent to user {user_id}")
    except Exception as e:
        print(f"Error: {e}")

@app.route('/callback', methods=['POST'])
def callback():
    """Handle VK Callback API events"""
    data = request.get_json()
    
    if data is None:
        return 'ok', 200
    
    event_type = data.get('type')
    
    if event_type == 'confirmation':
        print("Confirmation received")
        return VK_CONFIRMATION_TOKEN
    
    if event_type == 'user_subscribed':
        user_id = data.get('object', {}).get('user_id')
        if user_id:
            print(f"New subscriber: {user_id}")
            send_greeting(user_id)
        return 'ok'
    
    return 'ok', 200

@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return {'status': 'ok', 'bot': 'RoboSTEAMuL'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
app.run - Данный веб-сайт выставлен на продажу! - app Ресурсы и информация.
app.run


