import pandas as pd
import numpy as np
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.gaussian_process import GaussianProcessClassifier

class Facade:
    def __init__(self, models) -> None:
        self.models = models

    def fit(self, X, y):
        for model in self.models:
            model.fit(X, y)

    def predict(self, X):
        predictions = []

        for model in self.models:
            predictions.append(model.predict(X))

        predictions = np.vstack(predictions)
        result = np.zeros(predictions.shape[1])
        for i in range(predictions.shape[1]):
            result[i] = np.bincount(predictions[:, i]).argmax()

        return result

if __name__ == "__main__":
    data = load_iris()
    X, y = data.data, data.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=True)

    models = [LogisticRegression(), GaussianProcessClassifier(), LinearSVC(max_iter=1000)]

    ensamble = Facade(models)
    ensamble.fit(X_train, y_train)
    predict = ensamble.predict(X_test)
    print(predict)