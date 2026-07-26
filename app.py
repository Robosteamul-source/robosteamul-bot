const express = require('express');
require('dotenv').config();

const app = express();
app.use(express.json());

// База знаний программ
const programs = [
  {
    id: 1,
    name: 'Робототехника РобоСТЕАМ',
    age: '3-4 года',
    price: 300,
    description: 'Первый уровень робототехники для самых маленьких'
  },
  {
    id: 2,
    name: 'Робототехника РобоСТЕАМ Брик',
    age: '5-6 лет',
    price: 300,
    description: 'Второй уровень с более сложными конструкциями'
  },
  {
    id: 3,
    name: 'Робототехника РобоСТЕАМ Про',
    age: '6-8 лет',
    price: 400,
    description: 'Продвинутый уровень робототехники'
  },
  {
    id: 4,
    name: 'Хореография',
    age: '3-8 лет',
    price: 350,
    description: 'Танцевальное развитие и физическая координация'
  },
  {
    id: 5,
    name: 'Логопед и развитие речи',
    age: '3-7 лет',
    price: 600,
    diagnostic: 800,
    description: 'Логопедические занятия и развитие речи (диагностика +800 ₽)'
  },
  {
    id: 6,
    name: 'Дошколёнок за два года до Школы',
    age: '4-5 лет',
    price: 350,
    description: 'Подготовка к школе для детей 4-5 лет'
  },
  {
    id: 7,
    name: 'Дошколёнок За год до Школы',
    age: '6-7 лет',
    price: 375,
    description: 'Интенсивная подготовка за год до школы'
  }
];

// Функция отправки сообщения в ВК
async function sendVKMessage(userId, message) {
  // ✅ ИСПРАВЛЕНО: Валидация параметров
  if (!userId || !message || !process.env.VK_TOKEN) {
    console.error('❌ Error: Missing required parameters for VK message');
    console.error(`   userId: ${userId}, message length: ${message?.length || 0}`);
    return false;
  }

  // ✅ ИСПРАВЛЕНО: Проверка максимальной длины сообщения (VK лимит ~4096 символов)
  if (message.length > 4096) {
    console.warn('⚠️  Warning: Message is too long, truncating...');
  }

  try {
    const params = new URLSearchParams();
    params.append('user_id', userId);
    params.append('message', message.substring(0, 4096)); // Обрезаем до лимита VK
    params.append('random_id', Math.floor(Math.random() * 2147483647));
    params.append('access_token', process.env.VK_TOKEN);
    params.append('v', '5.131');

    const response = await fetch('https://api.vk.com/method/messages.send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: params.toString()
    });

    if (!response.ok) {
      console.error(`❌ HTTP error! status: ${response.status}`);
      return false;
    }

    const data = await response.json();
    
    // ✅ ИСПРАВЛЕНО: Правильная обработка ошибок VK API
    if (data.error) {
      console.error('❌ VK API Error:', data.error.error_code, '-', data.error.error_msg);
      return false;
    }

    if (data.response) {
      console.log(`✅ Message sent successfully to user ${userId} (ID: ${data.response})`);
      return true;
    }
    
    console.warn('⚠️  Unexpected response from VK API:', data);
    return false;
  } catch (error) {
    console.error('❌ Error sending message:', error.message);
    return false;
  }
}

// ✅ ИСПРАВЛЕНО: Функция поиска программ по возрасту с обработкой ошибок
function findProgramsByAge(age) {
  // Валидация входных данных
  if (!age || isNaN(age)) {
    return [];
  }

  return programs.filter(program => {
    try {
      const ageParts = program.age.split('-').map(a => parseInt(a.trim()));
      
      if (ageParts.length === 2) {
        const [minAge, maxAge] = ageParts;
        return age >= minAge && age <= maxAge;
      }
      
      return false;
    } catch (error) {
      console.warn(`Error parsing age for program ${program.name}:`, error);
      return false;
    }
  });
}

