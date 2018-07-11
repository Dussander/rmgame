from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
from flask_session import Session

from rmgame import game_class

app = Flask(__name__)
sess = Session()

@app.route("/")
def index():
    # this is used to "setup" the session with starting values
    session['engine'] = game_class.a_game
    return redirect(url_for("game"))

@app.route("/game", methods=['GET', 'POST'])
def game():
    engine = session['engine']

    if request.method == "GET":
        if engine:
            return render_template("show_room.html", engine=engine)
        else:
            return render_template("you_died.html")
    elif request.method == "POST":
        action = request.form.get('action')

        # there is a bug here, can you fix it?
        if engine and action:
            session['engine'] = engine.digest(action)

    return redirect(url_for("game"))


if __name__ == '__main__':
    app.secret_key = 'an7y2sldf78aql8f'
    app.config['SESSION_TYPE'] = 'filesystem'
    sess.init_app(app)
#    app.debug = True
    app.run(host='192.168.1.121', port=8080)

