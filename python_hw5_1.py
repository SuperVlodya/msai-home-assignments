import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


class Builder:
    def __init__(self, X_train, y_train):
        self.X_train = X_train
        self.y_train = y_train
        self.random_seed = 0

    def set_random_seed(self, seed):
        self.random_seed = seed

    def get_subsample(self, df_share):
        X = self.X_train.copy()
        y = self.y_train.copy()
        X, y = shuffle(X, y, random_state=self.random_seed)
        indexes = int((df_share / 100) * len(y))
        return X[:indexes], y[:indexes]


if __name__ == "__main__":
    iris = load_iris()
    iris_df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
    X = iris_df.drop(labels='sepal length (cm)', axis=1)
    y = iris_df['sepal length (cm)']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=101)

    pattern_item = Builder(X_train, y_train)
    pattern_item.set_random_seed(42)
    for df_share in range(10, 101, 10):
        curr_X_train, curr_y_train = pattern_item.get_subsample(df_share)
        lr = LinearRegression()
        lr.fit(curr_X_train, curr_y_train)

        lr.predict(X_test)
        pred = lr.predict(X_test)

        print(f'MSE at {df_share}:', mean_squared_error(y_test, pred))