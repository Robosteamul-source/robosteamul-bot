"""
RoboSTEAMuL VK Bot - Полная система управления группой
Платформа: ВКонтакте (Callback API)
Версия: 1.0
Дата: 19 июля 2026
"""

import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from vk_api.utils import get_random_id
import logging
import sqlite3
from datetime import datetime, timedelta
import json
import re
from typing import Dict, List, Optional
import schedule
import time
from threading import Thread

# ==================== КОНФИГУРАЦИЯ ====================

VK_GROUP_TOKEN = "your_group_token_here"
VK_API_TOKEN = "your_api_token_here"
GROUP_ID = 000000  # ID группы
CALLBACK_SECRET = "your_secret_here"
CALLBACK_CONFIRMATION_TOKEN = "your_confirmation_token"

# ID специальных пользователей
DIRECTOR_ID = 45815523  # Игорь Иванович
ADMIN_ID = 441534266   # Наталья

# ==================== ЛОГИРОВАНИЕ ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('robosteanul_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== БАЗА ДАННЫХ ====================

class Database:
    def __init__(self, db_name='robosteanul.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        # Таблица заявок
        c.execute('''CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            child_name TEXT,
            child_birthday TEXT,
            kindergarten_number TEXT,
            group_number TEXT,
            parent_name TEXT,
            phone_number TEXT,
            program TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notification_sent BOOLEAN DEFAULT 0
        )''')
        
        # Таблица истории сообщений
        c.execute('''CREATE TABLE IF NOT EXISTS message_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            message_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Таблица состояния диалога пользователя
        c.execute('''CREATE TABLE IF NOT EXISTS user_state (
            user_id INTEGER PRIMARY KEY,
            state TEXT,
            data TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Таблица обратной связи
        c.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            feedback_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        conn.commit()
        conn.close()
    
    def save_application(self, user_id: int, data: dict) -> bool:
        """Сохранить заявку на программу"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        try:
            c.execute('''INSERT INTO applications 
                        (user_id, child_name, child_birthday, kindergarten_number, 
                         group_number, parent_name, phone_number, program)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (user_id, data.get('child_name'), data.get('child_birthday'),
                       data.get('kindergarten_number'), data.get('group_number'),
                       data.get('parent_name'), data.get('phone_number'),
                       data.get('program')))
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error saving application: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_state(self, user_id: int) -> tuple:
        """Получить состояние диалога пользователя"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('SELECT state, data FROM user_state WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return result[0], json.loads(result[1]) if result[1] else {}
        return None, {}
    
    def set_user_state(self, user_id: int, state: str, data: dict = None):
        """Установить состояние диалога пользователя"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        data_json = json.dumps(data) if data else None
        
        c.execute('''INSERT OR REPLACE INTO user_state (user_id, state, data, updated_at)
                     VALUES (?, ?, ?, CURRENT_TIMESTAMP)''',
                  (user_id, state, data_json))
        conn.commit()
        conn.close()
    
    def get_pending_applications(self) -> List[dict]:
        """Получить незакрытые заявки"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM applications WHERE status = 'pending' ''')
        columns = [description[0] for description in c.description]
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(columns, row)) for row in results]
    
    def mark_notification_sent(self, app_id: int):
        """Отметить, что уведомление отправлено"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        c.execute('UPDATE applications SET notification_sent = 1 WHERE id = ?', (app_id,))
        conn.commit()
        conn.close()

# ==================== БАЗА ЗНАНИЙ О ПРОГРАММАХ ====================

PROGRAMS_DB = {
    'робототехника robosteanul': {
        'name': 'Робототехника РобоСТЕАМ',
        'age': '3-4 года',
        'price': '300 ₽',
        'description': 'Введение в основы робототехники для самых маленьких'
    },
    'робототехника brick': {
        'name': 'Робототехника РобоСТЕАМ Брик',
        'age': '5-6 лет',
        'price': '300 ₽',
        'description': 'Продвинутое обучение с использованием кирпичных конструкторов'
    },
    'робототехника про': {
        'name': 'Робототехника РобоСТЕАМ Про',
        'age': '6-8 лет',
        'price': '400 ₽',
        'description': 'Профессиональный уровень робототехники'
    },
    'хореография': {
        'name': 'Хореография',
        'age': '3-8 лет',
        'price': '350 ₽',
        'description': 'Развитие координации и творчества через танец'
    },
    'логопед': {
        'name': 'Логопед и развитие речи',
        'age': '3-7 лет',
        'price': '600 ₽ (+800 ₽ диагностика)',
        'description': 'Коррекция речи и развитие коммуникативных навыков'
    },
    'дошколёнок два года': {
        'name': 'Дошколёнок за два года до Школы',
        'age': '4-5 лет',
        'price': '350 ₽',
        'description': 'Подготовка к школе для детей 4-5 лет'
    },
    'дошколёнок год': {
        'name': 'Дошколёнок За год до Школы',
        'age': '6-7 лет',
        'price': '375 ₽',
        'description': 'Интенсивная подготовка к школе для детей 6-7 лет'
    }
}

# ==================== VK БОТ ====================

class RoboSTEAMuLBot:
    def __init__(self, group_token: str, api_token: str, group_id: int):
        self.vk_session = vk_api.VkApi(token=group_token)
        self.vk = self.vk_session.get_api()
        self.vk_api_session = vk_api.VkApi(token=api_token)
        self.vk_api = self.vk_api_session.get_api()
        self.group_id = group_id
        self.longpoll = VkBotLongPoll(self.vk_session, group_id)
        self.db = Database()
        
        logger.info("RoboSTEAMuL Bot initialized")
    
    def send_message(self, peer_id: int, message: str, keyboard=None):
        """Отправить сообщение"""
        try:
            params = {
                'peer_id': peer_id,
                'message': message,
                'random_id': get_random_id(),
            }
            if keyboard:
                params['keyboard'] = json.dumps(keyboard)
            
            self.vk.messages.send(**params)
            logger.info(f"Message sent to {peer_id}")
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    def get_user_info(self, user_id: int) -> dict:
        """Получить информацию о пользователе"""
        try:
            user_info = self.vk.users.get(user_ids=user_id)[0]
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    def handle_join_event(self, event):
        """Обработка вступления в группу"""
        user_id = event.object.user_id
        
        greeting_message = """👋 Добро пожаловать в RoboSTEAMuL!

Мы предлагаем 7 образовательных программ для детей:

🤖 Робототехника РобоСТЕАМ (3-4 года) - 300 ₽
🎯 Робототехника РобоСТЕАМ Брик (5-6 лет) - 300 ₽
⚙️ Робототехника РобоСТЕАМ Про (6-8 лет) - 400 ₽
💃 Хореография (3-8 лет) - 350 ₽
🗣️ Логопед и развитие речи (3-7 лет) - 600 ₽ + диагностика
📚 Дошколёнок за два года до школы (4-5 лет) - 350 ₽
📖 Дошколёнок за год до школы (6-7 лет) - 375 ₽

Напишите название интересующей вас программы или нажмите на один из вариантов!"""
        
        self.send_message(user_id, greeting_message)
        logger.info(f"User {user_id} joined the group")
    
    def handle_leave_event(self, event):
        """Обработка выхода из группы"""
        user_id = event.object.user_id
        
        feedback_message = """😢 Нам очень жаль, что вы уходите! 

Можете ли вы рассказать, почему вы решили отписаться? Ваша обратная связь помогает нам улучшаться."""
        
        # Отправляем только в том случае, если сможем получить информацию о пользователе
        try:
            self.vk.messages.send(
                peer_id=user_id,
                message=feedback_message,
                random_id=get_random_id()
            )
        except:
            pass  # Пользователь уже вышел, сообщение не отправится
        
        logger.info(f"User {user_id} left the group")
    
    def handle_message(self, event):
        """Основная обработка сообщений"""
        user_id = event.object.message['from_id']
        text = event.object.message['text'].lower()
        
        user_state, user_data = self.db.get_user_state(user_id)
        
        # Специальные команды для директора
        if user_id == DIRECTOR_ID:
            if text in ['сводка', '/сводка', 'дневная сводка']:
                self.send_daily_report(user_id)
                return
        
        # Специальные команды для администратора
        if user_id == ADMIN_ID:
            if text in ['/заявки', 'заявки']:
                self.send_applications_report(user_id)
                return
        
        # Обработка записи на программу
        if 'запис' in text or user_state == 'recording_program':
            self.handle_program_registration(user_id, text, user_state, user_data)
            return
        
        # Обработка вопросов о программах
        if any(program_key in text for program_key in PROGRAMS_DB.keys()):
            self.handle_program_inquiry(user_id, text)
            return
        
        # Поиск программы по ключевым словам
        for key, program in PROGRAMS_DB.items():
            if key in text:
                response = f"""📋 {program['name']}
                
Возраст: {program['age']}
Цена: {program['price']}
Описание: {program['description']}

Хотите записаться на эту программу? Напишите 'запись' или нажмите кнопку ниже."""
                
                self.send_message(user_id, response)
                return
        
        # Стандартный ответ
        default_response = """Привет! 👋 
        
Я здесь, чтобы помочь вам узнать о наших программах. 
Какую программу вас интересует? Напишите название или выберите из списка:
- Робототехника
- Хореография  
- Логопед
- Дошколёнок"""
        
        self.send_message(user_id, default_response)
    
    def handle_program_inquiry(self, user_id: int, text: str):
        """Ответ на вопрос о программе"""
        matched_program = None
        
        for key, program in PROGRAMS_DB.items():
            if key in text:
                matched_program = program
                break
        
        if matched_program:
            response = f"""📋 {matched_program['name']}
            
✅ Возраст: {matched_program['age']}
💰 Цена: {matched_program['price']}
ℹ️ {matched_program['description']}

Вы хотите записать ребенка на эту программу? 
Ответьте 'да' и заполните анкету!"""
            
            self.send_message(user_id, response)
    
    def handle_program_registration(self, user_id: int, text: str, 
                                   user_state: Optional[str], user_data: dict):
        """Обработка процесса записи на программу"""
        
        # Шаг 1: Выбор программы
        if not user_state or user_state == 'start':
            self.send_message(user_id, "🎓 Какую программу выбираете?")
            for key, program in PROGRAMS_DB.items():
                msg = f"• {program['name']} ({program['age']})"
                self.send_message(user_id, msg)
            self.db.set_user_state(user_id, 'choose_program', {})
            return
        
        # Шаг 2: Запрос имени ребенка
        if user_state == 'choose_program':
            user_data['program'] = text
            self.send_message(user_id, "👧 Как зовут вашего ребенка?")
            self.db.set_user_state(user_id, 'enter_child_name', user_data)
            return
        
        # Шаг 3: Дата рождения
        if user_state == 'enter_child_name':
            user_data['child_name'] = text
            self.send_message(user_id, "📅 Дата рождения ребенка (ДД.MM.ГГГГ)?")
            self.db.set_user_state(user_id, 'enter_birthday', user_data)
            return
        
        # Шаг 4: Номер детского сада
        if user_state == 'enter_birthday':
            user_data['child_birthday'] = text
            self.send_message(user_id, "🏢 Номер детского сада?")
            self.db.set_user_state(user_id, 'enter_kindergarten', user_data)
            return
        
        # Шаг 5: Номер группы
        if user_state == 'enter_kindergarten':
            user_data['kindergarten_number'] = text
            self.send_message(user_id, "👥 Номер группы?")
            self.db.set_user_state(user_id, 'enter_group', user_data)
            return
        
        # Шаг 6: ФИО родителя
        if user_state == 'enter_group':
            user_data['group_number'] = text
            self.send_message(user_id, "👨‍👩‍👧 ФИО родителя?")
            self.db.set_user_state(user_id, 'enter_parent_name', user_data)
            return
        
        # Шаг 7: Номер телефона
        if user_state == 'enter_parent_name':
            user_data['parent_name'] = text
            self.send_message(user_id, "📱 Номер телефона?")
            self.db.set_user_state(user_id, 'enter_phone', user_data)
            return
        
        # Шаг 8: Обработка номера телефона
        if user_state == 'enter_phone':
            phone_match = re.search(r'\d{10,}', text.replace(' ', '').replace('-', '').replace('+', ''))
            
            if phone_match:
                user_data['phone_number'] = phone_match.group()
                
                # Сохранить заявку
                if self.db.save_application(user_id, user_data):
                    confirmation = f"""✅ Спасибо! Ваша заявка принята!

📋 Данные:
Ребенок: {user_data.get('child_name')}
Дата рождения: {user_data.get('child_birthday')}
Детский сад: {user_data.get('kindergarten_number')}
Группа: {user_data.get('group_number')}
Родитель: {user_data.get('parent_name')}
Телефон: {user_data.get('phone_number')}
Программа: {user_data.get('program')}

Мы свяжемся с вами в ближайшее время!"""
                    
                    self.send_message(user_id, confirmation)
                    
                    # Отправить уведомление администратору
                    self.send_admin_notification(user_id, user_data)
                    
                    # Очистить состояние
                    self.db.set_user_state(user_id, None, {})
                else:
                    self.send_message(user_id, "❌ Ошибка при сохранении заявки. Попробуйте позже.")
            else:
                self.send_message(user_id, "📱 Пожалуйста, введите корректный номер телефона")
    
    def send_admin_notification(self, user_id: int, user_data: dict):
        """Отправить уведомление администратору о новой заявке"""
        try:
            user_info = self.get_user_info(user_id)
            profile_link = f"https://vk.com/id{user_id}"
            
            notification = f"""📬 НОВАЯ ЗАЯВКА!

Родитель: {user_info.get('first_name', '')} {user_info.get('last_name', '')}
Профиль: {profile_link}

Ребенок: {user_data.get('child_name')}
Дата рождения: {user_data.get('child_birthday')}
Детский сад: {user_data.get('kindergarten_number')}
Группа: {user_data.get('group_number')}
ФИО родителя: {user_data.get('parent_name')}
Телефон: {user_data.get('phone_number')}
Программа: {user_data.get('program')}"""
            
            self.send_message(ADMIN_ID, notification)
            logger.info(f"Admin notification sent for user {user_id}")
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
    
    def send_daily_report(self, director_id: int):
        """Отправить ежедневную сводку директору"""
        try:
            pending_apps = self.db.get_pending_applications()
            
            report = f"""📊 ЕЖЕДНЕВНАЯ СВОДКА
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

📝 Новые заявки: {len(pending_apps)}
"""
            
            if pending_apps:
                report += "\nДетали:\n"
                for app in pending_apps:
                    report += f"""
• {app['child_name']} - {app['program']}
  Родитель: {app['parent_name']}
  Телефон: {app['phone_number']}
  Статус: {app['status']}"""
            
            self.send_message(director_id, report)
            logger.info(f"Daily report sent to director {director_id}")
        except Exception as e:
            logger.error(f"Error sending daily report: {e}")
    
    def send_applications_report(self, admin_id: int):
        """Отправить отчет о заявках администратору"""
        try:
            pending_apps = self.db.get_pending_applications()
            
            report = f"""📋 ОТЧЕТ О ЗАЯВКАХ
Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

Всего заявок: {len(pending_apps)}
"""
            
            for app in pending_apps:
                report += f"""

🔹 ID: {app['id']}
   Ребенок: {app['child_name']}
   Родитель: {app['parent_name']}
   Телефон: {app['phone_number']}
   Программа: {app['program']}
   Статус: {app['status']}"""
            
            self.send_message(admin_id, report)
        except Exception as e:
            logger.error(f"Error sending applications report: {e}")
    
    def run(self):
        """Запустить бота"""
        logger.info("Bot started listening...")
        
        for event in self.longpoll.listen():
            try:
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self.handle_message(event)
                
                elif event.type == VkBotEventType.USER_JOIN:
                    self.handle_join_event(event)
                
                elif event.type == VkBotEventType.USER_LEAVE:
                    self.handle_leave_event(event)
            
            except Exception as e:
                logger.error(f"Error handling event: {e}")

# ==================== ЗАПУСК ====================

if __name__ == "__main__":
    bot = RoboSTEAMuLBot(VK_GROUP_TOKEN, VK_API_TOKEN, GROUP_ID)
    bot.run()
