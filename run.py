from flask import Flask, render_template, json, request, session
from flask_socketio import SocketIO, send, emit
from main import preprocessing
from telebot import types, TeleBot
from telebot.util import async
import _thread


tkn = '343114871:AAH7VQdTnblr9szIKwH_CtibzWrQVv-qajU'
app = Flask(__name__)
socketio = SocketIO(app)
bot = TeleBot(tkn)
tags = ['CRM', 'Тестирование', 'Коммерция', 'Консалтинг',
        'Сервер', 'Интеграция', 'Телефония', 'Сайт']

global current_chat_id


@app.route('/hello')
def hello():
    return 'Hello World'


def update_json(tag, question):
    result = preprocessing(tag, question)
    data = {"title": "Здравствуйте, что вас интересует?",
            "type": "object",
            "properties": {tag: {
                "type": result[0]},
                tag + "2": {
                    "type": result[1]},
                tag + "3": {
                    "type": result[2]}
            }
            }
    socketio.emit('update json', json.dumps(data, indent=2, separators=(', ', ': ')), namespace='/socket')


@socketio.on('connect', namespace='/socket')
def test_connect():
    emit('Connect response', {'data': 'Connected'})


@socketio.on('disconnect', namespace='/socket')
def test_disconnect():
    print('Client disconnected')


@socketio.on('receive answer', namespace='/socket')
def get_javascript_data(message):
    print(message)
    test_send(message)


@async()
def test_send(text):
    print(session['client'])
    bot.send_message(session['client'], text)  # номер чата с десктопного приложения


@app.route('/viewer/')
def get_view():
    data = {"title": "Здравствуйте, что вас интересует?",
            "type": "object"
            }
    return render_template('index.html',
                           context=json.dumps(data, indent=2, separators=(', ', ': ')))


@bot.message_handler(commands=['start'])
def handle_text(message):
    answer = "Начало диалога"
    app.session['client'] = message.chat.id
    log(message, answer)
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton('Начать диалог')])
    bot.send_message(message.chat.id,
                     """Здравствуйте, вас приветствует система консультации.""",
                     reply_markup=keyboard,
                     parse_mode="Markdown")

# ВЫВОД ЛОГОВ
print(bot.get_me())


def log(message, answer):
    print("\n --------")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. (id = {2}) \n Текст - {3}". format(message.from_user.first_name,
                                                                    message.from_user.last_name,
                                                                    str(message.from_user.id),
                                                                    message.text))
    print(answer)


@bot.message_handler(func=lambda message: message.text == 'Начать диалог', content_types=['text'])
def handle_tags(message):
    answer = """Выберете интересующую вас тему."""
    keyboard = types.ReplyKeyboardMarkup(True, False)
    keyboard.add(*[types.KeyboardButton(tag) for tag in tags])
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=keyboard,
                     parse_mode="Markdown")

    log(message, answer)


@bot.message_handler(func=lambda message: message.text in tags, content_types=['text'])
def handle_text(message):
    answer = """Хорошо. Задайте ваш вопрос."""
    bot.send_message(message.chat.id, answer)

    log(message, answer)


@bot.message_handler(func=lambda message: message.text[-1:] == '?', content_types=['text'])
def handle_text2(message):
    answer = """Пожалуйста, подождите."""
    bot.send_message(message.chat.id, answer)

    log(message, answer)
    update_json('CRM', message.text)


def bot_thread():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    _thread.start_new_thread(bot_thread, ())
    socketio.run(app)






