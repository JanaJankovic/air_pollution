import pandas as pd
import json
import os


def main():
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))
    we = os.path.join(root_dir, 'data', 'raw', 'weather', 'data.json')
    we_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_we.csv')

    print('Processing weather data...')
    f = open(we, 'r', encoding='utf-8')
    raw = json.load(f)
    f.close()

    df = pd.DataFrame()
    df['date'] = raw['hourly']['time']
    df['date'] = pd.to_datetime(df['date'])

    df['temp'] = raw['hourly']['temperature_2m']
    df['temp'].fillna(df['temp'].mean(), inplace=True)

    df['hum'] = raw['hourly']['relativehumidity_2m']
    df['hum'].fillna(df['hum'].mean(), inplace=True)
    df['hum'] = df['hum'].astype(float)

    df['percp'] = raw['hourly']['precipitation']
    df['percp'].fillna(df['percp'].mean(), inplace=True)

    df['wspeed'] = raw['hourly']['windspeed_10m']
    df['wspeed'].fillna(df['wspeed'].mean(), inplace=True)

    missing_values = df.isnull().sum()
    print(missing_values)

    print('Saving processed data...')
    df.to_csv(we_proc, index=False)


if __name__ == '__main__':
    main()
