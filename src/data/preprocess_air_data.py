import pandas as pd
import json
import os


def refactor_values(data):
    new_data = {}
    for key, value in data.items():
        if value != '':
            new_data[key] = value
        if isinstance(value, str) and '<' in value:
            new_value = value.split('<')[1]
            new_data[key] = int(new_value)
    return new_data


def main():
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    air = os.path.join(root_dir, 'data', 'raw', 'data.json')
    air_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_air.csv')

    print('Processing air data...')

    f = open(air, 'r', encoding='utf-8')
    raw = json.load(f)
    f.close()

    df = pd.DataFrame()

    print('Json to data frame...')
    # prilagodimo json dataframe-u
    for i in range(len(raw)):
        jdata = json.loads(raw[i]['json'])
        station = jdata['arsopodatki']['postaja']
        for i in range(len(station)):
            if station[i]['merilno_mesto'] == 'MB Titova':
                data = station[i]
                data = refactor_values(data)
                df = pd.concat([df, pd.json_normalize(data)])

    print('Fill in missing data...')
    df = df[['datum_od', 'pm10']]
    df['pm10'].fillna((df['pm10'].mean()), inplace=True)
    df['datum_od'] = pd.to_datetime(df['datum_od'])
    df = df.sort_values(by='datum_od')
    df = df.drop_duplicates(subset='datum_od')

    df['date'] = df['datum_od']
    df = df.drop(columns='datum_od')

    print('Saving processed data')
    df.to_csv(air_proc, index=False)


if __name__ == '__main__':
    main()
