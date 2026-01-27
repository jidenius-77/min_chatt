from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hemlis!'
socketio = SocketIO(app)

# Vårt "minne" - en lista som sparar meddelande-objekt
chat_history = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        password_attempt = request.form.get('password')
        username = request.form.get('username')

        if password_attempt == 'undrom77':
            return render_template('index.html', username=username)
        else:
            return """
            <body style="background: #000; color: #ff0000; font-family: 'Courier New', monospace; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0;">
                <h1 style="text-shadow: 0 0 15px #ff0000; letter-spacing: 5px;">ACCESS DENIED</h1>
                <p style="border: 1px solid #ff0000; padding: 10px;">ERROR: Invalid Encryption Key</p>
                <a href="/" style="color: #ff0000; text-decoration: none; border: 1px solid #ff0000; padding: 10px 20px; margin-top: 20px; font-weight: bold;">[ TRY AGAIN ]</a>
            </body>
            """, 403
        
    return render_template('login.html')


@socketio.on('connect')
def handle_connect():
    # När en ny användare ansluter, skicka hela historiken bara till dem
    print("En ny användare anslöt. Skickar historik...")
    emit('history', chat_history)

@socketio.on('message')
def handle_message(data):
    data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Spara meddelandet i vår lista
    chat_history.append(data)
    
    # Håll historiken lagom stor (t.ex. de senaste 50 meddelandena)
    if len(chat_history) > 50:
        chat_history.pop(0)
        
    print(f"Sparat meddelande från {data['user']}")
    send(data, broadcast=True)

@socketio.on('clear_chat')
def handle_clear():
    global chat_history
    chat_history = []  # Tömmer listan på servern
    print("Chatten har rensats av en användare.")
    # Skicka en signal till ALLA klienter att de ska rensa sina skärmar
    emit('chat_cleared', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)