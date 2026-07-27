"""
РобоСТЕАМ Bot v3.2 - УЛУЧШЕННАЯ ВЕРСИЯ
Высокое качество ответов, контекстный анализ, умные рекомендации
БЕЗ СТОРОННИХ СЕРВИСОВ - только внутренние улучшения!

Автор улучшений: Claude
Дата: 2024
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json

# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: АНАЛИЗ НАСТРОЕНИЯ И КОНТЕКСТА ПОЛЬЗОВАТЕЛЯ
# ════════════════════════════════════════════════════════════════════════════

class UserMood(Enum):
    """Определенное настроение пользователя"""
    CONFUSED = "confused"        # Запутался
    FRUSTRATED = "frustrated"    # Раздражен
    CURIOUS = "curious"          # Заинтересован
    CALM = "calm"                # Спокоен
    EXCITED = "excited"          # Воодушевлен
    NEUTRAL = "neutral"          # Нейтрален


class UserContext:
    """
    Контекст пользователя - полная история и анализ
    НОВОЕ в v3.2: Умная память о пользователе
    """
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.dialog_history: List[Dict] = []
        self.error_count = 0
        self.successful_steps = 0
        self.last_interaction = datetime.now()
        self.detected_interests: List[str] = []
        self.user_mood = UserMood.NEUTRAL
        self.preferred_response_style = "friendly"  # friendly | formal | brief
        self.is_first_time = True
        self.confusion_detected = False
        self.help_requests = 0
        
    def add_message(self, role: str, content: str, field: str = None):
        """Добавить сообщение в историю"""
        self.dialog_history.append({
            'timestamp': datetime.now(),
            'role': role,  # user | bot
            'content': content,
            'field': field  # на каком шаге
        })
        self.last_interaction = datetime.now()
    
    def detect_user_mood(self) -> UserMood:
        """
        Определить настроение пользователя по истории
        НОВОЕ в v3.2: Анализ эмоционального состояния
        """
        if not self.dialog_history:
            return UserMood.NEUTRAL
        
        recent_messages = self.dialog_history[-3:]
        user_messages = [m for m in recent_messages if m['role'] == 'user']
        
        frustrated_indicators = ['не', 'не могу', 'сложно', 'не понимаю', '?????', 'что']
        curious_indicators = ['интересно', 'как', 'почему', 'расскажи', 'подробнее']
        excited_indicators = ['да!', 'отлично', 'супер', '!!!', 'круто', 'спасибо']
        confused_indicators = ['?', 'что это', 'не разобрал', 'еще раз', 'повтори']
        
        mood_scores = {
            UserMood.FRUSTRATED: 0,
            UserMood.CURIOUS: 0,
            UserMood.EXCITED: 0,
            UserMood.CONFUSED: 0,
            UserMood.CALM: 0
        }
        
        for msg in user_messages:
            text = msg['content'].lower()
            if any(ind in text for ind in frustrated_indicators):
                mood_scores[UserMood.FRUSTRATED] += 1
            if any(ind in text for ind in curious_indicators):
                mood_scores[UserMood.CURIOUS] += 1
            if any(ind in text for ind in excited_indicators):
                mood_scores[UserMood.EXCITED] += 1
            if any(ind in text for ind in confused_indicators):
                mood_scores[UserMood.CONFUSED] += 1
        
        # Если много ошибок - скорее всего запутался
        if self.error_count > 2:
            mood_scores[UserMood.CONFUSED] += 2
        
        # Определить самое высокое настроение
        if all(v == 0 for v in mood_scores.values()):
            return UserMood.NEUTRAL
        
        self.user_mood = max(mood_scores.items(), key=lambda x: x[1])[0]
        return self.user_mood
    
    def record_error(self, field: str, value: str):
        """Записать ошибку"""
        self.error_count += 1
        self.add_message('system', f'Error: {value}', field)
        self.confusion_detected = self.error_count > 1
    
    def record_success(self, field: str, value: str):
        """Записать успешный ввод"""
        self.successful_steps += 1
        self.add_message('system', f'Success: {value}', field)
        # Немного снизить ошибки при успехе
        if self.error_count > 0:
            self.error_count -= 1
    
    def extract_interests(self) -> List[str]:
        """
        Извлечь интересы пользователя из истории
        НОВОЕ в v3.2: Умное обнаружение интересов
        """
        if self.detected_interests:
            return self.detected_interests
        
        interests_keywords = {
            'танец': ['танец', 'хореография', 'ритм', 'движение', 'танцы'],
            'робо': ['робот', 'робототехника', 'конструирование', 'лего', 'строить'],
            'речь': ['речь', 'логопед', 'слова', 'говорить', 'произношение'],
            'школа': ['школа', 'подготовка', 'учеба', 'знания', 'буквы'],
        }
        
        for msg in self.dialog_history:
            if msg['role'] == 'user':
                text = msg['content'].lower()
                for interest, keywords in interests_keywords.items():
                    if any(kw in text for kw in keywords):
                        if interest not in self.detected_interests:
                            self.detected_interests.append(interest)
        
        return self.detected_interests
    
    def should_offer_help(self) -> bool:
        """Нужно ли предложить помощь?"""
        # Если ошибок больше чем успехов - значит запутался
        if self.error_count > self.successful_steps:
            return True
        
        # Если долго ничего не происходит
        if (datetime.now() - self.last_interaction).total_seconds() > 60:
            return True
        
        # Если много запросов помощи
        if self.help_requests > 2:
            return True
        
        return False


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: УМНЫЙ АНАЛИЗ НАМЕРЕНИЙ
# ════════════════════════════════════════════════════════════════════════════

class IntentAnalyzer:
    """
    Анализ истинного намерения пользователя
    НОВОЕ в v3.2: Контекстное понимание
    """
    
    @staticmethod
    def analyze(text: str, context: UserContext) -> Dict:
        """
        Анализировать свободный текст пользователя
        Возвращает: {'intent': str, 'confidence': float, 'entities': dict}
        """
        text_lower = text.lower().strip()
        
        # Простые намерения
        simple_intents = {
            'start_registration': ['запис', 'хочу запис', 'запись', 'регистр'],
            'get_help': ['помощь', 'помоги', 'не понимаю', 'помогите', 'как это'],
            'get_info': ['расскажи', 'информация', 'подробнее', 'что это', 'как'],
            'show_programs': ['программ', 'направления', 'что у вас есть'],
            'cancel': ['отмена', 'выход', 'не хочу', 'стоп', 'хватит'],
            'back': ['назад', 'назад!', 'вернуться', '<<<'],
        }
        
        for intent, keywords in simple_intents.items():
            if any(kw in text_lower for kw in keywords):
                return {
                    'intent': intent,
                    'confidence': 0.9,
                    'entities': {}
                }
        
        # Сложное распознавание: возраст
        import re
        age_match = re.search(r'(\d+)\s*(?:год|лет|года)', text)
        if age_match:
            age = int(age_match.group(1))
            if 2 <= age <= 12:
                return {
                    'intent': 'provide_age',
                    'confidence': 0.95,
                    'entities': {'age': age}
                }
        
        # Если много вопросов - user запутался
        if text.count('?') > 1:
            return {
                'intent': 'confusion_detected',
                'confidence': 0.7,
                'entities': {}
            }
        
        # Default: обычное сообщение
        return {
            'intent': 'generic_message',
            'confidence': 0.5,
            'entities': {}
        }


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: УМНЫЙ РЕКОМЕНДАТОР ПРОГРАММ
# ════════════════════════════════════════════════════════════════════════════

class SmartRecommender:
    """
    Умные рекомендации программ
    НОВОЕ в v3.2: Анализ интересов и особенностей
    """
    
    @staticmethod
    def calculate_program_fit(
        age: int, 
        interests: List[str],
        programs: Dict,
        context: UserContext
    ) -> List[Tuple[str, float, str]]:
        """
        Рассчитать подходящие программы с обоснованием
        Возвращает: [(program_code, score, reason), ...]
        """
        recommendations = []
        
        for code, program in programs.items():
            score = 0.0
            reasons = []
            
            # Проверка по возрасту
            if program['age_min'] <= age <= program['age_max']:
                score += 40
                reasons.append(f"подходит по возрасту {age} лет")
            elif program['age_min'] <= age <= program['age_max'] + 1:
                score += 20
                reasons.append(f"подходит для возраста чуть старше")
            
            # Проверка по интересам
            if 'танец' in interests and 'dance' in code.lower():
                score += 30
                reasons.append("совпадает с интересом к танцам")
            if 'робо' in interests and ('robot' in code.lower() or 'robo' in code.lower()):
                score += 30
                reasons.append("совпадает с интересом к робототехнике")
            if 'речь' in interests and 'logoped' in code.lower():
                score += 30
                reasons.append("совпадает с интересом к развитию речи")
            if 'школа' in interests and 'school' in code.lower():
                score += 30
                reasons.append("совпадает с интересом к подготовке")
            
            # Первый раз? Рекомендуем популярные
            if context.is_first_time and code in ['robo_stim', 'brick', 'dance']:
                score += 10
                reasons.append("популярная программа для начинающих")
            
            if score > 0:
                reason = " • ".join(reasons)
                recommendations.append((code, score, reason))
        
        # Отсортировать поScore
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: УМНАЯ ОБРАБОТКА ОШИБОК
# ════════════════════════════════════════════════════════════════════════════

class SmartErrorHandler:
    """
    Умная обработка ошибок ввода
    НОВОЕ в v3.2: Помощь вместо критики
    """
    
    @staticmethod
    def handle_age_error(value: str, user_age: Optional[int] = None) -> str:
        """Помощь при ошибке ввода возраста"""
        
        # Попытка извлечь число
        import re
        match = re.search(r'\d+', value)
        
        if match:
            attempted_age = int(match.group())
            if attempted_age < 2:
                return f"""❓ Малыш еще очень маленький ({attempted_age} года).
