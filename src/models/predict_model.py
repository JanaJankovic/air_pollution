import pandas as pd
import pickle
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
from statsmodels.tsa.vector_ar.var_model import VAR


def predict_model(data_path, model_path, train_metrics_path, metrics_path):
    csv = pd.read_csv(data_path, encoding='utf_8')
    df = pd.DataFrame(csv)
    df = df.drop(columns='date')
    print('Data read')

    # Set the lags to 72
    lags = 72

    # Split the data into training and testing sets
    train = df[:-lags]
    test = df[-lags:]

    # Fit a VAR model with 72 lags
    model = VAR(train)
    results = model.fit(lags)

    # Make predictions for the next 3 days
    predictions = results.forecast(test.values, steps=lags)

    # Convert the predictions back to a DataFrame
    predictions = pd.DataFrame(
        predictions, columns=df.columns, index=test.index)

    print('Model trained')

    # Calculate MSE and MAE for the test data
    mse_test = mean_squared_error(test, predictions)
    mae_test = mean_absolute_error(test, predictions)
    evs_test = explained_variance_score(test, predictions)

    # Make predictions for the training data
    predictions_train = results.fittedvalues

    train = train[lags:]
    # Calculate MSE and MAE for the training data
    mse_train = mean_squared_error(train, predictions_train)
    mae_train = mean_absolute_error(train, predictions_train)
    evs_train = explained_variance_score(train, predictions_train)

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
        pickle.dump(results, f)

    print('Model serialized')


if __name__ == '__main__':
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    data_path = os.path.join(root_dir, 'data', 'processed', 'data.csv')
    model_path = os.path.join(root_dir, 'models', 'var_model')
    train_metrics_path = os.path.join(root_dir, 'reports', 'train_metrics.txt')
    metrics_path = os.path.join(root_dir, 'reports', 'metrics.txt')

    predict_model(data_path, model_path, train_metrics_path, metrics_path)
