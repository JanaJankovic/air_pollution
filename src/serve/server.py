import pickle
import pandas as pd
from flask import Flask
from flask import request
import os

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
