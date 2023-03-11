import pickle
import numpy as np
import pandas as pd
from flask import Flask
from flask import request
import json
from flask import jsonify
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
    raw = json.load(object_json)
    df = reorder(raw)

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    model_path = os.path.join(root_dir, 'models', 'var_model')

    f = open(model_path, 'rb')
    model = pickle.load(f)

    predictions = model.forecast(df.values, steps=72)
    return jsonify({'predictions': predictions})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
