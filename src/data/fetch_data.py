import pandas as pd
import json
import requests
import datetime
import os

root_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..'))

air = os.path.join(root_dir, 'data', 'raw', 'data.json')
we = os.path.join(root_dir, 'data', 'raw', 'weather', 'data.json')
air_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_air.csv')
we_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_we.csv')
merged = os.path.join(root_dir, 'data', 'processed', 'data.csv')


def fetch_air_data():
    print('Fetching air data...')
    url = "https://arsoxmlwrapper.app.grega.xyz/api/air/archive"
    response = requests.get(url)
    if response.status_code == 200:
        print("Fetched main datset")
        data = json.loads(response.content)
        with open(air, "w") as f:
            json.dump(data, f)
    else:
        print("Failed to retrieve JSON data")


def fetch_weather_data():
    print('Fetching weather data...')
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
        with open(we, "w") as f:
            json.dump(data, f)
    else:
        print("Failed to retrieve JSON data")


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


def process_air_data():
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
    df = df.drop_duplicates(subset='datum_od', keep='first')
    df.to_csv(air_proc, index=False)


def process_weather_data():
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

    df['percp'] = raw['hourly']['precipitation']
    df['percp'].fillna(df['percp'].mean(), inplace=True)

    df['wspeed'] = raw['hourly']['windspeed_10m']
    df['wspeed'].fillna(df['wspeed'].mean(), inplace=True)

    df.to_csv(we_proc, index=False)


def merge_processed_data():
    print('Merging data...')
    csv = pd.read_csv(air_proc, encoding='utf_8')
    df = pd.DataFrame(csv)

    csv = pd.read_csv(we_proc, encoding='utf_8')
    df1 = pd.DataFrame(csv)

    start = df['datum_od'].iloc[0]
    end = df['datum_od'].iloc[-1]

    start_index = df1.loc[df1['date'] == start].index[0]
    end_index = df1.loc[df1['date'] == end].index[0]
    df1 = df1.iloc[start_index:end_index]

    df = df.reset_index(drop=True)
    df1 = df1.reset_index(drop=True)

    df1['pm10'] = df.loc[:, 'pm10']

    print('Saving processed data...')
    df1.to_csv(merged, index=False)

    print('Finished!')


if __name__ == '__main__':
    fetch_air_data()
    fetch_weather_data()
    process_air_data()
    process_weather_data()
    merge_processed_data()
