import pandas as pd
import json
import requests
import datetime


# for avoiding weird data like <4 and null


def refactor_values(data):
    new_data = {}
    for key, value in data.items():
        if value != '':
            new_data[key] = value
        if isinstance(value, str) and '<' in value:
            new_value = value.split('<')[1]
            new_data[key] = int(new_value)
    return new_data


def process_data(src, src1, dist):
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
            if station[i]['merilno_mesto'] == 'MB Titova':
                data = station[i]
                data = refactor_values(data)
                df = pd.concat([df, pd.json_normalize(data)])

    print('Connecting data...')

    df = df[['datum_od', 'pm10']]
    df['pm10'].fillna((df['pm10'].mean()), inplace=True)
    df['datum_od'] = pd.to_datetime(df['datum_od'])
    df = df.sort_values(by='datum_od')
    df = df.drop_duplicates(subset='datum_od', keep='first')

    f = open(src1, 'r', encoding='utf-8')
    raw = json.load(f)
    f.close()

    df1 = pd.DataFrame()
    df1['date'] = raw['hourly']['time']
    df1['date'] = pd.to_datetime(df1['date'])

    df1['temp'] = raw['hourly']['temperature_2m']
    df1['temp'].fillna(df1['temp'].mean(), inplace=True)

    df1['hum'] = raw['hourly']['relativehumidity_2m']
    df1['hum'].fillna(df1['hum'].mean(), inplace=True)

    df1['percp'] = raw['hourly']['precipitation_probability']
    df1['percp'].fillna(df1['percp'].mean(), inplace=True)

    df1['wspeed'] = raw['hourly']['windspeed_10m']
    df1['wspeed'].fillna(df1['wspeed'].mean(), inplace=True)

    start = df['datum_od'].iloc[0]
    end = df['datum_od'].iloc[-1]

    start_index = df1.loc[df1['date'] == start].index[0]
    end_index = df1.loc[df1['date'] == end].index[0]
    df1 = df1.iloc[start_index:end_index]

    df = df.reset_index(drop=True)
    df1 = df1.reset_index(drop=True)

    df1['pm10'] = df.loc[:, 'pm10']

    print('Saving processed data...')
    df1.to_csv(dist, index=False)

    print('Finished!')


def fetch_data(src):
    url = "https://arsoxmlwrapper.app.grega.xyz/api/air/archive"
    response = requests.get(url)
    if response.status_code == 200:
        print("Fetched main datset")
        data = json.loads(response.content)
        with open(src, "w") as f:
            json.dump(data, f)
    else:
        print("Failed to retrieve JSON data")


def fetch_other_data(src1):
    # Get the current date and time
    current_date = datetime.datetime.now()

    # Get the date one month ago
    one_month_ago = current_date - datetime.timedelta(days=30)

    # Convert dates to Unix time
    current_unix_time = int(current_date.timestamp())
    one_month_ago_unix_time = int(one_month_ago.timestamp())

    lat = '46.5547222'
    lon = '15.6466667'

    end_date = datetime.datetime.utcfromtimestamp(
        current_unix_time).strftime('%Y-%m-%d')
    start_date = datetime.datetime.utcfromtimestamp(
        one_month_ago_unix_time).strftime('%Y-%m-%d')

    url = f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start_date}&end_date={end_date}&hourly=temperature_2m,relativehumidity_2m,precipitation,windspeed_10m'
    response = requests.get(url)
    if response.status_code == 200:
        print("Fetched weather history")
        data = json.loads(response.content)
        with open(src1, "w") as f:
            json.dump(data, f)
    else:
        print("Failed to retrieve JSON data")


if __name__ == '__main__':
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    src = os.path.join(root_dir, 'data', 'raw', 'data.json')
    dist = os.path.join(root_dir, 'data', 'processed', 'data.csv')

    src1 = os.path.join(root_dir, 'data', 'raw', 'weather', 'data.json')

    fetch_data(src)
    fetch_other_data(src1)
    process_data(src, src1, dist)
