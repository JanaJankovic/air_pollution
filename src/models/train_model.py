import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, explained_variance_score
import numpy as np
import mlflow
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import GridSearchCV
from mlflow.models.signature import infer_signature
from mlflow import MlflowClient


class CategoricalTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return transform_categorical(X)


def transform_categorical(column):
    pm10 = column['pm10']
    pm10 = pm10.str.replace('<', '')
    nan_mask = pm10.isna()
    pm10nan = pm10[nan_mask]

    pm10 = pm10.str.strip().dropna().loc[lambda x: x.str.len() > 0]
    pm10 = pm10.astype('float')

    pm10nan[:] = pm10.mean()
    pm10 = pd.concat([pm10, pm10nan], axis=0)

    column['pm10'] = pm10.astype('float')
    return column


def transform_test(test_path, categorical_transform, numerical_transform):
    csv = pd.read_csv(test_path, encoding='utf_8')
    test = pd.DataFrame(csv)
    print('Data read')

    cat_features = test.select_dtypes(include=['object']).columns.tolist()
    num_features = test.select_dtypes(
        include=['float64', 'int64']).columns.tolist()

    test_preprocessor = ColumnTransformer([
        ('pm10_transform', categorical_transform, cat_features),
        ('normal_transform', numerical_transform, num_features)
    ])

    arr = test_preprocessor.fit_transform(test)

    test = pd.DataFrame(
        arr, columns=['temp', 'hum', 'percp', 'wspeed', 'pm10'])
    return test.astype('float')


def transform_test(test_path, categorical_transform, numerical_transform):
    csv = pd.read_csv(test_path, encoding='utf_8')
    test = pd.DataFrame(csv)
    print('Data read')

    cat_features = test.select_dtypes(include=['object']).columns.tolist()
    num_features = test.select_dtypes(
        include=['float64', 'int64']).columns.tolist()

    test_preprocessor = ColumnTransformer([
        ('pm10_transform', categorical_transform, cat_features),
        ('normal_transform', numerical_transform, num_features)
    ])

    arr = test_preprocessor.fit_transform(test)
    test = pd.DataFrame(
        arr, columns=['temp', 'hum', 'percp', 'wspeed', 'pm10'])
    return test


def train_model(train_path, test_path):
    MLFLOW_TRACKING_URI = "https://dagshub.com/JanaJankovic/air_pollution.mlflow"
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("airpollution-mlruns")
    mlflow.autolog()
    csv = pd.read_csv(train_path, encoding='utf_8')
    train = pd.DataFrame(csv)

    x_train = train.drop('pm10', axis=1)
    y_train = pd.DataFrame(train['pm10'])

    num_features = ['temp', 'hum', 'percp', 'wspeed']

    categorical_transform = Pipeline([
        ('transformer', CategoricalTransformer())
    ])

    arr = categorical_transform.fit_transform(y_train)
    y_train = pd.DataFrame(arr, columns=['pm10'])

    numerical_transform = Pipeline([
        ('imputer', SimpleImputer(strategy='mean'))
    ])

    preprocessor = ColumnTransformer([
        ('numerical_transform', numerical_transform,
            num_features),
    ])

    pipe = Pipeline([
        ('preprocess', preprocessor),
        ('MLPR', MLPRegressor())
    ])

    parameter_space = {
        "MLPR__hidden_layer_sizes": [(32), (16)],
        "MLPR__learning_rate_init": [0.001, 0.01]
    }

    search = GridSearchCV(pipe, parameter_space,
                          verbose=2, error_score='raise')
    search.fit(x_train, y_train)

    test = transform_test(
        test_path, categorical_transform, numerical_transform)
    x_test = test.drop('pm10', axis=1)
    y_test = pd.DataFrame(test['pm10'])

    signature = infer_signature(x_train, search.predict(x_test))
    mlflow.sklearn.log_model(search, signature=signature, artifact_path="MLPRegressor",
                             registered_model_name="MLPRegressor")

    prediction = search.predict(x_test)

    # Calculate MSE and MAE for the test data
    mse_test = mean_squared_error(y_test, prediction)
    mae_test = mean_absolute_error(y_test, prediction)
    evs_test = explained_variance_score(y_test, prediction)

    mlflow.log_metric("MSE Test", mse_test)
    mlflow.log_metric("MAE Test", mae_test)
    mlflow.log_metric("EVS Test", evs_test)

    client = MlflowClient()
    m = client.get_latest_versions('MLPRegressor', stages=["Production"])[0]
    history = client.get_metric_history(m.run_id, key='MAE Test')

    minM = history[0].value
    for h in history:
        if h.value < minM:
            minM = h.value

    if mae_test < minM:
        print('jere')
        client.transition_model_version_stage(
            name="MLPRegressor", version=m.version, stage='Production'
        )


def main():
    import os

    root_dir = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '../..'))

    train_path = os.path.join(root_dir, 'data', 'processed', 'train.csv')
    test_path = os.path.join(root_dir, 'data', 'processed', 'test.csv')

    train_model(train_path, test_path)


if __name__ == '__main__':
    main()
