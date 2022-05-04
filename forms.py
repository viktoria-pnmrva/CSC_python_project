from collections import namedtuple
import sqlite3
from random import randint, choice
from flask import Flask, render_template, redirect, url_for, request,g
from urllib.request import urlopen
import re
app = Flask(__name__)

Message = namedtuple('Message', 'text tag')
message = ''
video = None
subtitle = None
@app.route('/', methods=['GET'])
def main():
    global message
    global video
    global subtitle
    return render_template('main.html', message=message, video = video,subtitle = subtitle)

def find_video(text):
    global CURSOR
    CURSOR = get_db().cursor()
    find_word = find_usages(text)
    print(find_word)

    if(len(find_word) != 0):
        r = choice(find_word)
        print(r)
        video_id = r[0]
        star_time = r[4] // 1000 - 1
        end_time = star_time + r[1] // 1000 + 5
        print(r[2])
        video_url = f'https://embed.ted.com/talks/lang/en/{video_id}'
        print(video_url)
        html = str(urlopen(video_url).read())
        print(html)
        pattern = r'https://py.tedcdn.com/.*.mp4'
        match = re.search(pattern, html)
        print(match)
        start = match.span()[0]
        end = match.span()[1]

        global video, subtitle
        subtitle = r[2]
        video = html[start:end] + f'#t={star_time},{end_time}'
        print(1)

        print('finded video ', video)
        return video, subtitle
    return None, None


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form['text']
    global message
    message = text
    global video
    global subtitle
    video, subtitle = find_video(text)
    if(video == None):
        message = 'word '+ message+' didn\'t find'
        subtitle = None
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
