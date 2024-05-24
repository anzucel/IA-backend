import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from naiveBayes import NaiveBayes

reviewDSPath = "Files/rotten_tomatoes_critic_reviews.csv"
moviesDSPath = "Files/rotten_tomatoes_movies.csv"


class Model:
    def __init__(self):
        # Convertir las reviews en una representación numérica, eliminacion de palabras comunes
        self.vectorizer = TfidfVectorizer(stop_words='english')

        # Entrenar el modelo
        self.model = NaiveBayes()

        # leyendo data
        self.data = pd.read_csv(reviewDSPath)

        print("Datos cargados correctamente")

        # Eliminar columnas irrelevantes
        self.data = self.data.drop(columns=['top_critic', 'review_score', 'review_date'])
        # Normalizar los datos
        self.data['review_type'] = self.data['review_type'].apply(lambda x: 1 if x == 'Fresh' else 0)
        self.data = self.data.dropna(subset=['review_content'])

        self.trainModel()

    def trainModel(self):
        # Preparación de datos
        X = self.data['review_content']
        y = self.data['review_type']

        X = self.vectorizer.fit_transform(X)

        # Dividir el dataset en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.model.fit(X_train, y_train)

    def predict(self, rotten_link, publisher, review, user):
        review_type = ""
        # clasificacion
        review_transformed = self.vectorizer.transform([review])
        prediction = self.model.predict(review_transformed)
        review_type = "Fresh" if prediction[0] == 1 else "Rotten"
        # agregar nueva película al dataset
        new_review = pd.DataFrame([[rotten_link, user, publisher, review_type, review]], columns=['rotten_tomatoes_link', 'critic_name', 'publisher_name', 'review_type', 'review_content'])

        # normalizar
        new_review['review_type'] = self.data['review_type'].apply(lambda x: 1 if x == 'Fresh' else 0)

        self.data = pd.concat([self.data, new_review], ignore_index=True) # se agrega al final
        # entrenar nuevamente
        self.retrainModel()
       # retornar respuesta
        return review_type

    def retrainModel(self):
        X = self.data['review_content']
        y = self.data['review_type']

        # Vectorizar las reseñas
        X = self.vectorizer.fit_transform(X)

        # entrenar modelo con nuevos datos
        X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)

    def runExamples(self, rotten_link, publisher, review, user):
        #    "The movie was absolutely fantastic, I loved every moment of it!",
        #    "The movie was terrible, I hated it and it was a waste of time.",
        #    "Too many long, very pauses. The Story was slow. Very dissapointed"
        classification = self.predict(rotten_link, publisher, review, user)
        return classification
