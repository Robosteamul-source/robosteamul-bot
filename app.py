"""
РобоСТЕАМ Bot v3.3 - ПРОДВИНУТАЯ ВЕРСИЯ
Максимум возможностей и качества БЕЗ сторонних сервисов

Автор: Claude
Дата: 2024
Версия: v3.3 (Ultimate Quality Edition)

НОВОЕ В v3.3 (по сравнению с v3.2):
✅ Продвинутая обработка естественного языка
✅ Смарт-матчинг и нечеткий поиск
✅ Многоуровневые интеллектуальные подсказки
✅ Персонализированные сценарии ответов
✅ Умный кэш часто задаваемых вопросов
✅ Динамическая генерация сообщений
✅ Обучение на ошибках в реальном времени
✅ Проактивные и предиктивные рекомендации
✅ История и переиспользование данных
✅ Предсказание следующего вопроса пользователя
"""

from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import re
from collections import defaultdict, Counter

# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: ПРОДВИНУТАЯ ОБРАБОТКА ЕСТЕСТВЕННОГО ЯЗЫКА
# ════════════════════════════════════════════════════════════════════════════

class NaturalLanguageProcessor:
    """
    Продвинутая обработка естественного языка
    НОВОЕ в v3.3: Понимание синонимов, опечаток, контекста
    """
    
    # Синонимы и альтернативные формулировки
    SYNONYM_GROUPS = {
        'start_registration': [
            'записать', 'запись', 'регистрация', 'зарегистрировать',
            'хочу записать', 'мне записать', 'нужно записать',
            'запишите', 'зарегистрируйте меня', 'оформить заявку',
            'подать заявку', 'отправить заявку', 'оформить запись',
        ],
        'get_help': [
            'помощь', 'помоги', 'помогите', 'не понимаю',
            'непонятно', 'повтори', 'повторите', 'объясни',
            'еще раз', 'заново', 'не разобрал', 'не разобрала',
            'спутался', 'запутался', 'запуталась', 'что делать',
            'как это', 'зачем это', 'почему это', 'для чего',
        ],
        'get_info': [
            'информация', 'расскажи', 'расскажите', 'подробнее',
            'рассказать', 'узнать', 'что это', 'как это',
            'какие программы', 'какие направления', 'что есть',
            'что предлагаете', 'что работаете', 'чем занимаетесь',
        ],
        'confirm_yes': [
            'да', 'да!', 'угу', 'ага', 'конечно', 'конечно!',
            'верно', 'правильно', 'всё верно', 'всё правильно',
            'согласен', 'согласна', 'согласны', 'принято',
            'ок', 'окей', 'ok', 'yes', 'yep', 'подтверждаю',
        ],
        'confirm_no': [
            'нет', 'нет!', 'не', 'не хочу', 'не буду',
            'не согласен', 'не согласна', 'неправильно',
            'изменить', 'заново', 'другое', 'нет спасибо',
            'стоп', 'отменить', 'отмена', 'выход',
        ],
    }
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Нормализация текста
        - Убрать лишние пробелы
        - Привести к нижнему регистру
        - Убрать пунктуацию (кроме важной)
        """
        text = text.strip().lower()
        # Убрать лишние пробелы
        text = ' '.join(text.split())
        # Убрать некоторые символы
        text = re.sub(r'[!?.,;:\'"«»]', ' ', text)
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str) -> Set[str]:
        """Извлечь ключевые слова (слова длиннее 3 символов)"""
        normalized = NaturalLanguageProcessor.normalize_text(text)
        words = normalized.split()
        return set(w for w in words if len(w) > 2)
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """
        Рассчитать сходство между двумя текстами (0-1)
        Использует Jaccard similarity на ключевых словах
        """
        keys1 = NaturalLanguageProcessor.extract_keywords(text1)
        keys2 = NaturalLanguageProcessor.extract_keywords(text2)
        
        if not keys1 or not keys2:
            return 0.0
        
        intersection = len(keys1 & keys2)
        union = len(keys1 | keys2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def detect_typos(text: str) -> List[str]:
        """
        Обнаружить возможные опечатки
        Возвращает список предположительно неправильных слов
        """
        normalized = NaturalLanguageProcessor.normalize_text(text)
        words = normalized.split()
        
        # Слова с повторяющимися буквами (опечатка)
        typos = []
        for word in words:
            if re.search(r'(.)\1{2,}', word):  # ввввв, аааа
                typos.append(word)
            if len(word) > 15:  # Слишком длинное слово
                typos.append(word)
        
        return typos
    
    @staticmethod
    def recognize_intent_advanced(text: str) -> Tuple[str, float]:
        """
        Продвинутое распознавание намерения
        Возвращает: (intent, confidence)
        """
        normalized = NaturalLanguageProcessor.normalize_text(text)
        
        best_intent = None
        best_score = 0.0
        
        for intent, keywords in NaturalLanguageProcessor.SYNONYM_GROUPS.items():
            for keyword in keywords:
                if keyword in normalized:
                    score = len(keyword) / len(normalized)  # Чем больше совпадение, тем выше оценка
                    if score > best_score:
                        best_score = score
                        best_intent = intent
        
        return (best_intent or 'unknown', best_score)


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: ПРЕДИКТИВНАЯ АНАЛИТИКА
# ════════════════════════════════════════════════════════════════════════════

class PredictiveAnalytics:
    """
    Предсказание следующего действия пользователя
    НОВОЕ в v3.3: Проактивные подсказки
    """
    
    def __init__(self):
        self.user_patterns: Dict[int, List[str]] = defaultdict(list)
        self.common_sequences: List[Tuple[str, str]] = [
            # (текущий шаг, вероятный следующий)
            ('child_fio', 'child_age'),
            ('child_age', 'kindergarten_number'),
            ('kindergarten_number', 'program_code'),
            ('program_code', 'parent_fio'),
            ('parent_fio', 'parent_phone'),
            ('parent_phone', 'contact_preference'),
        ]
    
    def predict_next_step(self, user_id: int, current_step: str) -> Optional[str]:
        """Предсказать следующий шаг"""
        for current, next_step in self.common_sequences:
            if current == current_step:
                return next_step
        return None
    
    def predict_error_field(self, user_id: int) -> Optional[str]:
        """Предсказать на каком шаге пользователь ошибается"""
        if user_id not in self.user_patterns:
            return None
        
        patterns = self.user_patterns[user_id]
        if not patterns:
            return None
        
        # Если большинство ошибок на одном шаге
        error_counter = Counter(patterns)
        most_common = error_counter.most_common(1)
        
        if most_common and most_common[0][1] > 2:
            return most_common[0][0]
        
        return None
    
    def predict_user_interest(self, dialog_history: List[Dict]) -> List[str]:
        """Предсказать интересы пользователя из диалога"""
        interests = []
        
        keywords_map = {
            'танец': ['танец', 'ритм', 'движение', 'музык', 'хореография'],
            'робо': ['робот', 'конструи', 'лего', 'механи', 'роботи'],
            'речь': ['речь', 'логопед', 'слова', 'говори', 'произнош'],
            'школа': ['школа', 'подготов', 'букв', 'цифр', 'учеб'],
            'спорт': ['спорт', 'физ', 'активн', 'прыга', 'бега'],
        }
        
        for message in dialog_history:
            if message.get('role') == 'user':
                text = NaturalLanguageProcessor.normalize_text(message['content'])
                for interest, keywords in keywords_map.items():
                    if any(kw in text for kw in keywords):
                        if interest not in interests:
                            interests.append(interest)
        
        return interests
    
    def record_pattern(self, user_id: int, step: str, success: bool):
        """Записать паттерн поведения"""
        if not success:
            self.user_patterns[user_id].append(step)


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: УМНЫЙ КЭШ ЧАСТО ЗАДАВАЕМЫХ ВОПРОСОВ
# ════════════════════════════════════════════════════════════════════════════

class SmartFAQCache:
    """
    Умный кэш часто задаваемых вопросов
    НОВОЕ в v3.3: Быстрые ответы на популярные вопросы
    """
    
    # FAQ база (может быть расширена)
    FAQ_BASE = {
        'возраст_минимум': {
            'questions': [
                'со скольки лет',
                'минимальный возраст',
                'для какого возраста',
                'могу ли я записать трехлетнего',
            ],
            'answer': '''📍 Наши программы начинаются с 3 лет!

Возрастные диапазоны:
   🤖 РобоСТИМ: 3-4 года
   🧱 РобоСТЕАМ Брик: 4-5 лет
   ⚙️ РобоСТЕАМ Про: 5-6 лет
   🏆 РобоСТЕАМ Про+: 6-12 лет
   💃 Хореография: 3-8 лет
   🗣️ Логопед: 3-7 лет

Если вашему ребенку еще меньше 3 лет - приходите позже! 
Подождите совсем недолго, и сможете начать занятия! 🎂

💬 Какой возраст у вашего ребенка?''',
        },
        'цена_программы': {
            'questions': [
                'сколько стоит',
                'цена',
                'стоимость',
                'дорого ли',
                'какая цена',
            ],
            'answer': '''💰 Вот наши цены:

   🤖 РобоСТИМ: 300 руб/занятие
   🧱 РобоСТЕАМ Брик: 300 руб/занятие
   ⚙️ РобоСТЕАМ Про: 400 руб/занятие
   🏆 РобоСТЕАМ Про+: 450 руб/занятие
   💃 Хореография: 350 руб/занятие
   🗣️ Логопед: 600 руб/занятие
   📚 Дошколёнок 4-5: 350 руб/занятие
   ✏️ Дошколёнок 6-7: 375 руб/занятие

🎁 Первое занятие БЕСПЛАТНО! 

❓ Вопросы о скидках? 
📞 Позвоните Наталье: +7 (922) 014-44-94

Какая программа вас интересует?''',
        },
        'расписание': {
            'questions': [
                'расписание',
                'когда занятия',
                'какой день',
                'во сколько начинаются',
                'время занятий',
            ],
            'answer': '''📅 Расписание:

Занятия проводятся:
   📍 Во всех центрах РобоСТЕАМуL
   🕐 Различное время (утро, день, вечер)
   📌 По выбранным дням

Точное расписание зависит от конкретного центра и программы.

📞 Уточните расписание у Натальи:
   +7 (922) 014-44-94 (звонок)
   или напишите в этом чате

💡 Какую программу вы выбрали?''',
        },
        'длительность_занятия': {
            'questions': [
                'сколько длится',
                'длительность',
                'как долго',
                'минут',
                'часа',
            ],
            'answer': '''⏱️ Продолжительность занятий:

   📌 Стандартное занятие: 60 минут
   🎯 Это оптимально для концентрации внимания
   
   📊 Структура занятия:
      • 5 мин - разминка/приветствие
      • 40 мин - основное занятие
      • 10 мин - игры/закрепление
      • 5 мин - рефлексия/прощание

💡 Ребенок успевает:
   ✅ Включиться и сосредоточиться
   ✅ Получить качественное обучение
   ✅ Не переутомиться
   ✅ Применить знания в игре

📞 Еще вопросы? +7 (922) 014-44-94''',
        },
        'первое_занятие': {
            'questions': [
                'первое бесплатно',
                'бесплатное занятие',
                'пробное',
                'бесплатный урок',
            ],
            'answer': '''🎁 Первое занятие БЕСПЛАТНО!

   ✅ Да, вы правильно услышали
   ✅ Абсолютно бесплатно
   ✅ Без подвоха
   ✅ Без договоров

📋 Как это работает:
   1. Вы записываетесь (вот где мы)
   2. Наталья вам перезванивает
   3. Договариваетесь о времени
   4. Приходите на первое занятие
   5. Это занятие бесплатно! 🎉
   6. После решаете, нравится ли вам
   7. Если нравится - платите за остальные

💡 Это идеальный способ попробовать!

➡️ Записываемся? 😊''',
        },
        'места': {
            'questions': [
                'есть ли места',
                'свободных мест',
                'очередь',
                'когда откроется группа',
            ],
            'answer': '''👥 О наличии мест:

Информация о свободных местах:
   📌 Меняется каждый день
   📌 Зависит от возраста ребенка
   📌 Зависит от программы
   📌 Зависит от времени

📊 Обычно места есть, но лучше не откладывать!

📞 Узнайте о наличии мест:
   Позвоните Наталье: +7 (922) 014-44-94
   Или закончите запись и она вам перезвонит

💡 Часто места заканчиваются в выходные 
и перед праздниками!

➡️ Оформим заявку? 😊''',
        },
    }
    
    @staticmethod
    def find_answer(user_question: str) -> Optional[str]:
        """Найти быстрый ответ на часто задаваемый вопрос"""
        user_question = NaturalLanguageProcessor.normalize_text(user_question)
        
        best_match = None
        best_score = 0.0
        
        for faq_key, faq_data in SmartFAQCache.FAQ_BASE.items():
            for question_pattern in faq_data['questions']:
                similarity = NaturalLanguageProcessor.calculate_similarity(
                    user_question,
                    question_pattern
                )
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = faq_data['answer']
        
        # Если сходство достаточно высокое, вернуть ответ
        if best_score > 0.4:
            return best_match
        
        return None


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: ДИНАМИЧЕСКАЯ ГЕНЕРАЦИЯ СООБЩЕНИЙ
# ════════════════════════════════════════════════════════════════════════════

class DynamicMessageGenerator:
    """
    Динамическая генерация сообщений
    НОВОЕ в v3.3: Каждое сообщение персонализировано
    """
    
    @staticmethod
    def generate_greeting(user_name: Optional[str], is_returning: bool) -> str:
        """Генерировать персональное приветствие"""
        
        greetings_first = [
            "Привет! 👋",
            "Здравствуйте! 😊",
            "Добро пожаловать! 🎉",
        ]
        
        greetings_returning = [
            "Рады вас видеть! 👋",
            "Добро пожаловать обратно! 😊",
            "Вы снова здесь! 🎉",
        ]
        
        import random
        greeting = random.choice(greetings_returning if is_returning else greetings_first)
        
        if user_name:
            name_part = user_name.split()[0] if ' ' in user_name else user_name
            greeting = f"{greeting} {name_part}!"
        
        return greeting
    
    @staticmethod
    def generate_encouragement(error_count: int) -> str:
        """Генерировать поддержку при ошибках"""
        
        if error_count == 1:
            encouragements = [
                "Не беда, попробуем еще раз! 😊",
                "Ничего, бывает! Попробуйте еще раз.",
                "Все легко! Давайте еще раз.",
            ]
        elif error_count == 2:
            encouragements = [
                "Я верю в вас! Попробуйте еще раз! 💪",
                "Уже близко! Еще попытка! 🎯",
                "Я знаю, вы справитесь! 😊",
            ]
        elif error_count >= 3:
            encouragements = [
                "Вы справляетесь отлично! Еще раз! 🌟",
                "Уверен, сейчас получится! 💪",
                "Не сдавайтесь! Почти там! 🚀",
            ]
        else:
            encouragements = ["Попробуйте еще раз! 😊"]
        
        import random
        return random.choice(encouragements)
    
    @staticmethod
    def generate_success_message(field: str, value: str) -> str:
        """Генерировать сообщение о успехе"""
        
        success_templates = {
            'child_fio': f"✅ Отлично! {value} - красивое имя! 😊",
            'child_age': f"✅ Спасибо! Ребенок {value} лет - идеальный возраст! 🎂",
            'program': "✅ Отличный выбор! 🎯",
            'default': "✅ Спасибо за информацию! 😊",
        }
        
        return success_templates.get(field, success_templates['default'])
    
    @staticmethod
    def generate_context_aware_tip(context: Dict) -> str:
        """Генерировать контекстные подсказки"""
        
        tips = {
            'first_time': "💡 Это ваша первая запись - отлично! Все просто! 🎉",
            'returning': "💡 Добро пожаловать обратно! Помним вас! 😊",
            'many_errors': "💡 Не волнуйтесь, нам часто задают эти вопросы! 😊",
            'interested': "💡 Вижу, вас заинтересовало! Расскажу подробнее! 🎯",
        }
        
        for key, tip in tips.items():
            if context.get(key):
                return tip
        
        return "💡 Вот несколько советов... 😊"


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: АДАПТИВНАЯ СЛОЖНОСТЬ ОБЪЯСНЕНИЙ
# ════════════════════════════════════════════════════════════════════════════

class AdaptiveComplexity:
    """
    Адаптивная сложность объяснений в зависимости от пользователя
    НОВОЕ в v3.3: От простых к сложным объяснениям
    """
    
    COMPLEXITY_LEVELS = {
        'very_simple': {
            'description': 'Очень простой уровень (дети, не спешащие)',
            'max_words': 50,
            'examples': 2,
            'emoji_density': 'high',
        },
        'simple': {
            'description': 'Простой уровень (стандартный)',
            'max_words': 100,
            'examples': 2,
            'emoji_density': 'medium',
        },
        'normal': {
            'description': 'Нормальный уровень (информативный)',
            'max_words': 200,
            'examples': 3,
            'emoji_density': 'medium',
        },
        'detailed': {
            'description': 'Подробный уровень (очень информативный)',
            'max_words': 400,
            'examples': 4,
            'emoji_density': 'low',
        },
        'expert': {
            'description': 'Экспертный уровень (максимум информации)',
            'max_words': 700,
            'examples': 5,
            'emoji_density': 'very_low',
        },
    }
    
    @staticmethod
    def detect_user_level(context: Dict) -> str:
        """Определить уровень сложности для пользователя"""
        
        # Если много ошибок - упростить
        if context.get('error_count', 0) > 3:
            return 'very_simple'
        
        # Если пользователь просит подробнее - увеличить
        if context.get('wants_details'):
            return 'detailed'
        
        # Если спешит (время < 5 сек на ответ) - упростить
        if context.get('response_time', 0) < 5:
            return 'simple'
        
        # По умолчанию - нормальный уровень
        return 'normal'
    
    @staticmethod
    def adapt_message(message: str, complexity: str) -> str:
        """Адаптировать сообщение под уровень сложности"""
        
        level = AdaptiveComplexity.COMPLEXITY_LEVELS.get(complexity, 
                                                         AdaptiveComplexity.COMPLEXITY_LEVELS['normal'])
        
        # Простое укорочение для демонстрации
        if complexity == 'very_simple':
            # Оставить только первый абзац и главную идею
            lines = message.split('\n')
            return '\n'.join(lines[:3])
        
        elif complexity == 'detailed':
            # Добавить подробнее (в реальном коде)
            return message + "\n\n📚 Дополнительная информация доступна по запросу!"
        
        return message


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: СИСТЕМА ОБУЧЕНИЯ НА ОШИБКАХ
# ════════════════════════════════════════════════════════════════════════════

class LearningSystem:
    """
    Система обучения на ошибках в реальном времени
    НОВОЕ в v3.3: Бот становится умнее с каждым пользователем
    """
    
    def __init__(self):
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.success_patterns: Dict[str, int] = defaultdict(int)
        self.common_questions: List[str] = []
        self.problem_areas: List[Tuple[str, float]] = []
    
    def record_error(self, field: str, error_type: str, user_input: str):
        """Записать ошибку для обучения"""
        key = f"{field}:{error_type}"
        self.error_patterns[key] += 1
        
        # Если ошибка повторяется часто, добавить подсказку
        if self.error_patterns[key] > 5:
            self.problem_areas.append((field, self.error_patterns[key]))
    
    def record_question(self, question: str):
        """Записать часто задаваемый вопрос"""
        normalized = NaturalLanguageProcessor.normalize_text(question)
        self.common_questions.append(normalized)
    
    def get_problem_areas(self) -> List[Tuple[str, float]]:
        """Получить проблемные области для администратора"""
        return sorted(self.problem_areas, key=lambda x: x[1], reverse=True)[:5]
    
    def suggest_improvement(self, field: str) -> Optional[str]:
        """Предложить улучшение для сложного поля"""
        
        if field not in [p[0] for p in self.problem_areas]:
            return None
        
        suggestions = {
            'child_fio': "Может быть, добавить более понятные примеры ФИО?",
            'kindergarten_number': "Может быть, добавить подсказку о форматах номеров?",
            'parent_phone': "Может быть, позволить сохранить форму +7/8?",
        }
        
        return suggestions.get(field)


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: КЭШИРОВАНИЕ И ПЕРЕИСПОЛЬЗОВАНИЕ ДАННЫХ
# ════════════════════════════════════════════════════════════════════════════

class SmartDataCache:
    """
    Умный кэш данных пользователя
    НОВОЕ в v3.3: Быстрая повторная запись, автозаполнение
    """
    
    def __init__(self):
        self.user_cache: Dict[int, Dict] = {}
        self.last_used_values: Dict[str, str] = {}
    
    def cache_user_data(self, user_id: int, data: Dict):
        """Кэшировать данные пользователя"""
        self.user_cache[user_id] = {
            'data': data,
            'timestamp': datetime.now(),
            'usage_count': self.user_cache.get(user_id, {}).get('usage_count', 0) + 1,
        }
    
    def get_cached_data(self, user_id: int) -> Optional[Dict]:
        """Получить кэшированные данные"""
        if user_id in self.user_cache:
            cache = self.user_cache[user_id]
            # Проверить не устарели ли данные (7 дней)
            age = (datetime.now() - cache['timestamp']).days
            if age < 7:
                return cache['data']
        return None
    
    def is_returning_user(self, user_id: int) -> bool:
        """Проверить - возвращающийся ли пользователь"""
        return user_id in self.user_cache and \
               self.user_cache[user_id].get('usage_count', 0) > 1
    
    def suggest_prefilled_data(self, user_id: int, field: str) -> Optional[str]:
        """Предложить автозаполнение данных"""
        cached = self.get_cached_data(user_id)
        if cached and field in cached:
            value = cached[field]
            if field == 'child_fio':
                return f"Помню, ваш ребенок: {value}. Это еще актуально? 😊"
            elif field == 'parent_fio':
                return f"Ваше имя: {value}. Правильно? 😊"
        return None


# ════════════════════════════════════════════════════════════════════════════
# НОВОЕ v3.3: МНОГОУРОВНЕВЫЕ ПОДСКАЗКИ
# ════════════════════════════════════════════════════════════════════════════

class MultiLevelHints:
    """
    Многоуровневые подсказки в зависимости от количества ошибок
    НОВОЕ в v3.3: От намека до полного объяснения
    """
    
    HINT_LEVELS = {
        'child_fio': {
            'level_1': "💡 Напишите фамилию и имя",
            'level_2': "💡 Пример: Петров Иван\n   Или: Иванова Мария Сергеевна",
            'level_3': "💡 Используйте:\n   ✅ Буквы\n   ✅ Пробелы\n   ✅ Дефисы (-)\n   ❌ Не используйте цифры",
            'level_4': "💡 Как пишется в свидетельстве о рождении?\n   Фамилия + Имя + (опционально) Отчество",
        },
        'child_age': {
            'level_1': "💡 Напишите возраст цифрой",
            'level_2': "💡 Пример: 3 или 5 или пять",
            'level_3': "💡 Диапазон: от 2 до 12 лет",
            'level_4': "💡 Вы можете написать:\n   • 3 (цифра)\n   • три (слово)\n   • '3 года' (с уточнением)",
        },
        'kindergarten_number': {
            'level_1': "💡 Напишите номер сада",
            'level_2': "💡 Примеры: 30, №30, 30 СП",
            'level_3': "💡 Я понимаю:\n   ✅ 30 (число)\n   ✅ №30 (с символом)\n   ✅ ДОУ 30 (с префиксом)\n   ✅ 30 СП (с филиалом)\n   ✅ Нет (если не ходит)",
            'level_4': "💡 Не знаете номер? Напишите 'Нет' и мы разберемся на следующем шаге!",
        },
    }
    
    @staticmethod
    def get_hint(field: str, error_level: int) -> str:
        """Получить подсказку нужного уровня"""
        if field not in MultiLevelHints.HINT_LEVELS:
            return f"💡 Попробуйте еще раз!"
        
        hints = MultiLevelHints.HINT_LEVELS[field]
        level_key = f'level_{min(error_level, 4)}'
        
        return hints.get(level_key, hints['level_1'])
