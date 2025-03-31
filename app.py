from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Dictionary to store connected users (key: socket id, value: user details)
users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    username = f"User_{random.randint(1000,9999)}"
    gender = random.choice(["male", "female"])
    
    # Set avatar URL based on gender
    if gender == "male":
        avatar_url = "https://th.bing.com/th/id/OIP.PMhANanxddOBObcYxcYOcwHaGy?w=860&h=789&rs=1&pid=ImgDetMain"
    else:
        avatar_url = "https://www.pngkey.com/png/full/115-1150152_default-profile-picture-avatar-png-green.png"
    
    users[request.sid] = {'username': username, 'avatar_url': avatar_url}

    # Emit with property name "avatar" to match the client-side expectation
    emit('user_connected', {'username': username, 'avatar': avatar_url}, broadcast=True)
    emit("set_username", {"username": username})

@socketio.on('disconnect')
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        print(f'{user["username"]} disconnected')
        emit('user_disconnected', {'username': user['username']}, broadcast=True)

@socketio.on('send_message')
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user['username'],
            "avatar": user['avatar_url'],  # Using "avatar" key for client compatibility
            "message": data['message']
        }, broadcast=True)

@socketio.on('update_username')
def handle_update_username(data):
    old_username = users[request.sid]['username']
    new_username = data['username']
    users[request.sid]['username'] = new_username

    emit('username_updated', {'old_username': old_username, 'new_username': new_username}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)
