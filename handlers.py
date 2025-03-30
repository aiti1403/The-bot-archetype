import telebot
from telebot import types
from config import TOKEN, START, ANSWERING, FINISHED
from questions import QUESTIONS
from archetypes import ARCHETYPES
from user_state import UserState
import textwrap

bot = telebot.TeleBot(TOKEN)
user_state = UserState()

def create_options_keyboard(question_index):
    """Создает клавиатуру с вариантами ответов, разбивая длинный текст на несколько строк"""
    keyboard = types.InlineKeyboardMarkup()
    options = QUESTIONS[question_index]['options']
   
    for i, option in enumerate(options):
        # Разбиваем длинный текст на строки по ~30 символов
        wrapped_text = textwrap.wrap(option, width=30)
        
        # Создаем группу кнопок для одного варианта ответа
        for j, line in enumerate(wrapped_text):
            callback_data = f"answer_{question_index}_{i}"
            
            # Для первой строки добавляем номер варианта
            if j == 0:
                line = f"{i+1}. {line}"
                
            keyboard.add(types.InlineKeyboardButton(text=line, callback_data=callback_data))
        
        # Добавляем пустую кнопку-разделитель между вариантами ответов, если это не последний вариант
        if i < len(options) - 1:
            keyboard.add(types.InlineKeyboardButton(text="─────────────", callback_data="separator"))

    return keyboard

@bot.callback_query_handler(func=lambda call: call.data == "separator")
def separator_callback(call):
    """Обработчик нажатия на кнопку-разделитель"""
    # Просто игнорируем нажатие на разделитель
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['start'])
def start_handler(message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    user_state.reset_user(user_id)
   
    welcome_text = """
Добро пожаловать в тест на определение архетипа!

Этот тест поможет вам узнать, какой архетип соответствует вашей личности.
Вам предстоит ответить на 11 вопросов, выбирая наиболее подходящий для вас вариант.

Нажмите "Начать тест", чтобы приступить.
"""
   
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="Начать тест", callback_data="start_test"))
   
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "start_test")
def start_test_callback(call):
    """Обработчик нажатия на кнопку 'Начать тест'"""
    user_id = call.from_user.id
    user_data = user_state.update_user_state(user_id, state=ANSWERING, question=0)
   
    # Отправляем первый вопрос
    question_index = user_data['current_question']
    question_text = QUESTIONS[question_index]['text']
   
    keyboard = create_options_keyboard(question_index)
   
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=question_text,
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def answer_callback(call):
    """Обработчик выбора ответа"""
    user_id = call.from_user.id
    user_data = user_state.get_user_state(user_id)
   
    # Парсим данные из callback
    _, question_index, answer_index = call.data.split("_")
    question_index = int(question_index)
    answer_index = int(answer_index)
   
    # Записываем ответ
    user_state.record_answer(user_id, question_index, answer_index)
   
    # Переходим к следующему вопросу или завершаем тест
    next_question = question_index + 1
    if next_question < len(QUESTIONS):
        user_data = user_state.update_user_state(user_id, question=next_question)
        question_text = QUESTIONS[next_question]['text']
        keyboard = create_options_keyboard(next_question)
        
        # Отправляем новое сообщение с вопросом вместо редактирования текущего
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text=question_text,
            reply_markup=keyboard
        )
    else:
        # Тест завершен
        user_state.update_user_state(user_id, state=FINISHED)
        dominant_archetype = user_state.get_dominant_archetype(user_id)
       
        result_text = f"""
✨ ТЕСТ ЗАВЕРШЁН! ✨

✨ Ваш доминирующий архетип: «{dominant_archetype}» ✨

✨ Нужен идеальный образ?

✨ Узнайте, как подчеркнуть вашу силу и уникальность через стиль!

✨ Выберите LookBook в https://t.me/emotionlifestyle с готовыми
решениями для:

• Романтики ✨
• Работы ✨
• Вечеринки ✨
• И других важных событий!

✨ Прокачайте себя: https://t.me/EmoCompassBot

✨ Видеоэфир — секреты отношений и финансов ✨

✨ Марафон — архетип как суперсила!

✨ Ссылки:
• Лукбук: https://t.me/emotionlifestyle
• Видео + марафон: https://t.me/EmoCompassBot

✨ Раскройте свой потенциал на 100% — вы этого достойны! ✨
"""
       
        # Удаляем текущее сообщение и отправляем результат
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            chat_id=call.message.chat.id,
            text=result_text,
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['help'])
def help_handler(message):
    """Обработчик команды /help"""
    help_text = """
Это бот для определения вашего архетипа.

Команды:
/start - Начать тест
/help - Показать эту справку
/reset - Сбросить прогресс и начать заново
"""
   
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    """Обработчик команды /reset"""
    user_id = message.from_user.id
    user_state.reset_user(user_id)
   
    bot.send_message(message.chat.id, "Ваш прогресс сброшен. Чтобы начать тест заново, нажмите /start")
