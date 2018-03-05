from flask import Flask
from threading import Thread

from quiz.Session import Session
from quiz.session_api import session_app
from user.user_api import user_app

app = Flask(__name__)
app.register_blueprint(user_app)
app.register_blueprint(session_app)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    Thread(target=Session.close_finished_sessions).start()
    app.run()
