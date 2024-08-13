from flask import Flask, render_template, flash, redirect, request, send_file, jsonify, url_for, abort, session
from werkzeug.utils import secure_filename

from json import dumps, loads
from random import randint, choice

from tools import tools, structures


app = Flask(__name__)
app.config['SECRET_KEY'] = '5a17e0af1f364c72065534d68a916153a780a5fc'
app.config['UPLOAD_FOLDER'] = './static/content/'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 4

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'tiff']
COUNT_POSTS = 20
MAX_CONTENT_IN_POST = 16

connection, cursor = None, None

menu = [
    {}
]

@app.route('/')
def index():
    return render_template('base.html', left_column=column(COUNT_POSTS), center_column=column(COUNT_POSTS), right_column=column(COUNT_POSTS))


@app.route('/reg')
def registration():
    return render_template('reg.html')


@app.route('/log')
def login():
    return render_template('log.html')


@app.route('/gallery/<string:link>')
def gallery_post(link):
    post = database_query(f"""SELECT * FROM `POST` WHERE `URL` = '{link}' LIMIT 1""")[0]
    post = prepare_data(post, 'post')
    content = []
    for content_id in post.content:
        content.append(prepare_data(database_query(f"""SELECT * FROM `CONTENT` WHERE `ID` = {content_id} LIMIT 1""")[0], 'content'))
    #comments_id = database_query(f"""SELECT `ID` FROM `COMMENTS` WHERE `ID_POST` = {post[0]}""")
    #comments = [prepare_data() for comment in database_query(f"""SELECT * FROM `COMMENTS` WHERE `ID` = {}""")
    return render_template('post.html', post=content, comments=[])


@app.route('/user/<string:link>')
def user(link):
    result = database_query(f"""SELECT * FROM `ACCOUNTS` WHERE `URL` = "{link}" LIMIT 1""")
    if result[0]:
        result = prepare_data(result[0], 'account')
        return render_template('user.html', data=result)
    return error()


@app.route('/add')
def add():
    return render_template('add.html')


@app.route('/chat/<string:params>')
def chat(params):
    params = create_response(params)


@app.route('/api/<string:link>/<string:params>', methods=['GET', 'POST'])
def api(link, params):
    print(link, params)
    if link == 'login':
        params = create_response(params)
        response = database_query(f"""SELECT * FROM `ACCOUNTS` WHERE `NICKNAME` = "{params['login']}" """)
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

        response = database_query(f"""SELECT * FROM `ACCOUNTS` WHERE `Nickname` = "{params['nickname']}" """)
        if response[0]:
            return render_template('reg.html', message='Этот ник занят')
        response = database_query(f"""SELECT * FROM `ACCOUNTS` WHERE `Email` = "{params['Email']}" """)
        if response[0]:
            return render_template('reg.html', message='Эта почта занята')
        database_query(
            f"""INSERT INTO `ACCOUNTS` (`Nickname`, `Email`, `Password`) VALUES ("{params['nickname']}", "{params['email']}", "{params['password']}") """)

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
                       f"""({params['IDpost']}, {params['IDuser']}, "{params['Text']}", "{tools.get_date()}", "{tools.get_time()}")""")

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

                sizes = tools.get_file_sizes(f'./static/content/{filename}')
                weight = tools.get_file_weight(f'static/content/{filename}')
                print(sizes, weight)
                database_query(f'INSERT INTO `content` (`Name`, `Description`, `URL`, `Date`, `Time`, `Width`, `Height`) VALUES'
                               f'("{filename}", "{1}", "{get_url(16)}", "{get_date()}", "{get_time()}", {sizes[0]}, {sizes[1]})')

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
    from sqlite3 import connect
    global connection, cursor
    connection = connect('data/MemossDB.sqlite', check_same_thread=False)
    cursor = connection.cursor()


def database_query(query=''):
    global cursor
    result = cursor.execute(query).fetchall()
    if query.split()[0] != 'SELECT':
        connection.commit()
    return result


def check_user_login(session) -> bool:
    if session['user_login']:
        return True
    return False


def prepare_data(result, structure):
    match structure:
        case 'account':
            return structures.Account(*result)
        case 'content':
            return structures.Content(*result)
        case 'post':
            return structures.Post(*result)
        case 'comment':
            return structures.Comment(*result)
        case _:
            return 'Error: Unknown structure'


def column(n=10):
    posts = []
    for _ in range(n):
        random_post = database_query(f"""SELECT * FROM `POST` WHERE `ID` = {randint(1, database_query("SELECT COUNT(*) FROM `POST`")[0][0])} LIMIT 1""")[0]
        posts.append(prepare_data(random_post, 'post'))
    
    for post in posts:
        database_query(f"""UPDATE `POST` SET `VIEWS` = `VIEWS` + 1 WHERE `ID` = {post.ID}""")
        post.icon = database_query(f"""SELECT `FILENAME` FROM `CONTENT` WHERE `ID` = {post.content[0]} LIMIT 1""")[0][0]
        for content_id in post.content:
            post_likes = sum([database_query(f"""SELECT `LIKES` FROM `CONTENT` WHERE `ID` = {content_id} LIMIT 1""")[0][0] for content_id in post.content])
            post_dislikes = sum([database_query(f"""SELECT `DISLIKES` FROM `CONTENT` WHERE `ID` = {content_id} LIMIT 1""")[0][0]])
            post.reputation = post_likes - post_dislikes
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


def get_url(n):
    from string import ascii_letters
    result = ''
    for _ in range(n):
        result += choice(ascii_letters)
    return result


if __name__ == '__main__':
    database_start()
    app.run(host='0.0.0.0', port=5000, debug=True)
