# Импортирует поддержку UTF-8.
from __future__ import unicode_literals

from flask import Flask, request
from werkzeug.contrib.fixers import ProxyFix
import sys
from Server.server import Server
import json

#Настройка логирования
from Server.s_log import setup_logger
alice_log = setup_logger('alice logger', 'alice.log')

#импорт набора фраз
from Server.alice_client import AliceClient

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
    alice_log.info('Request: %r', request.json)

    response = {
        "version": request.json['version'],
        "session": request.json['session'],
        "response": {
            "end_session": False
        }
    }

    user_id = request.json['session']['user_id']

    if request.json['session']['new']:
        #Если новая сессия создаем класс клиента
        sessionStorage[user_id] = AliceClient(user_id)

    #Вызываем обработчик диалога
    response = sessionStorage[user_id].handle_dialog(request.json, response)

    alice_log.info('Response: %r', response)

    return json.dumps(response, ensure_ascii=False, indent=2)





app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()