// Функция генерации ответа
function generateResponse(text, userId) {
  if (!text) return '❓ Не получилось обработать сообщение. Попробуйте ещё раз.';
  
  const lowerText = text.toLowerCase().trim();
  let response = '';

  // Обработка разных типов запросов
  if (lowerText.includes('привет') || lowerText.includes('привет!') || lowerText.includes('начало')) {
    response = `👋 Добро пожаловать в консультацию по образовательным программам!\n\n` +
      `🎓 Я могу помочь вам с информацией о:\n` +
      `• Возрастных группах\n` +
      `• Ценах на занятия\n` +
      `• Описании программ\n\n` +
      `📝 Напишите:\n` +
      `"Мне 5 лет" - для подходящих программ\n` +
      `"Программы" - для списка всех программ\n` +
      `"Цены" - для информации о стоимости`;
  }
  
  else if (lowerText.includes('программ')) {
    response = '📚 Все наши образовательные программы:\n\n';
    programs.forEach((prog, index) => {
      response += `${index + 1}. ${prog.name}\n   Возраст: ${prog.age}\n   Цена: ${prog.price} ₽`;
      if (prog.diagnostic) {
        response += ` (диагностика +${prog.diagnostic} ₽)`;
      }
      response += '\n\n';
    });
  }
  
  else if (lowerText.includes('цен') || lowerText.includes('стоимост')) {
    response = '💰 Стоимость занятий:\n\n';
    const prices = {};
    programs.forEach(prog => {
      if (!prices[prog.price]) {
        prices[prog.price] = [];
      }
      prices[prog.price].push(prog.name);
    });
    
    Object.keys(prices).sort((a, b) => parseInt(a) - parseInt(b)).forEach(price => {
      response += `${price} ₽: ${prices[price].join(', ')}\n`;
    });
    
    response += '\n💡 Логопед и развитие речи: 600 ₽/занятие + 800 ₽ диагностика';
  }
  
  // ✅ ИСПРАВЛЕНО: Правильное соответствие возраста
  else if (/мне\s+(\d+)|(\d+)\s*(?:лет|год|года)/i.test(lowerText)) {
    const ageMatch = lowerText.match(/мне\s+(\d+)|(\d+)\s*(?:лет|год|года)/);
    if (ageMatch) {
      const age = parseInt(ageMatch[1] || ageMatch[2]);
      
      if (isNaN(age) || age < 1 || age > 18) {
        response = `❓ Пожалуйста, укажите корректный возраст (от 1 до 18 лет)`;
      } else {
        const suitable = findProgramsByAge(age);
        
        if (suitable.length > 0) {
          response = `✨ Программы для ${age} лет:\n\n`;
          suitable.forEach((prog, index) => {
            response += `${index + 1}. ${prog.name}\n   ${prog.description}\n   Цена: ${prog.price} ₽`;
            if (prog.diagnostic) {
              response += ` (+${prog.diagnostic} ₽ диагностика)`;
            }
            response += '\n\n';
          });
        } else {
          response = `❌ К сожалению, для возраста ${age} лет нет подходящих программ.\n\n` +
            `Наши программы рассчитаны на детей от 3 до 8 лет.`;
        }
      }
    }
  }
  
  else if (lowerText.includes('робот')) {
    const robotics = programs.filter(p => p.name.includes('Робототехника'));
    if (robotics.length > 0) {
      response = '🤖 Программы робототехники:\n\n';
      robotics.forEach(prog => {
        response += `${prog.name}\n   Возраст: ${prog.age}\n   Цена: ${prog.price} ₽\n\n`;
      });
    } else {
      response = '❌ К сожалению, программы робототехники временно недоступны.';
    }
  }
  
  else if (lowerText.includes('хореогра') || lowerText.includes('танц')) {
    const dance = programs.find(p => p.name.includes('Хореография'));
    if (dance) {
      response = `💃 ${dance.name}\n` +
        `Возраст: ${dance.age}\n` +
        `Цена: ${dance.price} ₽\n` +
        `Описание: ${dance.description}`;
    } else {
      response = '❌ К сожалению, программа хореографии временно недоступна.';
    }
  }
  
  else if (lowerText.includes('логопед') || lowerText.includes('речь')) {
    const speech = programs.find(p => p.name.includes('Логопед'));
    if (speech) {
      response = `🗣️ ${speech.name}\n` +
        `Возраст: ${speech.age}\n` +
        `Цена: ${speech.price} ₽\n` +
        `Диагностика: ${speech.diagnostic} ₽\n` +
        `Описание: ${speech.description}`;
    } else {
      response = '❌ К сожалению, услуга логопеда временно недоступна.';
    }
  }
  
  else if (lowerText.includes('дошколён') || lowerText.includes('школ')) {
    const preschool = programs.filter(p => p.name.includes('Дошколён'));
    if (preschool.length > 0) {
      response = '📖 Программы подготовки к школе:\n\n';
      preschool.forEach(prog => {
        response += `${prog.name}\n   Возраст: ${prog.age}\n   Цена: ${prog.price} ₽\n\n`;
      });
    } else {
      response = '❌ К сожалению, программы подготовки к школе временно недоступны.';
    }
  }
  
  else if (lowerText.includes('контакт') || lowerText.includes('запис')) {
    response = `📞 Свяжитесь с нами:\n\n` +
      `Напишите в личные сообщения группе или позвоните администратору для записи на интересующую программу.`;
  }
  
  else if (lowerText.includes('спас') || lowerText.includes('спасибо')) {
    response = `😊 Пожалуйста! Если у вас есть ещё вопросы о наших программах, я готов помочь!`;
  }
  
  else {
    response = `❓ Я - консультант по образовательным программам.\n\n` +
      `Вы можете спросить:\n` +
      `• "Мне 5 лет" - программы для вашего возраста\n` +
      `• "Программы" - полный список\n` +
      `• "Цены" - стоимость занятий\n` +
      `• "Робот", "Танцы", "Логопед", "Школа"\n\n` +
      `📝 Напишите один из этих запросов!`;
  }

  return response;
}

