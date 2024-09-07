from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime, timedelta

from flask_socketio import SocketIO, send, emit

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SECRET_KEY"] = "mysecret"

db = SQLAlchemy(app)
admin = Admin(app)
socketio = SocketIO(app)

weather_data = [
    {"date": "2024-09-01", "temperature": 22, "humidity": 60, "carbon": 400},
    {"date": "2024-09-02", "temperature": 24, "humidity": 55, "carbon": 420},
    {"date": "2024-09-03", "temperature": 19, "humidity": 70, "carbon": 430},
    {"date": "2024-09-04", "temperature": 23, "humidity": 65, "carbon": 410},
    {"date": "2024-09-05", "temperature": 21, "humidity": 60, "carbon": 415},
    {"date": "2024-09-06", "temperature": 25, "humidity": 50, "carbon": 425},
    {"date": "2024-09-07", "temperature": 20, "humidity": 55, "carbon": 405}
]

class Sensors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    carbon = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.now)
    node = db.Column(db.String(80))

class SensorView(ModelView):
    can_delete = False
    can_export = True
    form_columns = ["temperature", "humidity", "carbon", "created_date", "node"]
    column_list = ["temperature", "humidity", "carbon", "created_date", "node"]
    page_size = 100
    column_searchable_list = ['created_date', 'node']
    column_default_sort = ('created_date', False)

admin.add_view(SensorView(Sensors, db.session))

@app.route('/graph')
def graphs():
    return render_template('graphs.html')

@app.route('/vdata')
def vdata():
   return jsonify(weather_data)


@app.route('/data')
def data():
    # Calculate the start and end dates for the past week
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Query the Sensors table for data from the past week
    weather_data = Sensors.query.filter(Sensors.created_date.between(start_date, end_date)).all()

    # Format the data
    formatted_data = [
        {
            'date': sensor.created_date.strftime('%Y-%m-%d'),
            'temperature': sensor.temperature,
            'humidity': sensor.humidity,
            'carbon': sensor.carbon
        }
        for sensor in weather_data
    ]

    return jsonify(formatted_data)

@app.route('/')
def index():
    # Query for the last week's data
    one_week_ago = datetime.now() - timedelta(days=7)
    weather_data = Sensors.query.filter(Sensors.created_date >= one_week_ago).all()

    # Convert query results to a list of dictionaries
    weather_data_list = [
        {
            'date': data.created_date.strftime('%Y-%m-%d'),
            'temperature': data.temperature,
            'humidity': data.humidity,
            'carbon': data.carbon
        }
        for data in weather_data
    ]

    # Pass the weather_data list to the template
    return render_template('index.html', weather_data=weather_data_list)

@socketio.on('message')
def handle_message(msg):
    print('Message received: ' + msg)
    send(msg, broadcast=True)  # Broadcasts the message to all connected clients

@socketio.on('custom_event')
def handle_custom_event(data):
    print(f'Custom event received with data: {data}')
    emit('response_event', {'response': 'This is a response to your custom event'})

@app.route('/sensors', methods=['GET', 'POST'])
def save_sensor_data():
    content = request.json
    date_obj = datetime.strptime(content["createdate"], "%Y-%m-%d %H:%M")
    sensor_data = Sensors(
        temperature=float(content["temperature"]),
        humidity=float(content["humidity"]),
        carbon=float(content["carbon"]),
        created_date=date_obj,
        node=content["node"]
    )
    db.session.add(sensor_data)
    db.session.commit()
    print(content)
    return request.json

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True, port=8000)