К сожалению, наши программы начинаются с 3 лет.

💡 Подождите чуть-чуть! 🎂 
За полгода-год ребенок подрастет, и тогда можно начать занятия!

Или может быть вы опечатались? 😊"""
            elif attempted_age > 12:
                return f"""❓ Отлично, что ваш ребенок уже {attempted_age} лет!

К сожалению, наша программа для детей до 12 лет.
Для ребенка старшего возраста рекомендуем позвонить Наталье:
📞 +7 (922) 014-44-94

Она подберет что-то подходящее! 😊"""
        
        return """❓ Кажется, я не разобрал возраст.

💡 Напишите просто цифру:
   • 3 или 4 или 5
   • три или четыре
   • '3 года' или '4 года'

Я поймаю любой формат! 😊"""
    
    @staticmethod
    def handle_phone_error(value: str, last_error: Optional[str] = None) -> str:
        """Помощь при ошибке в телефоне"""
        
        if last_error == "too_short":
            return """📞 Кажется, номер получился коротковатым.

Для России обычно 10-11 цифр:
   ✅ Правильно: +7 (921) 123-45-67
   ✅ Или так: 8-921-123-45-67
   ✅ Или просто: 89211234567

💡 Совет: скопируйте номер из телефона - так точнее! 📱

Напишите номер еще раз:"""
        
        return """📞 Проверьте номер телефона.

