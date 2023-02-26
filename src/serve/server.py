import pickle
import numpy as np
import pandas as pd
from flask import Flask
from flask import request
import json
from flask import jsonify
import os

app = Flask(__name__)


def reorder(df):
    new_data = pd.DataFrame()
    new_data['nadm_visina'] = df['nadm_visina']
    new_data['benzen'] = df['benzen']
    new_data['ge_sirina'] = df['ge_sirina']
    new_data['ge_dolzina'] = df['ge_dolzina']
    new_data['pm2.5'] = df['pm2.5']
    new_data['o3'] = df['o3']
    new_data['co'] = df['co']
    new_data['no2'] = df['no2']
    new_data['so2'] = df['so2']
    new_data['CE Ljubljanska'] = df['CE Ljubljanska']
    new_data['CE bolnica'] = df['CE bolnica']
    new_data['Hrastnik'] = df['Hrastnik']
    new_data['Iskrba'] = df['Iskrba']
    new_data['Koper'] = df['Koper']
    new_data['Kranj'] = df['Kranj']
    new_data['Krvavec'] = df['Krvavec']
    new_data['LJ Bežigrad'] = df['LJ Bežigrad']
    new_data['LJ Celovška'] = df['LJ Celovška']
    new_data['LJ Vič'] = df['LJ Vič']
    new_data['MB Titova'] = df['MB Titova']
    new_data['MB Vrbanski'] = df['MB Vrbanski']
    new_data['MS Cankarjeva'] = df['MS Cankarjeva']
    new_data['MS Rakičan'] = df['MS Rakičan']
    new_data['NG Grčna'] = df['NG Grčna']
    new_data['Novo mesto'] = df['Novo mesto']
    new_data['Otlica'] = df['Otlica']
    new_data['Ptuj'] = df['Ptuj']
    new_data['Rečica v I.Bistrici'] = df['Rečica v I.Bistrici']
    new_data['Trbovlje'] = df['Trbovlje']
    new_data['Zagorje'] = df['Zagorje']
    return new_data


@app.route('/air/predict/', methods=['POST'])
def predict():
    object_json = request.json
    df = pd.json_normalize(object_json)
    df = reorder(df)
    print(object_json)

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    model_path = os.path.join(root_dir, 'models', 'linear')

    f = open(model_path, 'rb')
    model = pickle.load(f)

    prediction = model.predict(df)
    return jsonify({'prediction': prediction[0]})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
