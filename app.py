#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VK Bot для Render
Исправленная версия без ошибок импорта
"""

import os
import json
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
import requests

# ===== КОНФИГУРАЦИЯ ЛОГИРОВАНИЯ =====
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ =====
load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
API_VERSION = os.getenv('API_VERSION', '5.131')
SECRET = os.getenv('SECRET', '')
CONFIRMATION_TOKEN = os.getenv('CONFIRMATION_TOKEN', '')

# ===== ПРОВЕРКА ПЕРЕМЕННЫХ =====
if not VK_TOKEN:
    logger.error("❌ VK_TOKEN не установлен!")
    raise ValueError("Переменная VK_TOKEN обязательна")

if not GROUP_ID:
    logger.error("❌ GROUP_ID не установлен!")
    raise ValueError("Переменная GROUP_ID обязательна")

logger.info(f"✅ VK_TOKEN загружен")
logger.info(f"✅ GROUP_ID = {GROUP_ID}")

# ===== ИНИЦИАЛИЗАЦИЯ FLASK =====
app = Flask(__name__)

# ===== ИНИЦИАЛИЗАЦИЯ VK API =====
try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    logger.info("✅ VK API успешно инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации VK API: {e}")

# ===== ФУНКЦИИ =====

def send_message(user_id, message, keyboard=None):
    """Отправить сообщение пользователю"""
    try:
        msg_params = {
            'user_id': user_id,
            'message': message,
            'random_id': get_random_id(),
            'v': API_VERSION
        }
        
        if keyboard:
            msg_params['keyboard'] = keyboard
        
        vk.messages.send(**msg_params)
        logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        return False

def get_group_info():
    """Получить информацию о группе"""
    try:
        info = vk.groups.getById(group_id=GROUP_ID)
        return info[0] if info else None
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации группы: {e}")
        return None

def handle_message(event):
    """Обработчик входящих сообщений"""
    user_id = event.object.message['from_id']
    text = event.object.message['text'].lower()
    
    logger.info(f"📨 Сообщение от {user_id}: {text}")
    
    # ===== КОМАНДЫ =====
    if text == 'привет' or text == 'hi':
        response = f"👋 Привет, пользователь {user_id}!"
        send_message(user_id, response)
    
    elif text == 'помощь' or text == 'help':
        response = """
🤖 Доступные команды:
• привет - приветствие
• помощь - эта справка
• инфо - информация о боте
• пинг - проверка соединения
        """
        send_message(user_id, response)
    
    elif text == 'инфо' or text == 'info':
        group = get_group_info()
        if group:
            response = f"ℹ️ Группа: {group.get('name', 'Неизвестно')}"
        else:
            response = "❌ Не удалось получить информацию"
        send_message(user_id, response)
    
    elif text == 'пинг' or text == 'ping':
        response = "🏓 ПОНГ! Соединение работает!"
        send_message(user_id, response)
    
    else:
        response = "❓ Неизвестная команда. Введите 'помощь' для справки."
        send_message(user_id, response)

# ===== FLASK ROUTES =====

@app.route('/', methods=['GET'])
def home():
    """Главная страница"""
    return jsonify({
        'status': 'running',
        'bot': 'robosteamul_vk_bot',
        'version': '1.0.0'
    })

@app.route('/callback', methods=['POST'])
def callback():
    """Обработчик вебхуков от VK"""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("⚠️ Пустой запрос")
            return jsonify({'error': 'Empty request'}), 400
        
        # ===== ПОДТВЕРЖДЕНИЕ СЕРВЕРА =====
        if data.get('type') == 'confirmation':
            logger.info("✅ Запрос подтверждения сервера")
            return CONFIRMATION_TOKEN, 200
        
        # ===== ПРОВЕРКА СЕКРЕТНОГО КЛЮЧА =====
        if SECRET and data.get('secret') != SECRET:
            logger.warning("⚠️ Неверный secret")
            return jsonify({'error': 'Invalid secret'}), 403
        
        # ===== ОБРАБОТКА СОБЫТИЙ =====
        event_type = data.get('type')
        object_data = data.get('object', {})
        
        # Событие: новое сообщение
        if event_type == 'message_new':
            message = object_data.get('message', {})
            
            # Пропускаем сообщения от сервиса
            if message.get('from_id') < 0:
                logger.info("ℹ️ Сообщение от сервиса, игнорируем")
                return jsonify({'ok': True}), 200
            
            # Пропускаем свои сообщения
            if message.get('from_id') == message.get('peer_id'):
                logger.info("ℹ️ Собственное сообщение, игнорируем")
                return jsonify({'ok': True}), 200
            
            # Обрабатываем сообщение
            class Event:
                def __init__(self, data):
                    self.object = type('obj', (object,), {'message': data})()
            
            event = Event(message)
            handle_message(event)
        
        # Другие типы событий
        else:
            logger.info(f"ℹ️ Событие типа: {event_type}")
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Проверка здоровья приложения"""
    try:
        info = get_group_info()
        return jsonify({
            'status': 'healthy',
            'api': 'connected' if info else 'disconnected'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def stats():
    """Статистика бота"""
    return jsonify({
        'status': 'running',
        'group_id': GROUP_ID,
        'api_version': API_VERSION,
        'flask_debug': app.debug
    })

# ===== ERROR HANDLERS =====

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    logger.error(f"❌ Внутренняя ошибка сервера: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ===== MAIN =====

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    debug = os.getenv('DEBUG', 'False') == 'True'
    
    logger.info(f"🚀 Запуск VK бота на порту {port}")
    logger.info(f"🔗 Callback URL: https://[ваш-сервис].onrender.com/callback")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        use_reloader=False
    )
