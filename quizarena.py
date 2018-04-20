from threading import Thread

from flask import Flask
from flask_sslify import SSLify

from quiz.Session import Session
from quiz.category_api import category_app
from quiz.session_api import session_app
from user.user_api import user_app

app = Flask(__name__)
app.register_blueprint(user_app)
app.register_blueprint(session_app)
app.register_blueprint(category_app)

SSLify(app, permanent=True)


@app.route('/', methods=['GET'])
def get():
    return 'App is running', 200


if __name__ == '__main__':
    Thread(target=Session.tidy_up_sessions).start()
    app.run()
