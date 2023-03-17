import pandas as pd
import pickle
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np


def predict_model(data_path, model_path, train_metrics_path, metrics_path):
    csv = pd.read_csv(data_path, encoding='utf_8')
    df = pd.DataFrame(csv)
    df = df.drop(columns='date')
    print('Data read')

    columns = np.array(df.columns)
    mask = columns != 'pm10'
    x_train, x_test, y_train, y_test = train_test_split(
        df[columns[mask]], df['pm10'], test_size=0.3, random_state=1234, shuffle=True)
    model = LinearRegression()
    model.fit(x_train, y_train)
    print('Model trained')

    prediction = model.predict(x_test)

    # Calculate MSE and MAE for the test data
    mse_test = mean_squared_error(y_test, prediction)
    mae_test = mean_absolute_error(y_test, prediction)
    evs_test = explained_variance_score(y_test, prediction)

    # Make predictions for the training data
    predictions_train = model.predict(x_train)

    # Calculate MSE and MAE for the training data
    mse_train = mean_squared_error(y_train, predictions_train)
    mae_train = mean_absolute_error(y_train, predictions_train)
    evs_train = explained_variance_score(y_train, predictions_train)

    with open(train_metrics_path, 'w') as file:
        file.write('MAE:' + str(mae_train) + '\n')
        file.write('MSE:' + str(mse_train) + '\n')
        file.write('EVS:' + str(evs_train) + '\n')

    with open(metrics_path, 'w') as file:
        file.write('MAE:' + str(mae_test) + '\n')
        file.write('MSE:' + str(mse_test) + '\n')
        file.write('EVS:' + str(evs_test) + '\n')

    print('Reports updated')

    with open(model_path, 'wb') as f:
        pickle.dump(model, f)

    print('Model serialized')


if __name__ == '__main__':
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    data_path = os.path.join(root_dir, 'data', 'processed', 'data.csv')
    model_path = os.path.join(root_dir, 'models', 'model.pickle')
    train_metrics_path = os.path.join(root_dir, 'reports', 'train_metrics.txt')
    metrics_path = os.path.join(root_dir, 'reports', 'metrics.txt')

    predict_model(data_path, model_path, train_metrics_path, metrics_path)