// Обработка Callback API
// ✅ ИСПРАВЛЕНО: Обработчик сделан асинхронным
app.post('/callback', async (req, res) => {
  try {
    const { type, object, secret } = req.body;

    // ✅ ИСПРАВЛЕНО: Проверка секрета
    if (!secret || secret !== process.env.VK_SECRET) {
      console.warn('⚠️  Invalid secret received - possible security threat');
      return res.send('ok'); // Отправляем 'ok' чтобы VK не повторял запрос
    }

    if (type === 'confirmation') {
      console.log('✅ VK Confirmation received and sent');
      return res.send(process.env.VK_CONFIRMATION);
    }

    if (type === 'message_new') {
      // ✅ ИСПРАВЛЕНО: Правильная деструктуризация объекта
      if (!object || !object.message) {
        console.warn('⚠️  Invalid message object structure');
        return res.send('ok');
      }

      const { message } = object;
      const { text, from_id } = message;

      // ✅ ИСПРАВЛЕНО: Валидация данных
      if (!text || !from_id) {
        console.warn('⚠️  Missing message text or from_id');
        return res.send('ok');
      }

      // Пропускаем сообщения от сообщества (ID <= 0)
      if (from_id <= 0) {
        console.log(`ℹ️  Skipping message from community/service (ID: ${from_id})`);
        return res.send('ok');
      }

      console.log(`📨 Incoming message from user ${from_id}: "${text.substring(0, 50)}${text.length > 50 ? '...' : ''}"`);

      const botResponse = generateResponse(text, from_id);
      
      // ✅ ИСПРАВЛЕНО: Ожидание результата асинхронной функции
      const sent = await sendVKMessage(from_id, botResponse);
      
      if (sent) {
        console.log(`✅ Response successfully processed for user ${from_id}`);
      } else {
        console.warn(`⚠️  Failed to send response to user ${from_id}`);
      }

      return res.send('ok');
    }

    // Для других типов событий просто логируем и отправляем 'ok'
    console.log(`ℹ️  Event type '${type}' received but not processed`);
    res.send('ok');

  } catch (error) {
    console.error('❌ Callback handler error:', error.message);
    console.error('Stack:', error.stack.split('\n').slice(0, 3).join('\n'));
    // VK требует 'ok' в ответе, даже при ошибках
    res.send('ok');
  }
});

// Основной маршрут
app.get('/', (req, res) => {
  res.status(200).json({
    status: '✅ OK',
    message: '🤖 VK Educational Bot is running',
    programs: programs.length,
    version: '1.0.0',
    api: '5.131'
  });
});

// Проверка здоровья для Render
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: {
      used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
      total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024)
    }
  });
});

// Обработка 404 ошибок
app.use((req, res) => {
  console.warn(`⚠️  404 Not Found: ${req.method} ${req.path}`);
  res.status(404).json({
    error: 'Not Found',
    path: req.path,
    method: req.method
  });
});

// Обработка необработанных ошибок
process.on('unhandledRejection', (reason, promise) => {
  console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('❌ Uncaught Exception:', error);
});

// ✅ Проверка переменных окружения перед запуском
function validateEnvironment() {
  const requiredVars = ['VK_TOKEN', 'VK_SECRET', 'VK_CONFIRMATION'];
  const missing = requiredVars.filter(varName => !process.env[varName]);
  
  if (missing.length > 0) {
    console.error('');
    console.error('╔════════════════════════════════════════════════════════╗');
    console.error('║                  ❌ ОШИБКА КОНФИГУРАЦИИ                ║');
    console.error('╚════════════════════════════════════════════════════════╝');
    console.error('');
    console.error('❌ Отсутствуют переменные окружения:');
    missing.forEach(varName => {
      console.error(`   - ${varName}`);
    });
    console.error('');
    console.error('📝 Пожалуйста, установите следующие переменные в .env:');
    console.error('');
    missing.forEach(varName => {
      console.error(`   ${varName}=значение`);
    });
    console.error('');
    console.error('📚 Смотрите .env.example для справки');
    console.error('');
    process.exit(1);
  }
  
  console.log('✅ Все переменные окружения установлены корректно');
}

// Запуск сервера
const PORT = process.env.PORT || 3000;

// Проверка конфигурации перед запуском
validateEnvironment();

app.listen(PORT, () => {
  console.log('');
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║      🤖 VK EDUCATIONAL BOT ЗАПУЩЕН УСПЕШНО! 🤖       ║');
  console.log('╚════════════════════════════════════════════════════════╝');
  console.log('');
  console.log(`✅ Сервер запущен на порту: ${PORT}`);
  console.log(`✅ Загружено программ: ${programs.length}`);
  console.log(`✅ Бот готов получать сообщения из VK`);
  console.log('');
  console.log('📍 Важные адреса:');
  console.log(`   🔐 Callback URL: /callback`);
  console.log(`   ❤️  Health check: /health`);
  console.log('');
  console.log('📖 API версия: 5.131');
  console.log(`⏰ Время запуска: ${new Date().toLocaleString('ru-RU')}`);
  console.log('');
});
