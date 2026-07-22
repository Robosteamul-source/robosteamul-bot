#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
import vk_api
from vk_api.utils import get_random_id

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

VK_TOKEN = os.getenv('VK_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')
API_VERSION = os.getenv('API_VERSION', '5.131')
SECRET = os.getenv('SECRET', '')
CONFIRMATION_TOKEN = os.getenv('CONFIRMATION_TOKEN', '')

if not VK_TOKEN or not GROUP_ID:
    logger.error("❌ VK_TOKEN или GROUP_ID не установлены!")
    raise ValueError("VK_TOKEN и GROUP_ID обязательны")

app = Flask(__name__)

try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    logger.info("✅ VK API инициализирован")
except Exception as e:
    logger.error(f"❌ Ошибка VK API: {e}")

def send_message(user_id, message):
    try:
        vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            v=API_VERSION
        )
        logger.info(f"✅ Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")

def handle_message(text, user_id):
    text = text.lower()
    
    if text == 'привет' or text == 'hi':
        send_message(user_id, f"👋 Привет, пользователь {user_id}!")
    elif text == 'помощь' or text == 'help':
        send_message(user_id, "🤖 Введите: привет, помощь, инфо, пинг")
    elif text == 'пинг' or text == 'ping':
        send_message(user_id, "🏓 ПОНГ!")
    else:
        send_message(user_id, "❓ Неизвестная команда. Напишите 'помощь'")

@app.route('/', methods=['GET'])
def home():
    return jsonify({'status': 'running', 'bot': 'vk_bot', 'version': '1.0'})

@app.route('/callback', methods=['POST'])
def callback():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Empty'}), 400
        
        # Подтверждение сервера VK
        if data.get('type') == 'confirmation':
            logger.info("✅ Confirmation request received")
            return CONFIRMATION_TOKEN, 200
        
        # Проверка SECRET
        if SECRET and data.get('secret') != SECRET:
            logger.warning("⚠️ Invalid secret key")
            return jsonify({'error': 'Invalid secret'}), 403
        
        # Обработка события сообщения
        if data.get('type') == 'message_new':
            message = data.get('object', {}).get('message', {})
            from_id = message.get('from_id')
            text = message.get('text', '')
            
            # Игнорируем сообщения от сервиса (отрицательные ID)
            if from_id < 0:
                logger.info("ℹ️ Service message, ignoring")
                return jsonify({'ok': True}), 200
            
            logger.info(f"📨 Message from {from_id}: {text}")
            handle_message(text, from_id)
        
        return jsonify({'ok': True}), 200
    
    except Exception as e:
        logger.error(f"❌ Callback error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'vk_bot'}), 200

@app.route('/stats', methods=['GET'])
def stats():
    """Bot stats"""
    return jsonify({'status': 'running', 'group_id': GROUP_ID, 'api_version': API_VERSION}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"🚀 Starting VK bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
