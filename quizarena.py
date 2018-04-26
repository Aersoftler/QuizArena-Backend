from flask import Flask, send_from_directory
from flask_sslify import SSLify

from quiz.category_api import category_app
from quiz.session_api import session_app
from user.user_api import user_app

app = Flask(__name__, static_url_path='/static')
app.register_blueprint(user_app)
app.register_blueprint(session_app)
app.register_blueprint(category_app)

SSLify(app, permanent=True)


@app.route('/', methods=['GET'])
def root():
    return send_from_directory('static', 'QuizArena-lila.png'), 200


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'QuizArena-lila.png'), 200


@app.route('/sharing/<session_id>')
def sharing(session_id):
    return send_from_directory('static', 'quizarena.html'), 200


@app.route('/download')
def download():
    return send_from_directory('download', 'quizarena.apk'), 200


if __name__ == '__main__':
    app.run()
