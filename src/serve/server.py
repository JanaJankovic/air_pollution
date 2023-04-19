import pandas as pd
from flask import Flask
from flask_cors import CORS, cross_origin
import requests
from mlflow import MlflowClient
import mlflow
import os
import pymongo

app = Flask(__name__)

MLFLOW_TRACKING_URI = "https://dagshub.com/JanaJankovic/air_pollution.mlflow"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient()
run_id = client.get_latest_versions(
    'MLPRegressor', stages=['production'])[0].run_id
model = mlflow.pyfunc.load_model(f'runs:/{run_id}/MLPRegressor')

clientdb = pymongo.MongoClient(os.environ['MONGO_URI'])
db = clientdb.iis
col = db.prediction


def get_forecast():
    lat = '46.5547222'
    lon = '15.6466667'

    url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,windspeed_10m'
    raw = requests.get(url)
    raw = raw.json()

    df = pd.DataFrame()
    df['date'] = raw['hourly']['time']
    df['date'] = pd.to_datetime(df['date'])

    df['temp'] = raw['hourly']['temperature_2m']
    df['temp'].fillna(df['temp'].mean(), inplace=True)

    df['hum'] = raw['hourly']['relativehumidity_2m']
    df['hum'].fillna(df['hum'].mean(), inplace=True)

    df['percp'] = raw['hourly']['precipitation_probability']
    df['percp'].fillna(df['percp'].mean(), inplace=True)

    df['wspeed'] = raw['hourly']['windspeed_10m']
    df['wspeed'].fillna(df['wspeed'].mean(), inplace=True)

    return df


@app.route('/forecast', methods=['GET'])
@cross_origin()
def forecast():
    df = get_forecast()
    df_date = pd.to_datetime(df['date'])
    df_date = df_date.dt.strftime('%Y-%m-%d %H:%M:%S')
    df = df.drop(columns='date')
    df = df.astype(float)
    df['hum'] = df['hum'].astype(int)

    prediction = model.predict(df)
    df['pm10'] = prediction
    df['date'] = df_date
    df = df.head(72)

    df_dict = df.to_dict()
    json_data = {key: list(df_dict[key].values()) for key in df_dict}

    data = {
        'temp': df['temp'].tolist(),
        'hum': df['hum'].tolist(),
        'percp': df['percp'].tolist(),
        'wspeed': df['wspeed'].tolist(),
        'pm10': df['pm10'].tolist(),
        'date': df['date'].tolist(),
    }
    col.insert_one(data)

    return json_data


def main():
    app.run(host='0.0.0.0', port=5000)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})


if __name__ == '__main__':
    main()
