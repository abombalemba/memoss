from flask import Flask, render_template, flash, redirect, request, send_file, jsonify
from werkzeug.utils import secure_filename
import flask

import sqlite3
from random import randint, choice
from os import environ
from PIL import Image
from datetime import datetime


server = Flask(__name__)
server.config['SECRET_KEY'] = '0a17e0af1f364c72065534d68a916153a780a5fc'
server.config['UPLOAD_FOLDER'] = './static/content/'
server.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

connect, cursor = None, None


@server.route('/')
@server.route('/gallery')
def index():
    return render_template('main.html', left_column=column(5), center_column=column(5), right_column=column(5))


@server.route('/reg')
def registration():
    return render_template('reg.html')


@server.route('/log')
def login():
    return render_template('log.html')


@server.route('/gallery/<string:link>')
def gallery_post(link):
    result = database_query(f"""SELECT * FROM `content` WHERE `URL` = "{link}" """)
    if result[0]:
        pass
    else:
        error()
    comments_id = database_query(f"""SELECT `ID` FROM `comments` WHERE `IDpost` = {result[0][0]} """)
    post = create_dict_post(result[0], len(comments_id))

    comments = []
    result = database_query(f"""SELECT * FROM `comments` WHERE `IDpost` = {post['ID']} """)
    for com in result:
        comments.append(create_dict_comments(com))

    return render_template('post.html', post=post, comments=comments)


@server.route('/user/<string:link>')
def user(link):
    result = database_query(f"""SELECT * FROM `accounts` WHERE `URL` = "{link}" """)
    if result[0]:
        result = create_dict_user(result[0])
    else:
        error()
    return render_template('user.html', data=result)


@server.route('/add')
def add():
    return render_template('add.html')


@server.route('/api/<string:link>')
def api(link):
    link = link.split('/')
    if link[0] == 'login':
        params = create_response(link[1])
        response = database_query(f"""SELECT * FROM `accounts` WHERE `Nickname` = "{params['login']}" """)
        if response[0]:
            if response[0][3] == params['password']:
                return jsonify(response)
                # return flask.render_template('main.html')
            else:
                return render_template('log.html', message='Неверный логин или пароль!')
        else:
            return render_template('log.html', message='Аккаунт не найден!')

    if link[1] == 'reg':
        params = create_response(link[1])
        if not params['nickname']:
            return render_template('reg.html', message='Введите ник')
        if not params['email']:
            return render_template('reg.html', message='Введите почту')
        if not params['password']:
            return render_template('reg.html', message='Введите пароль')

        response = database_query(f"""SELECT * FROM `accounts` WHERE `Nickname` = "{params['nickname']}" """)
        if response[0]:
            return render_template('reg.html', message='Этот ник занят')
        response = database_query(f"""SELECT * FROM `accounts` WHERE `Email` = "{params['Email']}" """)
        if response[0]:
            return render_template('reg.html', message='Эта почта занята')
        database_query(
            f"""INSERT INTO `accounts` (`Nickname`, `Email`, `Password`) VALUES ("{params['nickname']}", "{params['email']}", "{params['password']}") """)

        return render_template('main.html', message='Аккаунт создан')

    if link[1] == 'like':
        params = create_response(link[0])
        database_query(f"""UPDATE `accounts` SET `Likes` = `Likes` + 1 WHERE `ID` = {params['IDpost']}""")


@server.route('/send_file/<string:filename>')
def send_file(filename):
    path = './static/content/' + filename
    print(path, filename)
    return flask.send_file(path, as_attachment=True)


@server.route('/get_file/', methods=['GET', 'POST'])
def get_file():
    if request.method == 'GET':
        return render_template('add.html')

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            r = file.read()
            with open(f'./static/content/{filename}', mode='wb') as f:
                f.write(r)
    return render_template('add.html')


def error():
    return render_template('error.html')


def database_start():
    global connect, cursor
    connect = sqlite3.connect('MemossDB.sqlite', check_same_thread=False)
    cursor = connect.cursor()


def database_query(query=''):
    global cursor
    result = cursor.execute(query).fetchall()
    if query.split()[0] != 'SELECT':
        connect.commit()
    return result


def create_dict_post(result, comments):
    result = {
        'ID': result[0],
        'Name': result[1],
        'Description': result[2],
        'Views': result[3],
        'Likes': result[4],
        'Comments': comments,
        'URL': result[5],
        'Date': result[6],
        'Time': result[7],
        'Width': result[8],
        'Height': result[9],
    }
    return result


def create_dict_comments(result):
    result = {
        'ID': result[0],
        'IDpost': result[1],
        'IDuser': result[2],
        'Text': result[3],
        'Date': result[4],
        'Time': result[5],
    }
    return result


def create_dict_user(result):
    result = {
        'ID': result[0],
        'Nickname': result[1],
        'Email': result[2],
        'Password': result[3],
        'URL': result[4],
        'Preview': result[5],
        'LikedPosts': result[6],
    }
    return result


def column(n=10):
    posts = []
    for j in range(n):
        result = database_query(f'SELECT * FROM `content` WHERE ID = {randint(1, database_query("SELECT COUNT(*) FROM `content`")[0][0])}')
        print(result)
        comments = database_query(f'SELECT COUNT(`ID`) FROM `comments` WHERE `IDpost` = {result[0][0]}')
        database_query(f'UPDATE `content` SET `Views` = `Views` + 1 WHERE `ID` = {result[0][0]}')
        result = create_dict_post(result[0], comments[0][0])
        posts.append(result)
    return posts


def create_response(params):
    result = {}
    params = params.split('&')
    for param in params:
        item = param.split('=')
        result[item[0]] = item[1]
    return result


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_date():
    return f'{datetime.now().day}.{datetime.now().month}.{datetime.now().year}'


def get_time():
    return f'{datetime.now().hour}:{datetime.now().minute}'


def get_file_sizes(file_name):
    return Image.open(file_name).sizes


def get_URL(n):
    alphabet = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
    result = ''
    for i in range(n):
        result += choice(alphabet)
    return result


if __name__ == '__main__':
    database_start()
    port = int(environ.get('PORT', 5000))
    server.run(host='0.0.0.0', port=port)
