# predict_model.py

import numpy as np
import pandas as pd
from pandas import read_csv
from pandas.tseries.offsets import DateOffset
from keras.models import load_model
import joblib  # For loading the scaler
import matplotlib.pyplot as plt

# Load and preprocess data
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
n_input = int(len(train) * 0.3)  # Set n_input to 10% of the length of the training data
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

# Concatenate the original data with the predicted data
df_proj = pd.concat([df, df_predict], axis=1)

# Save the predicted data to a CSV file
df_predict = df_predict.round(1)  # Round the predictions for better readability
df_predict.to_csv('result.csv')  # Save predictions to a CSV file
print(df_predict)
# Plot the predictions for the next 7 days
plt.figure(figsize=(20, 10))
plt.plot(df_proj.index, df_proj["Hum1Pred"], marker='o', label="Hum1Pred", color='g')
plt.plot(df_proj.index, df_proj["Hum2Pred"], marker='*', label="Hum2Pred", color='r')
plt.plot(df_proj.index, df_proj["MaxTempPred"], marker='v', label="MaxTempPred", color='b')
plt.plot(df_proj.index, df_proj["MinTempPred"], marker='d', label="MinTempPred", color='m')

plt.legend()
plt.title("Next 7 Days Weather Predictions")
plt.xlabel("Date")
plt.ylabel("Weather Values (Humidity and Temperature)")
plt.grid(True)
plt.show()
