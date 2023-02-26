import pandas as pd
import json


def refactor_values(data):
    new_data = {}
    for key, value in data.items():
        if value != '':
            new_data[key] = value
        if isinstance(value, str) and '<' in value:
            new_value = value.split('<')[1]
            new_data[key] = int(new_value)
    return new_data


def process_data(src, dist):
    f = open(src, 'r', encoding='utf-8')
    raw = json.load(f)
    f.close()

    df = pd.DataFrame()

    print('Transforming json to pandas dataframe...')
    # prilagodimo json dataframe-u
    for i in range(len(raw)):
        jdata = json.loads(raw[i]['json'])
        station = jdata['arsopodatki']['postaja']
        for i in range(len(station)):
            data = station[i]
            data = refactor_values(data)
            df = pd.concat([df, pd.json_normalize(data)])

    print('Filling missing numerical data...')
    # nadomestimo numericne podatke
    num_cols = df.select_dtypes(include=['number']).columns
    for col in num_cols:
        df[col].fillna((df[col].mean()), inplace=True)

    print('Transforming categorical data...')
    # kategoricni podatki
    df_location = pd.get_dummies(df['merilno_mesto'])
    df = pd.concat([df, df_location], axis=1).reindex(df.index)

    print('Dropping unuseful columns...')
    # neuporabni podatki
    df.pop('merilno_mesto')
    df.pop('sifra')
    df.pop('datum_od')
    df.pop('datum_do')

    print('Saving processed data...')
    df.to_csv(dist, index=False)

    print('Finished!')


if __name__ == '__main__':
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    src = os.path.join(root_dir, 'data', 'raw', 'data.json')
    dist = os.path.join(root_dir, 'data', 'processed', 'data.csv')

    process_data(src, dist)
