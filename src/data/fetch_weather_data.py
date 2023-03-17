import json
import requests
import datetime
import os

root_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..'))
we = os.path.join(root_dir, 'data', 'raw', 'weather', 'data.json')

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
