from collections import namedtuple
import sqlite3
from random import randint
from flask import Flask, render_template, redirect, url_for, request,g
from urllib.request import urlopen
import re
app = Flask(__name__)

Message = namedtuple('Message', 'text tag')
message = ''


@app.route('/', methods=['GET'])
def main():
    global message, video
    video = None
    return render_template('main.html', message=message, video = video)

def find_video(text):
    global CURSOR
    CURSOR = get_db().cursor()
    find_word = find_usages(text)
    print(find_word)
    if(len(find_word) != 0):
        r = randint(0, len(find_word))
        video_id = find_word[r][0]
        star_time = find_word[r][4] // 1000 - 1
        end_time = star_time + find_word[r][1] // 1000 + 1
        print(find_word[r][2])
        video_url = f'https://embed.ted.com/talks/lang/en/{video_id}'
        print(video_url)
        html = str(urlopen(video_url).read())
        print(html)
        pattern = r'https://py.tedcdn.com/.*.mp4'
        match = re.search(pattern, html)
        print(match)
        start = match.span()[0]
        end = match.span()[1]
        global video
        video = html[start:end] + f'#t={star_time},{end_time}'
        print(1)
    return None


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form['text']
    global message
    message = text
    print(find_video(text))
    return redirect(url_for('main'))


DATABASE = 'subtitles.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def dict_factory(cursor, row):
    # обертка для преобразования
    # полученной строки. (взята из документации)
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



def find_usages(text: str):
    global CURSOR
    CURSOR.execute(
        f"""
        select * from subtitles
        where content like '% {text} %';
        """
    )
    usages_dict = CURSOR.fetchall()
    return usages_dict


app.run()
