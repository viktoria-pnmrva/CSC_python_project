from flask import Flask
from flask import request
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods = ['POST', 'GET'])

def main():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['username'],
                       request.form['password']):
            return log_the_user_in(request.form['username'])
        else:
            error = 'Invalid username/password'


    return str(datetime.now())


app.run()