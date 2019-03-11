# -*- coding: utf-8 -*-
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
import func

app = Flask(__name__)

# Прочитаем готовую модель и изначальный датасет.
raw_data = func.get_raw_data()
data_bag = func.get_bag()


# Настройки рутов.
@app.route('/')
def index():
    return redirect(url_for('ask'))


@app.route('/ask/', methods=['POST', 'GET'])
def ask():
    if request.method == 'POST':
        question = request.form['question']
        answer = func.ask_bot(question, data_bag, raw_data)
        return render_template('ask.html', question=question, answer=answer)
    else:
        return render_template('ask.html')


# Старт веб-приложения.
if __name__ == '__main__':
    app.debug = True
    app.run()
