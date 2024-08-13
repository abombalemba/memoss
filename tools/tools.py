'''import os


count = 0
path = 'C:/Users/Владислав/PycharmProjects/Memoss/static/img'
for file in os.listdir(path):
    os.rename(f'{path}/{file}', f'{path}/{count}.jpg')
    count += 1'''

# import sqlite3
# import os
# from PIL import Image
# from datetime import datetime
# from random import choice, randint


# path = 'C:/Users/Владислав/PycharmProjects/Memoss/static/content'
# abc = 'qwertyuiop[asdfghjkl;zxcvbnm,.QWERTYUIOP{ASDFGHJKLZXCVBNM<>?'

# connect = sqlite3.connect('MemossDB.sqlite')
# cursor = connect.cursor()


# def get_date():
#     return f'{datetime.now().day}.{datetime.now().month}.{datetime.now().year}'


# def get_time():
#     return f'{datetime.now().hour}:{datetime.now().minute}'


# def get_URL(n):
#     alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
#     result = ''
#     for i in range(n):
#         result += choice(alphabet)
#     return result


# def get_comment(n):
#     alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM    '
#     result = ''
#     for i in range(n):
#         result += choice(alphabet)
#     return result


# for file in os.listdir(path):
#     image = Image.open(path + '/' + file)
#     width, height = image.size
#     cursor.execute(f'INSERT INTO content (`Name`, `Description`, `Views`, `Likes`, `URL`, `Date`, `Time`, `Width`, `Height`) VALUES ("{file}", "{get_comment(randint(0, 30))}", {randint(1, 1000)}, {randint(1, 500)}, "{get_URL(16)}", "{get_date()}", "{get_time()}", {width}, {height})')
#     connect.commit()

"""
for i in range(1000):
    cursor.execute(f'INSERT INTO `comments` (`IDpost`, `IDuser`, `Text`, `Date`, `Time`) VALUES ({randint(0, 100)}, {randint(0, 100)}, "{get_URL(randint(0, 30))}", "{get_date()}", "{get_time()}")')
    connect.commit()
"""



from os import path
from PIL import Image
from datetime import datetime


def get_date():
    return f'{datetime.now().day}.{datetime.now().month}.{datetime.now().year}'


def get_time():
    return f'{datetime.now().hour}:{datetime.now().minute}'


def get_file_sizes(file_name):
    return Image.open(file_name).sizes


def get_file_weight(file_name):
    return path.getsize(file_name)


def get_string(n, m):
    from random import randint, choice
    from string import ascii_letters
    r = randint(n, m)
    result = ''
    for _ in range(r):
        result += choice(ascii_letters)
    return result

def fill_accounts():
    from sqlite3 import connect
    connection = connect('MemossDB — копия.sqlite')
    cursor = connection.cursor()
    for _ in range(100):
        nickname = get_string(4, 32)
        login = get_string(4, 32)
        password = get_string(4, 32)
        url = get_string(16, 16)
        icon = '1.gif'
        cursor.execute(f"""INSERT INTO ACCOUNTS (NICKNAME, LOGIN, PASSWORD, URL, ICON) VALUES ('{nickname}', '{login}', '{password}', '{url}', '{icon}')""")
        connection.commit()


def fill_content():
    from sqlite3 import connect
    from os import listdir
    from random import choice
    connection = connect('MemossDB — копия.sqlite')
    cursor = connection.cursor()
    for _ in range(400):
        filename = choice(listdir('C:/Users/Владислав/JT PycharmProjects/Memoss/static/content/'))
        description = get_string(0, 64)
        cursor.execute(f"""INSERT INTO CONTENT (FILENAME, DESCRIPTION) VALUES ('{filename}', '{description}')""")
        connection.commit()


def fill_post():
    from sqlite3 import connect
    from os import listdir
    from json import loads, dumps
    from random import randint
    connection = connect('MemossDB — копия.sqlite')
    cursor = connection.cursor()
    for _ in range(100):
        title = get_string(0, 16)
        content = dumps([randint(1, 483) for _ in range(randint(1, 16))])
        url = get_string(16, 16)
        datetime = get_date() + ' ' + get_time()
        cursor.execute(f"""INSERT INTO POST (TITLE, CONTENT, URL, DATETIME) VALUES ('{title}', '{content}', '{url}', '{datetime}')""")
        connection.commit()
