'''import os


count = 0
path = 'C:/Users/Владислав/PycharmProjects/Memoss/static/img'
for file in os.listdir(path):
    os.rename(f'{path}/{file}', f'{path}/{count}.jpg')
    count += 1'''

import sqlite3
import os
from PIL import Image
from datetime import datetime
from random import choice, randint


path = 'C:/Users/Владислав/PycharmProjects/Memoss/static/content'
abc = 'qwertyuiop[asdfghjkl;zxcvbnm,.QWERTYUIOP{ASDFGHJKLZXCVBNM<>?'

connect = sqlite3.connect('MemossDB.sqlite')
cursor = connect.cursor()


def get_date():
    return f'{datetime.now().day}.{datetime.now().month}.{datetime.now().year}'


def get_time():
    return f'{datetime.now().hour}:{datetime.now().minute}'


def get_URL(n):
    alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    result = ''
    for i in range(n):
        result += choice(alphabet)
    return result


def get_comment(n):
    alphabet = 'qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM                  !!!???...,,,'
    result = ''
    for i in range(n):
        result += choice(alphabet)
    return result


for file in os.listdir(path):
    image = Image.open(path + '/' + file)
    width, height = image.size
    cursor.execute(f'INSERT INTO content (`Name`, `Description`, `Views`, `Likes`, `URL`, `Date`, `Time`, `Width`, `Height`) VALUES ("{file}", "{get_comment(randint(0, 30))}", {randint(1, 1000)}, {randint(1, 500)}, "{get_URL(16)}", "{get_date()}", "{get_time()}", {width}, {height})')
    connect.commit()

"""
for i in range(1000):
    cursor.execute(f'INSERT INTO `comments` (`IDpost`, `IDuser`, `Text`, `Date`, `Time`) VALUES ({randint(0, 100)}, {randint(0, 100)}, "{get_URL(randint(0, 30))}", "{get_date()}", "{get_time()}")')
    connect.commit()
"""