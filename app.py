const express = require('express');
const crypto = require('crypto');
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
  const messageToSend = {
    user_id: userId,
    message: message,
    random_id: Math.floor(Math.random() * 1000000)
  };

  try {
    const response = await fetch('https://api.vk.com/method/messages.send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        ...messageToSend,
        access_token: process.env.VK_TOKEN,
        v: '5.131'
      })
    });

    const data = await response.json();
    if (data.error) {
      console.error('VK API Error:', data.error);
    }
  } catch (error) {
    console.error('Error sending message:', error);
  }
}

// Функция поиска подходящих программ по возрасту
function findProgramsByAge(age) {
  return programs.filter(program => {
    const [minAge, maxAge] = program.age.split('-').map(a => parseInt(a));
    return age >= minAge && age <= maxAge;
  });
}

// Функция генерации ответа
function generateResponse(text, userId) {
  const lowerText = text.toLowerCase().trim();
  
  let response = '';

  // Обработка разных типов запросов
  if (lowerText.includes('привет') || lowerText.includes('привет') || lowerText.includes('начало')) {
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
    
    Object.keys(prices).sort().forEach(price => {
      response += `${price} ₽: ${prices[price].join(', ')}\n`;
    });
    
    response += '\n💡 Логопед и развитие речи: 600 ₽/занятие + 800 ₽ диагностика';
  }
  
  else if (/(\d+)\s*(?:лет|год|года)/.test(lowerText) || /мне\s*(\d+)/.test(lowerText)) {
    const ageMatch = lowerText.match(/(\d+)\s*(?:лет|год|года|мне)/);
    if (ageMatch) {
      const age = parseInt(ageMatch[1]);
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
  
  else if (lowerText.includes('робот')) {
    const robotics = programs.filter(p => p.name.includes('Робототехника'));
    response = '🤖 Программы робототехники:\n\n';
    robotics.forEach(prog => {
      response += `${prog.name}\n   Возраст: ${prog.age}\n   Цена: ${prog.price} ₽\n\n`;
    });
  }
  
  else if (lowerText.includes('хореогра') || lowerText.includes('танц')) {
    const dance = programs.find(p => p.name.includes('Хореография'));
    response = `💃 ${dance.name}\n` +
      `Возраст: ${dance.age}\n` +
      `Цена: ${dance.price} ₽\n` +
      `Описание: ${dance.description}`;
  }
  
  else if (lowerText.includes('логопед') || lowerText.includes('речь')) {
    const speech = programs.find(p => p.name.includes('Логопед'));
    response = `🗣️ ${speech.name}\n` +
      `Возраст: ${speech.age}\n` +
      `Цена: ${speech.price} ₽\n` +
      `Диагностика: ${speech.diagnostic} ₽\n` +
      `Описание: ${speech.description}`;
  }
  
  else if (lowerText.includes('дошколён') || lowerText.includes('школ')) {
    const preschool = programs.filter(p => p.name.includes('Дошколён'));
    response = '📖 Программы подготовки к школе:\n\n';
    preschool.forEach(prog => {
      response += `${prog.name}\n   Возраст: ${prog.age}\n   Цена: ${prog.price} ₽\n\n`;
    });
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
app.post('/callback', (req, res) => {
  const { type, object, secret } = req.body;

  // Проверка секрета
  if (secret !== process.env.VK_SECRET) {
    return res.status(403).send('Invalid secret');
  }

  if (type === 'confirmation') {
    console.log('Confirmation received');
    return res.send(process.env.VK_CONFIRMATION);
  }

  if (type === 'message_new') {
    const { message } = object;
    const { text, from_id } = message;

    console.log(`Message from ${from_id}: ${text}`);

    // Проверка, что это сообщение не от сообщества
    if (from_id > 0) {
      const response = generateResponse(text, from_id);
      sendVKMessage(from_id, response);
    }

    return res.send('ok');
  }

  res.send('ok');
});

// Основной маршрут
app.get('/', (req, res) => {
  res.send('VK Educational Bot is running 🤖');
});

// Проверка здоровья для Render
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log('Bot is ready to receive messages from VK!');
});
