# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
import sys
import logging
from Server.server import Server
import json


logging.basicConfig(level=logging.DEBUG)

#Запуск сервера
server = Server()
server.start()

# Хранилище данных о сессиях.
sessionStorage = {}

app = Flask(__name__)

@app.route('/clients')
def get_clients():
    try:
        global server
        return 'Clients:\n' + '\n'.join(server.get_client_list())
    except:
        return str(sys.exc_info())

@app.route('/', methods=['POST'])
def alice_handler():
    logging.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', response)

    return json.dumps(response, ensure_ascii=False, indent=2)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.

        sessionStorage[user_id] = {
            'suggests': [
                "Выключить экран",
                "Звук потише",
                "Звук погромче",
            ]
        }

        res['response']['text'] = 'Привет! Что желаете?'
        res['response']['buttons'] = get_suggests(user_id)
        return

def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": "https://market.yandex.ru/search?text=слон",
            "hide": True
        })

    return suggests


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()

