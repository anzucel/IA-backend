import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report

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
        self.class_log_prior = np.log(self.class_counts) - np.log(n_docs)
        self.feature_log_prob = np.log(self.feature_counts + 1) - np.log(
            self.feature_counts.sum(axis=1)[:, np.newaxis] + n_features)

    def predict(self, X):
        return np.argmax(self.predict_log(X), axis=1)

    def predict_log(self, X):
        return X @ self.feature_log_prob.T + self.class_log_prior

# clasificacion
def classify_review(review):
    review_transformed = vectorizer.transform([review])
    prediction = model.predict(review_transformed)
    return "Fresh" if prediction[0] == 1 else "Rotten"

def classify():
    #leyendo data
    data = pd.read_csv(r'C:\Users\andre\OneDrive - Universidad Rafael Landivar\PRIMER CICLO 2024\IA\PROYECTO\archive\rotten_tomatoes_critic_reviews.csv')
    print("Datos cargados correctamente")

    # Normalizar los datos
    data['review_type'] = data['review_type'].apply(lambda x: 1 if x == 'Fresh' else 0)
    data = data.dropna(subset=['review_content'])

    # Preparación de datos
    X = data['review_content']
    y = data['review_type']

    # Convertir las reviews en una representación numérica
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(X)

    # Dividir el dataset en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo
    model = NaiveBayes()
    model.fit(X_train, y_train)

# Ejemplo de uso
def runEjemplos():
    new_review = "The movie was absolutely fantastic, I loved every moment of it!"
    print("Review:", new_review)
    print("Classification:", classify_review(new_review))

    new_review = "The movie was terrible, I hated it and it was a waste of time."
    print("Review:", new_review)
    print("Classification:", classify_review(new_review))

    new_review = "Too many long, very pauses. The Story was slow. Very dissapointed"
    print("Review:", new_review)
    print("Classification:", classify_review(new_review))

def getPublishers():
    data = pd.read_csv(r'C:\Users\andre\OneDrive - Universidad Rafael Landivar\PRIMER CICLO 2024\IA\PROYECTO\archive\rotten_tomatoes_critic_reviews.csv')
    data = data.dropna(subset=['publisher_name'])
    publisher_list = data['publisher_name'].astype(str).tolist()
    print(publisher_list)
    return publisher_list


