import json
import requests
import os

root_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../..'))

air = os.path.join(root_dir, 'data', 'raw', 'data.json')


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
