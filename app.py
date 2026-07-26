import vk_api
from vk_api.longpoll import VkLongPoll, Event
import requests
import json

# Ваши данные (замените на свои из Image 2)
VK_TOKEN = "ваш_vk_token"  # Из переменной VK_TOKEN
GROUP_ID = 192923833  # Ваш ID группы
VK_SECRET_KEY = "ваш_secret_key"  # Из VK_SECRET_KEY

class SubscriberGreeter:
    def __init__(self, token, group_id):
        self.vk = vk_api.VkApi(token=token)
        self.group_id = group_id
        self.longpoll = VkLongPoll(self.vk, group_id)
    
    def send_message(self, user_id, text):
        """Отправить личное сообщение пользователю"""
        try:
            self.vk.method('messages.send', {
                'user_id': user_id,
                'message': text,
                'random_id': 0
            })
            print(f"✓ Сообщение отправлено пользователю {user_id}")
        except Exception as e:
            print(f"✗ Ошибка при отправке: {e}")
    
    def greet_subscriber(self, user_id):
        """Приветствие нового подписчика"""
        greeting_text = """👋 Добро пожаловать в группу RoboSTEAMuL!

Здесь вы найдете:
🤖 Обновления о роботике
💡 Полезные советы и уроки
📚 Документацию и примеры кода
🎯 Новости проектов

Спасибо, что присоединились! 🚀"""
        
        self.send_message(user_id, greeting_text)
    
    def start_listening(self):
        """Запустить слушание событий"""
        print("🚀 Бот запущен и ожидает новых подписчиков...")
        
        for event in self.longpoll.listen():
            if event.type == Event.USER_SUBSCRIBED:
                user_id = event.user_id
                print(f"📌 Новый подписчик: {user_id}")
                self.greet_subscriber(user_id)

# Запуск
if __name__ == "__main__":
    greeter = SubscriberGreeter(VK_TOKEN, GROUP_ID)
    greeter.start_listening()
