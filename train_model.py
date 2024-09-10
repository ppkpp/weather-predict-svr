# train_model.py

import numpy as np
import pandas as pd
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.preprocessing.sequence import TimeseriesGenerator

# Load and preprocess data
df = read_csv('predict/weatherKZZM.csv', usecols=[0, 3, 4, 5, 6,7,8], engine='python')  # Adjust the file path as needed
df['Date'] = pd.to_datetime(df['Date'])  # Ensure 'Date' column is in datetime format
df = df.set_index("Date")  # Set 'Date' as the index

# Split the data into training and testing sets
train = df[:-12]  # Use all but last 12 rows for training

# Scale the data to be between 0 and 1
scaler = MinMaxScaler()
scaler.fit(train)  # Fit scaler on the training data
train = scaler.transform(train)

# Dynamic adjustment for LSTM model parameters
n_input = int(len(train) * 0.3)  # Set n_input to 10% of the length of the training data
n_features = train.shape[1]  # Automatically adjust to the number of features in the data

# Check to ensure n_input is a reasonable value
if n_input < 1:
    n_input = 1  # Ensure n_input is at least 1

# Use TimeseriesGenerator for LSTM
generator = TimeseriesGenerator(train, train, length=n_input, batch_size=4)

# Build the LSTM model
model = Sequential()
model.add(LSTM(200, activation="relu", input_shape=(n_input, n_features)))
model.add(Dropout(0.15))  # Dropout to avoid overfitting
model.add(Dense(n_features))  # Output layer with the same number of features
model.compile(optimizer="adam", loss="mse")  # Compile the model

# Train the model
model.fit(generator, epochs=20)

# Save the trained model
model.save('predict/weather_prediction_model.h5')  # Save the model for future predictions

# Save the scaler for use in the prediction file
import joblib
joblib.dump(scaler, 'predict/scaler.save')
