from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hemlis!'
socketio = SocketIO(app)

chat_history = []

# FIXA SKÄRMEN SÅ ALLT SYNS MED RENSA CHATTEN!!!!!!

@app.route('/', methods=['GET', 'POST'])
def index():
    # Autentisering
    if request.method == 'POST':
        password_attempt = request.form.get('password')
        username = request.form.get('username')

        if password_attempt == 'hemlis!':
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
    # När en ny användare ansluter, skicka hela historiken
    print("En ny användare anslöt. Skickar historik...")
    emit('history', chat_history)

@socketio.on('message')
def handle_message(data):
    # Spara meddelandet i vår lista och skicka det till alla anslutna användare
    data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    chat_history.append(data)
    
    if len(chat_history) > 50:
        chat_history.pop(0)
        
    print(f"Sparat meddelande från {data['user']}")
    send(data, broadcast=True)

@socketio.on('clear_chat')
def handle_clear():
    # Rensa chatthistoriken
    global chat_history
    chat_history = []  
    print("Chatten har rensats av en användare.")
    
    emit('chat_cleared', broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)