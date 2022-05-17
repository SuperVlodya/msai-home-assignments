from abc import ABC, abstractmethod
from sklearn.datasets import fetch_20newsgroups
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import f1_score
from xgboost import XGBClassifier
import pandas as pd

import pickle
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
from string import punctuation
import numpy as np

class BaseTagger(ABC):
    @abstractmethod
    def get_tags(self, texts):# list[str]) -> list[list[str]]:
        '''['Text1', 'Text2', ...] -> [['text1_tag1', 'text1_tag2', ...], ...]'''
        ...


class TextTagger(BaseTagger):
    def __init__(self, clf_threshold=0.2, pickle_weights="3ee33gjweights.pik"):

        self.clf_threshold = clf_threshold
        self.clf = Pipeline(
            [('tfidf', TfidfVectorizer()),
             ('svm_clf', SVC(C=0.1, degree=5, gamma=10, random_state=42))])

        data_test = fetch_20newsgroups(subset='test', shuffle=True)
        x_test = pd.DataFrame(data_test.data, columns=['text'])
        y_test = pd.DataFrame(data_test.target, columns=['target'])
        self.targets = data_test.target_names

        try:
            self.clf = pickle.load(open(pickle_weights, 'rb'))

        except FileNotFoundError as error:
            print("not fitted weights")
            data_train = fetch_20newsgroups(subset='train', shuffle=True)
            x_train = pd.DataFrame(data_train.data, columns=['text'])
            y_train = pd.DataFrame(data_train.target, columns=['target'])
            self.clf = self.clf.fit(x_train.text, y_train.target)
            preds = self.clf.predict(x_test.text)
            f1 = f1_score(y_test.target, preds, average='weighted')
            print(f"f1_score:{f1:.2f}")

            pickle.dump(self.clf, open(pickle_weights, 'wb'))

    # removes punctuation
    def remove_punct(self, text):
        table = {33: ' ', 34: ' ', 35: ' ', 36: ' ', 37: ' ', 38: ' ', 39: ' ', 40: ' ',
                 41: ' ', 42: ' ', 43: ' ', 44: ' ', 45: ' ', 46: ' ', 47: ' ', 58: ' ', 
                 59: ' ', 60: ' ', 61: ' ', 62: ' ', 63: ' ', 64: ' ', 91: ' ', 92: ' ',
                 93: ' ', 94: ' ', 95: ' ', 96: ' ', 123: ' ', 124: ' ', 125: ' ', 126: ' '}
        return text.translate(table)

    def get_tags(self, texts):
        topic = []
        topic_scores = []
        for text in texts:
            predictions = self.clf.predict_proba([text])[0].tolist()
            sorted_scores = [(predictions[i], predictions.index(predictions[i])) for i in range(len(predictions))]
            sorted_scores = sorted(sorted_scores, reverse=True, key=lambda x: x[0])
            valid_predictions = []
            valid_predictions_scores = []

            for v in range(len(sorted_scores)):
                if sorted_scores[v][0] >= self.clf_threshold:
                    valid_predictions.append(self.targets[sorted_scores[v][1]])
                    valid_predictions_scores.append(sorted_scores[v][0])
            topic.append(valid_predictions)
            topic_scores.append(valid_predictions_scores)

        return topic, topic_scores


texts = [
    "Help adding a SCSI Drive\nOriginator",
    "How to speed up games (marginally realistic)",
    "Choosing a window manager"]

tagger = TextTagger()
topic, scores = tagger.get_tags(texts)

print("predictions:\n", topic)
print(scores) 