from flask import Flask, render_template, request
import datetime
import json

app = Flask(__name__)

DB_FILE = "./data/db.json"  # Путь к файлу с сообщениями
db = open(DB_FILE, "rb")  # Открываем файл для чтения
data = json.load(db)  # Загрузить все данные в формате JSON из файла
messages = data["messages"]  # Из полученных данных берем поле messages


#  Функция для сохранения всех сообщений (в списке message) в файл
def save_messages_to_file():
    db = open(DB_FILE, "w")  # Открываем файл для записи
    data = {   # Создаем структуру для записи в файл
        "messages": messages
    }
    json.dump(data, db)  # Записываем структуру в файл



def add_message(text, sender):  # Объявим функцию, которая добавит сообщение в список
    now = datetime.datetime.now()  # текущее время и дата
    new_message = {
        "text": text,
        "sender": sender,
        "time": now.strftime("%H:%M")  # Текущий час:минуты
    }
    messages.append(new_message)  # Добавляем новое сообщение в список
    save_messages_to_file()


def print_message(message):  # Объявляем функцию, которая будет печатать одно сообщение
    print(f"[{message['sender']}]: {message['text']} / {message['time']} ")


# Главная страница
@app.route("/")
def index_page():
    return "Здравствуйте, вас приветствует СкиллЧат2022"


# Показать все сообщения в формате JSON
@app.route("/get_messages")
def get_messages():
    return {"messages": messages}


# Показать форму чата
@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/send_message")
def send_message():
    #  Получить имя и текст от пользователя
    name = request.args["name"]  # Получаем имя
    text = request.args["text"]  # Получаем текст
    #  Вызвать фукнцию add_message
    add_message(text, name)
    return "OK"


app.run()  # Запускаем веб-приложение


