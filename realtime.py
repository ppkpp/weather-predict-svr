from flask import Flask
from flask_socketio import SocketIO, send, emit

# Initialize Flask application
app = Flask(__name__)

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return "Socket.IO server is running"

@socketio.on('message')
def handle_message(msg):
    """Handle incoming messages and broadcast them."""
    print('Message received: ' + msg)
    send(msg, broadcast=True)

@socketio.on('custom_event')
def handle_custom_event(data):
    """Handle custom events and emit a response."""
    print(f'Custom event received with data: {data}')
    emit('response_event', {'response': 'This is a response to your custom event'})

if __name__ == '__main__':
    # Run the Flask application with SocketIO
    socketio.run(app, host='0.0.0.0', port=8889)
