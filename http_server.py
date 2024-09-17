# http_server.py
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime, timedelta

app = Flask(__name__)
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db.sqlite3")
app.config["SECRET_KEY"] = "mysecret"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
admin = Admin(app)

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
    temperature2 = db.Column(db.Float)
    humidity2 = db.Column(db.Float)
    carbon2 = db.Column(db.Float)
    created_date = db.Column(db.DateTime, default=datetime.now)
    node = db.Column(db.String(80))

class SensorView(ModelView):
    can_delete = False
    can_export = True
    form_columns = ["temperature", "humidity", "carbon","temperature2", "humidity2", "carbon2", "created_date", "node"]
    column_list = ["temperature", "humidity", "carbon","temperature2", "humidity2", "carbon2", "created_date", "node"]
    page_size = 100
    column_searchable_list = ['created_date', 'node']
    column_default_sort = ('created_date', False)
    column_labels = {
        'temperature': 'Temperature(Day)',
        'temperature2': 'Temperature(Night)',
        'humidity': 'Humidity(Day)',
        'humidity2': 'Humidity(Night)',
        'carbon': 'Carbon(Day)',
        'carbon2': 'Carbon(Night)'
    }

admin.add_view(SensorView(Sensors, db.session))

@app.route('/graph')
def graphs():
    return render_template('graphs.html')

@app.route('/predict')
def predict():
    return render_template('lstm.html')

@app.route('/vdata')
def vdata():
   return jsonify(weather_data)

@app.route('/data')
def data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    weather_data = Sensors.query.filter(Sensors.created_date.between(start_date, end_date)).all()
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
    one_week_ago = datetime.now() - timedelta(days=7)
    weather_data = Sensors.query.filter(Sensors.created_date >= one_week_ago).all()
    weather_data_list = [
        {
            'date': data.created_date.strftime('%Y-%m-%d'),
            'temperature': data.temperature,
            'humidity': data.humidity,
            'carbon': data.carbon
        }
        for data in weather_data
    ]
    return render_template('index.html', weather_data=weather_data_list)

@app.route('/sensors', methods=['POST'])
def post_sensor_data():
    data = request.get_json()
    current_hour = datetime.now().hour
    today = datetime.now().date()
    sensor_entry = Sensors.query.filter(db.func.date(Sensors.created_date) == today).first()
    if 0 <= current_hour < 12:
        if sensor_entry:
            return jsonify({'message': 'Day data already exists, skipping insert.'}), 200
        else:
            new_sensor = Sensors(
                temperature=data.get('temperature', None),
                humidity=data.get('humidity', None),
                carbon=data.get('carbon', None),
                created_date=datetime.now(),
                node=data.get('node', None)
            )
            db.session.add(new_sensor)
            db.session.commit()
            return jsonify({'message': 'Day data added successfully'}), 201
    else:
        if sensor_entry:
            if sensor_entry.temperature2 is not None and sensor_entry.humidity2 is not None and sensor_entry.carbon2 is not None:
                return jsonify({'message': 'Night data already updated, skipping update.'}), 200
            else:
                sensor_entry.temperature2 = data.get('temperature', sensor_entry.temperature2)
                sensor_entry.humidity2 = data.get('humidity', sensor_entry.humidity2)
                sensor_entry.carbon2 = data.get('carbon', sensor_entry.carbon2)
                db.session.commit()
                return jsonify({'message': 'Night data updated successfully'}), 200
        else:
            return jsonify({'error': 'No corresponding day data found'}), 404
    return jsonify({'error': 'Invalid request'}), 400

@app.route('/train', methods=['GET'])
def train_model():
    # Training code here
    return jsonify({"message": "Model trained and saved successfully!"})

@app.route('/predict_result', methods=['GET'])
def predict_weather():
    # Prediction code here
    return jsonify(predictions_dict)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8888)
