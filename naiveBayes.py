import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

reviewDSPath = "Files/rotten_tomatoes_critic_reviews.csv"
moviesDSPath = "Files/rotten_tomatoes_movies.csv"

# modelo naive bayes
class NaiveBayes:
    def fit(self, X, y):
        n_docs, n_features = X.shape

        # Contar las ocurrencias de cada clase
        self.class_counts = np.bincount(y)
        self.n_classes = len(self.class_counts)

        # Contar las ocurrencias de características por clase
        self.feature_counts = np.zeros((self.n_classes, n_features))
        for c in range(self.n_classes):
            self.feature_counts[c, :] = X[y == c].sum(axis=0)

        # Calcular probabilidades logaritmicas
        self.class_log_prior = np.log(self.class_counts) - np.log(n_docs) #calcular la probabilidad logaritmica de cada clase
        self.feature_log_prob = np.log(self.feature_counts + 1) - np.log( #se suma 1 por suavizado laplace
            self.feature_counts.sum(axis=1)[:, np.newaxis] + n_features)

    def predict(self, X):
        return np.argmax(self.predict_log(X), axis=1)

    def predict_log(self, X):
        return X @ self.feature_log_prob.T + self.class_log_prior

    @staticmethod
    def getPublishers():
        data = pd.read_csv(reviewDSPath)
        data = data.dropna(subset=['publisher_name'])
        publisher_list = data['publisher_name'].astype(str).tolist()
        return publisher_list

    @staticmethod
    def getMovies():
        data = pd.read_csv(moviesDSPath)
        data = data.dropna(subset=['rotten_tomatoes_link', 'movie_title'])
        movies_list = data[['rotten_tomatoes_link', 'movie_title']].to_dict(orient='records')
        return movies_list

