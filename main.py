from flask import Flask, render_template, flash, redirect, request, send_file, jsonify
from werkzeug.utils import secure_filename

import sqlite3
from json import loads, dumps
from random import randint, choice
from os import environ, path
from PIL import Image
from datetime import datetime


server = Flask(__name__)
server.config['SECRET_KEY'] = '0a17e0af1f364c72065534d68a916153a780a5fc'
server.config['UPLOAD_FOLDER'] = './static/content/'
server.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 4

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'tiff']
COUNT_POSTS = 20

connect, cursor = None, None


@server.route('/')
@server.route('/gallery')
def index():
    return render_template('index.html', left_column=column(COUNT_POSTS), center_column=column(COUNT_POSTS), right_column=column(COUNT_POSTS))


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


@server.route('/chat/<string:params>')
def chat(params):
    params = create_response(params)


@server.route('/api/<string:link>/<string:params>', methods=['GET', 'POST'])
def api(link, params):
    print(link, params)
    if link == 'login':
        params = create_response(params)
        response = database_query(f"""SELECT * FROM `accounts` WHERE `Nickname` = "{params['login']}" """)
        if response[0]:
            if response[0][3] == params['password']:
                return jsonify(response)
                # return flask.render_template('main.html')
            else:
                return render_template('log.html', message='Неверный логин или пароль!')
        else:
            return render_template('log.html', message='Аккаунт не найден!')

    if link == 'reg':
        params = create_response(params)
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

    if link == 'like':
        params = create_response(params)
        print(params)
        database_query(f"""UPDATE `content` SET `Likes` = `Likes` + 1 WHERE `ID` = {params['IDpost']}""")

    if link == 'dislike':
        params = create_response(params)
        database_query(f"""UPDATE `content` SET `Dislikes` = `Dislikes` + 1 WHERE `ID` = {params['IDpost']}""")

    if link == 'comment':
        params = create_response(params)
        database_query(f"""INSERT INTO `comments`" (`IDpost`, `IDuser`, `Text`, `Date`, `Time`) VALUES """
                       f"""({params['IDpost']}, {params['IDuser']}, "{params['Text']}", "{get_date()}", "{get_time()}")""")

    if link == 'send_file':
        params = create_response(params)
        return send_file('./static/content/' + params['filename'], as_attachment=True)

    if link == 'get_file':
        params = create_response(params)
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

                sizes = get_file_sizes(f'./static/content/{filename}')
                weight = get_file_weight(f'static/content/{filename}')
                print(sizes, weight)
                database_query(f'INSERT INTO `content` (`Name`, `Description`, `URL`, `Date`, `Time`, `Width`, `Height`) VALUES'
                               f'("{filename}", "{1}", "{get_URL(16)}", "{get_date()}", "{get_time()}", {sizes[0]}, {sizes[1]})')

    if link == 'send_message':
        params = create_response(params)
        database_query(f"""INSERT INTO `chat` (`IDuser`, `Text`, `Date`, `Time`) VALUES ({params['IDuser']}, "{params['Text']}", "{get_date()}", "{get_time()}")""")

    if link == 'get_message':
        result = database_query(f"""SELECT * FROM `chat` ORDER BY `ID` DESC LIMIT 50""")
        return jsonify(result)
    return dumps({'a': 123})


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
    return {
        'ID': result[0],
        'Name': result[1],
        'Description': result[2],
        'Views': result[3],
        'Likes': result[4],
        'Dislikes': result[5],
        'Comments': comments,
        'URL': result[6],
        'Date': result[7],
        'Time': result[8],
        'Width': result[9],
        'Height': result[10],
    }


def create_dict_comments(result):
    return {
        'ID': result[0],
        'IDpost': result[1],
        'IDuser': result[2],
        'Text': result[3],
        'Date': result[4],
        'Time': result[5],
    }


def create_dict_user(result):
    return {
        'ID': result[0],
        'Nickname': result[1],
        'Email': result[2],
        'Password': result[3],
        'URL': result[4],
        'Preview': result[5],
        'LikedPosts': result[6],
    }


def create_dict_message(result):
    return {
        'ID': result[0],
        'IDuser': result[1],
        'Text': result[2],
        'Date': result[3],
        'Time': result[4]
    }


def column(n=10):
    posts = []
    for j in range(n):
        result = database_query(f'SELECT * FROM `content` WHERE ID = {randint(1, database_query("SELECT COUNT(*) FROM `content`")[0][0])}')
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


def get_file_weight(file_name):
    return path.getsize(file_name)


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
