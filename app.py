import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "byt-mig-i-produktion")

socketio = SocketIO(app)

CHAT_PASSWORD = os.environ.get("CHAT_PASSWORD", "hemlis!")
MAX_HISTORY = 50
MAX_MESSAGE_LENGTH = 500

chat_history = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        password_attempt = request.form.get("password", "")
        username = request.form.get("username", "").strip()[:30]

        if password_attempt == CHAT_PASSWORD and username:
            session["username"] = username
            return redirect(url_for("index"))

        return render_template("login.html", error=True), 403

    if "username" not in session:
        return render_template("login.html")

    return render_template("index.html", username=session["username"])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@socketio.on("connect")
def handle_connect():
    if "username" not in session:
        return False

    print(f"{session['username']} anslot. Skickar historik...")
    emit("history", chat_history)


@socketio.on("message")
def handle_message(data):
    if "username" not in session:
        return

    msg = str(data.get("msg", "")).strip()
    if not msg:
        return

    message = {
        "user": session["username"],
        "msg": msg[:MAX_MESSAGE_LENGTH],
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    chat_history.append(message)
    if len(chat_history) > MAX_HISTORY:
        chat_history.pop(0)

    print(f"Sparat meddelande fran {message['user']}")
    send(message, broadcast=True)


@socketio.on("clear_chat")
def handle_clear():
    if "username" not in session:
        return

    chat_history.clear()
    print(f"Chatten rensades av {session['username']}.")
    emit("chat_cleared", broadcast=True)


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    socketio.run(app, host="0.0.0.0", port=5000, debug=debug_mode)