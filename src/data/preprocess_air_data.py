import pandas as pd
import json
import os


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
                df = pd.concat([df, pd.json_normalize(data)])

    df = df[['datum_od', 'pm10']]
    print('Saving processed data')
    df.to_csv(air_proc, index=False)


if __name__ == '__main__':
    main()
