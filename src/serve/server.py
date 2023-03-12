import pickle
import pandas as pd
from flask import Flask
from flask import request
import os
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin

app = Flask(__name__)


def reorder(data):
    new_data = pd.DataFrame()
    new_data['temp'] = data['temp']
    new_data['hum'] = data['hum']
    new_data['percp'] = data['percp']
    new_data['wspeed'] = data['wspeed']
    new_data['pm10'] = data['pm10']
    return new_data


@app.route('/air/predict/', methods=['POST'])
@cross_origin()
def predict():
    object_json = request.json
    df = reorder(object_json)

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    model_path = os.path.join(root_dir, 'models', 'var_model')

    f = open(model_path, 'rb')
    model = pickle.load(f)

    predictions = model.forecast(df.values, steps=72)
    predictions = pd.DataFrame(
        predictions, columns=df.columns, index=df.index)
    json_data = predictions.to_json(orient='records')

    return json_data


@app.route('/forecast', methods=['GET'])
@cross_origin()
def forecast():
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    data_path = os.path.join(root_dir, 'data', 'processed', 'data.csv')
    csv = pd.read_csv(data_path, encoding='utf_8')
    df = pd.DataFrame(csv)

    date_from = df['date'].tail(1).values[0]

    df = df.drop(columns='date')
    df = df.tail(72)

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    model_path = os.path.join(root_dir, 'models', 'var_model')

    f = open(model_path, 'rb')
    model = pickle.load(f)

    predictions = model.forecast(df.values, steps=72)
    predictions = pd.DataFrame(
        predictions, columns=df.columns, index=df.index)

    df_dict = predictions.to_dict()
    json_data = {key: list(df_dict[key].values()) for key in df_dict}

    start_date = datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')
    start_date += timedelta(hours=1)
    date_list = [start_date + timedelta(hours=i) for i in range(72)]
    date_str_list = [date.strftime('%Y-%m-%d %H:%M:%S') for date in date_list]
    json_data['date'] = date_str_list
    return json_data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})
