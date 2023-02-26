import pickle
import numpy as np
import pandas as pd
from flask import Flask
from flask import request
import json
from flask import jsonify
import os

app = Flask(__name__)


@app.route('/air/predict/', methods=['POST'])
def predict():
    object_json = request.json
    df = pd.json_normalize(object_json)

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    model_path = os.path.join(root_dir, 'models', 'linear')

    f = open(model_path, 'rb')
    model = pickle.load(f)

    prediction = model.predict(df)
    return jsonify({'prediction': prediction[0]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
