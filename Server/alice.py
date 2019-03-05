from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from Server.server import Server

app = Flask(__name__)


@app.route('/')
def alice_handler():
    return "Hello world!"

def start_server():
    server = Server()


app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()

