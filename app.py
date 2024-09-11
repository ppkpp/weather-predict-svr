from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import Column, Integer, Float, DateTime, String
from datetime import datetime, timedelta

from flask_socketio import SocketIO, send, emit
import numpy as np
import pandas as pd
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.preprocessing.sequence import TimeseriesGenerator
import joblib
from keras.models import load_model
from pandas.tseries.offsets import DateOffset
app = Flask(__name__)
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "db.sqlite3")
app.config["SECRET_KEY"] = "mysecret"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
def predcit():
    return render_template('lstm.html')
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
"""
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
    return request.json"""


@app.route('/sensors', methods=['POST'])
def post_sensor_data():
    data = request.get_json()
    current_hour = datetime.now().hour
    
    # Get today's date
    today = datetime.now().date()
    
    # Check if a sensor entry for today already exists
    sensor_entry = Sensors.query.filter(db.func.date(Sensors.created_date) == today).first()
    
    if 0 <= current_hour < 12:
        # Insert data for day columns if it doesn't already exist
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
        # Update the night columns if they haven't been updated yet
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
    # Load and preprocess static data (file path is hardcoded)
    file_path = 'predict/weatherKZZM.csv'
    df = read_csv(file_path, usecols=[0, 3, 4, 5, 6,7,8], engine='python')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index("Date")

    # Split the data into training and testing sets
    train = df[:-12]  # Use all but last 12 rows for training

    # Scale the data to be between 0 and 1
    scaler = MinMaxScaler()
    scaler.fit(train)
    train = scaler.transform(train)

    # Set dynamic input and features
    n_input = int(len(train) * 0.3)
    n_features = train.shape[1]

    if n_input < 1:
        n_input = 1

    # Create the TimeseriesGenerator for LSTM
    generator = TimeseriesGenerator(train, train, length=n_input, batch_size=4)

    # Build the LSTM model
    model = Sequential()
    model.add(LSTM(200, activation="relu", input_shape=(n_input, n_features)))
    model.add(Dropout(0.15))
    model.add(Dense(n_features))
    model.compile(optimizer="adam", loss="mse")

    # Train the model
    model.fit(generator, epochs=100)

    # Save the trained model and scaler
    model.save('predict/weather_prediction_model.h5')
    joblib.dump(scaler, 'predict/scaler.save')

    return jsonify({"message": "Model trained and saved successfully!"})


@app.route('/predict_result', methods=['GET'])
def predict_weather():

    df = read_csv('predict/weatherKZZM.csv', usecols=[0, 3, 4, 5, 6,7,8], engine='python')  # Adjust the file path as needed
    df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' column is in datetime format
    df = df.set_index("Date")  # Set 'Date' as the index

    # Load the scaler
    scaler = joblib.load('predict/scaler.save')

    # Split the data into training and testing sets
    train = df[:-12]  # Use all but last 12 rows for training

    # Scale the data
    train = scaler.transform(train)

    # Dynamic adjustment for LSTM model parameters
    n_input = int(len(train) * 0.3)  # Set n_input to 30% of the length of the training data
    n_features = train.shape[1]  # Automatically adjust to the number of features in the data

    # Load the pretrained model
    model = load_model('predict/weather_prediction_model.h5')

    # Use the last sequence from training data to predict
    batch = train[-n_input:].reshape((1, n_input, n_features))

    # Generate predictions for the next 7 days
    n_days_to_predict = 7
    pred_list = []
    for i in range(n_days_to_predict):
        pred = model.predict(batch)[0]
        pred_list.append(pred)
        batch = np.append(batch[:, 1:, :], [[pred]], axis=1)

    # Prepare future dates for the predictions
    add_dates = [df.index[-1] + DateOffset(days=x) for x in range(1, n_days_to_predict + 1)]
    future_dates = pd.DataFrame(index=add_dates, columns=df.columns)  # Prepare an empty DataFrame for future dates

    # Inverse transform the predictions to their original scale
    df_predict = pd.DataFrame(scaler.inverse_transform(pred_list), index=future_dates.index,
                              columns=["Hum1Pred", "Hum2Pred", "MaxTempPred", "MinTempPred","carbon1","carbon2"])

    # Convert the DataFrame to a dictionary
    predictions_dict = df_predict.reset_index().to_dict(orient='records')

    # Return the result as a JSON response
    return jsonify(predictions_dict)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', debug=True, port=8888)
