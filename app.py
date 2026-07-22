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
    logger.error("VK_TOKEN or GROUP_ID not set")
    raise ValueError("VK_TOKEN and GROUP_ID are required")

app = Flask(__name__)

try:
    vk_session = vk_api.VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    logger.info("VK API initialized successfully")
except Exception as e:
    logger.error(f"VK API error: {e}")

def send_message(user_id, message):
    try:
        vk.messages.send(
            user_id=user_id,
            message=message,
            random_id=get_random_id(),
            v=API_VERSION
        )
        logger.info(f"Message sent to user {user_id}")
    except Exception as e:
        logger.error(f"Send error: {e}")

def handle_message(text, user_id):
    text = text.lower().strip()
    
    if text in ['привет', 'hi', 'hello']:
        send_message(user_id, f"Привет, пользователь {user_id}!")
    elif text in ['пинг', 'ping']:
