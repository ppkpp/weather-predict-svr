import socketio
import json
import time
import random

# Create a new Socket.IO client instance
sio = socketio.Client()

# Event handler for when the client connects to the server
@sio.event
def connect():
    print('Connected to server')

# Event handler for when the client disconnects from the server
@sio.event
def disconnect():
    print('Disconnected from server')

# Event handler for receiving messages from the server
@sio.event
def message(data):
    print('Message received from server:', data)

# Function to send a message to the server
def send_message(temp, humidity, carbon, node):
    message = {
        'temp': temp,
        'humidity': humidity,
        'carbon': carbon,
        'node': node
    }
    sio.emit('message', json.dumps(message))

# Connect to the Socket.IO server
sio.connect('http://localhost:8000')  # Replace with your server URL

# Continuously send messages every 1 second
try:
    while True:
        # Generate random data
        temp = round(random.uniform(15.0, 30.0), 1)  # Temperature between 15.0 and 30.0
        humidity = random.randint(30, 80)  # Humidity between 30% and 80%
        carbon = random.randint(300, 600)  # Carbon levels between 300 and 600 ppm
        node = f'N1'  # Node identifier N1 to N10
        
        send_message(temp, humidity, carbon, node)
        
        # Wait for 1 second before sending the next message
        time.sleep(1)

except KeyboardInterrupt:
    print('Client stopped by user')
finally:
    sio.disconnect()
