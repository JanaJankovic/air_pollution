import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn import metrics
import pickle


def predict_model(data_path, model_path, train_metrics_path, metrics_path):
    csv_dataset = data_path
    csv = pd.read_csv(csv_dataset, encoding='utf_8')
    df = pd.DataFrame(csv)
    print('Data read')

    columns = np.array(df.columns)
    mask = columns != 'pm10'

    x_train, x_test, y_train, y_test = train_test_split(
        df[columns[mask]], df['pm10'], test_size=0.3, random_state=1234, shuffle=True)
    model = LinearRegression()
    model.fit(x_train, y_train)
    print('Model trained')

    pickle.dump(model, open(model_path, 'wb'))
    print('Model saved')

    prediction = model.predict(x_train)

    with open(train_metrics_path, 'w') as file:
        file.write(
            'MAE:' + str(metrics.mean_absolute_error(y_train, prediction, )) + '\n')
        file.write(
            'MSE:' + str(metrics.mean_squared_error(y_train, prediction)) + '\n')
        file.write(
            'EVS:' + str(metrics.explained_variance_score(y_train, prediction)) + '\n')

    prediction = model.predict(x_test)

    with open(metrics_path, 'w') as file:
        file.write(
            'MAE:' + str(metrics.mean_absolute_error(y_test, prediction, )) + '\n')
        file.write(
            'MSE:' + str(metrics.mean_squared_error(y_test, prediction)) + '\n')
        file.write(
            'EVS:' + str(metrics.explained_variance_score(y_test, prediction)) + '\n')

    print('Metrics saved')


if __name__ == '__main__':
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    data_path = os.path.join(root_dir, 'data', 'processed', 'data.csv')
    model_path = os.path.join(root_dir, 'models', 'linear')
    train_metrics_path = os.path.join(root_dir, 'reports', 'train_metrics.txt')
    metrics_path = os.path.join(root_dir, 'reports', 'metrics.txt')

    predict_model(data_path, model_path, train_metrics_path, metrics_path)
