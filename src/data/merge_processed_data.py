import pandas as pd
import os


def main():
    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    air_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_air.csv')
    we_proc = os.path.join(root_dir, 'data', 'preprocessed', 'data_we.csv')
    merged = os.path.join(root_dir, 'data', 'processed', 'current_data.csv')

    print('Merging data...')
    csv = pd.read_csv(air_proc, encoding='utf_8')
    df = pd.DataFrame(csv)
    df = df.rename(columns={'datum_od': 'date'})

    csv = pd.read_csv(we_proc, encoding='utf_8')
    df1 = pd.DataFrame(csv)

    df['date'] = pd.to_datetime(df['date'])
    df1['date'] = pd.to_datetime(df1['date'])

    merged_df = pd.merge(df1, df, on='date', how='inner')
    merged_df = merged_df.drop(columns='date')

    print('Saving processed data...')
    merged_df.to_csv(merged, index=False)

    print('Finished!')


if __name__ == '__main__':
    main()
