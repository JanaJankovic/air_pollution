import pandas as pd

csv = pd.read_csv('data/processed/current_data.csv', encoding='utf_8')
df = pd.DataFrame(csv)

null_rows = df[df['pm10'].isnull()]

print(null_rows)