Нам нужно 10-11 цифр для России:
   ✅ +7 900 123-45-67
   ✅ 8-921-123-45-67  
   ✅ 89211234567

❌ Неправильно: текст, спецсимволы кроме (+, -, пробел)

💡 Если затрудняетесь - позвоните в офис:
📞 +7 (922) 014-44-94 (Наталья)

Давайте еще раз? 😊"""
    
    @staticmethod
    def handle_name_error(value: str) -> str:
        """Помощь при ошибке в ФИО"""
        
        return f"""❓ С ФИО что-то не то: '{value}'

Используйте только буквы и дефисы, без цифр:
   ✅ Правильно: Петров Иван
   ✅ Правильно: Сидорова-Петрова Мария
   
   ❌ Неправильно: Петров123, Ivan, $$$

💡 Напишите ФИО как в свидетельстве о рождении.
Отчество (3-е слово) - необязательно!

Попробуем еще раз? 😊"""


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: КРАСИВОЕ ФОРМАТИРОВАНИЕ СООБЩЕНИЙ
# ════════════════════════════════════════════════════════════════════════════

class MessageFormatter:
    """
    Красивое и понятное форматирование сообщений
    НОВОЕ в v3.2: Профессиональный стиль
    """
    
    @staticmethod
    def format_welcome(user_name: Optional[str] = None) -> str:
        """Приветствие"""
        greeting = "Привет" if not user_name else f"Привет, {user_name.split()[0]}"
        
        return f"""{greeting}! 👋

Я помощник RoboSTEAMuL. 🤖

Помогу вам:
   🎯 Подобрать идеальную программу по возрасту
   📋 Оформить запись ребенка
   💬 Ответить на все вопросы

Что вас интересует?

   📝 Записать ребенка
   🎨 Узнать о направлениях
   ❓ Задать вопрос
   📞 Контакты"""
    
    @staticmethod
    def format_program_recommendation(
        program_code: str,
        program: Dict,
        age: int,
        reasons: str
    ) -> str:
        """Красиво отформатировать рекомендацию программы"""
        
        emoji = program.get('emoji', '✨')
        
        return f"""⭐ {emoji} {program['name'].upper()}

💡 Почему эта программа идеальна?
   {reasons}

📊 Что вы получите:
   ✓ {program['description']}
   ✓ Возраст: {program['age_min']}-{program['age_max']} лет
   ✓ Цена: {program['price']}/занятие
   ✓ Группы до 8 детей
   ✓ Первое занятие БЕСПЛАТНО! 🎁

📞 Вопросы? Позвоните Наталье: +7 (922) 014-44-94

➡️ Выбираете эту программу? 😊"""
    
    @staticmethod
    def format_help_message(context: UserContext) -> str:
        """Предложить помощь"""
        
        mood_emoji = {
            'confused': '🤔',
            'frustrated': '😟',
            'neutral': '😊',
            'curious': '👀',
        }
        
        emoji = mood_emoji.get(context.user_mood.value, '😊')
        
        return f"""{emoji} Кажется, вы затруднились?

Не беда! Я здесь, чтобы помочь:

💡 Вот что я могу сделать:
   • Повторить вопрос другими словами
   • Привести больше примеров
   • Объяснить зачем нужна информация
   • Позвать Наталью (живого человека!)

❓ Что вам нужно помощь?

   1️⃣ Еще примеры правильного ввода
   2️⃣ Объяснить вопрос подробнее
   3️⃣ Позвонить Наталье: +7 (922) 014-44-94
   4️⃣ Начать заново"""


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ИНТЕЛЛЕКТУАЛЬНЫЕ ПОДСКАЗКИ
# ════════════════════════════════════════════════════════════════════════════

def should_provide_hint(context: UserContext, field: str) -> bool:
    """Нужно ли показать подсказку на этом шаге?"""
    
    # На третьей ошибке точно показать подсказку
    if context.error_count >= 3:
        return True
    
    # Если пользователь запутался
    if context.confusion_detected:
        return True
    
    # Если много помощи запросил
    if context.help_requests > 1:
        return True
    
    return False


def generate_intelligent_hint(field: str, user_input: str) -> str:
    """
    Умная подсказка на основе ошибки
    НОВОЕ в v3.2: Контекстные подсказки
    """
    
    hints = {
        'child_fio': """💡 ФИО - это как в свидетельстве о рождении:
   • Фамилия (Петров)
   • Имя (Иван)
   • Отчество (Сергеевич) - необязательно
   
Примеры:
   ✅ Петров Иван
   ✅ Сидорова Мария Ивановна""",
        
        'child_age': """💡 Возраст - просто цифра:
   ✅ 3
   ✅ пять
   ✅ '4 года'
   
Наши программы для детей 3-12 лет.""",
        
        'kindergarten_number': """💡 Номер сада - это цифры:
   ✅ 30
   ✅ №30
   ✅ 30 СП
   ✅ Нет (если не ходит)""",
        
        'parent_phone': """💡 Телефон - 10-11 цифр:
   ✅ +7 900 123-45-67
   ✅ 89211234567
   
Не забудьте код страны/оператора!""",
    }
    
    return hints.get(field, "💡 Попробуйте еще раз. Я верю, что у вас получится! 😊")


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ: ОТСЛЕЖИВАНИЕ ВЗАИМОДЕЙСТВИЯ
# ════════════════════════════════════════════════════════════════════════════

class InteractionAnalytics:
    """
    Аналитика взаимодействия (только локально, не отправляем никуда)
    НОВОЕ в v3.2: Обучение на основе ошибок
    """
    
    def __init__(self):
        self.session_data = {}
    
    def track_step(self, user_id: int, step: str, success: bool, time_spent: float):
        """Отследить прохождение шага"""
        if user_id not in self.session_data:
            self.session_data[user_id] = []
        
        self.session_data[user_id].append({
            'step': step,
            'success': success,
            'time_spent': time_spent,
            'timestamp': datetime.now()
        })
    
    def get_hardest_step(self) -> Optional[str]:
        """Найти самый сложный шаг для пользователя"""
        if not self.session_data:
            return None
        
        step_stats = {}
        for user_steps in self.session_data.values():
            for record in user_steps:
                step = record['step']
                if step not in step_stats:
                    step_stats[step] = {'errors': 0, 'total': 0}
                
                step_stats[step]['total'] += 1
                if not record['success']:
                    step_stats[step]['errors'] += 1
        
        if not step_stats:
            return None
        
        # Найти шаг с максимальным процентом ошибок
        hardest = max(
            step_stats.items(),
            key=lambda x: x[1]['errors'] / max(x[1]['total'], 1)
        )
        
        return hardest[0]
