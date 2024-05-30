from flask import Flask
# from flask_pymongo import pymongo
# from pymongo import MongoClient
from flask import Flask, Response
import requests
from flask import request
from flask import jsonify
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps

import User
# from bson.json_util import dumps
import json

from pymongo import MongoClient
from flask_pymongo import PyMongo
from model import Model
from naiveBayes import NaiveBayes

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://admin:12345@cluster0.prvnm39.mongodb.net/dbexample?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

model = Model()

@app.route('/check_mongo')
def check_mongo():
    try:
        # Intentar obtener información sobre la base de datos para verificar la conexión
        mongo.cx.server_info()
        return jsonify({"message": "MongoDB connection successful"}), 200
    except ConnectionFailure:
        return jsonify({"message": "MongoDB connection failed"}), 500

# Crear usuario
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({'message': 'Username and password required!'}), 400

    existing_user = mongo.db.user.find_one({"username": data['username']})

    if existing_user:
        return jsonify({"error": "username already exist"}), 400

    mongo.db.user.insert_one(data)
    return jsonify({'status': 'success'}), 200

#iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    existing_user = mongo.db.user.find_one({"username": data['username']})

    if not data:
        return jsonify({'message': 'Bad Request'}), 500
    else:
        if existing_user:
            # valida contraseña
            if data['password'] == existing_user['password']:
                return jsonify({"status": "success"}), 200
            else:
                return jsonify({"message": "incorrect password"}), 401
        else:
            return jsonify({"error": "User not found, try again!"}), 404


# Obtener publisher
@app.route('/publishers', methods=['GET'])
def getPublisher():
    publishers = NaiveBayes.getPublishers()

    if publishers:
        return jsonify({'publishers': publishers})
    else:
        return jsonify({'message': 'Publishers not found'}), 400


# Obtener peliculas
@app.route('/movies', methods=['GET'])
def getMovies():
    movies_collection = mongo.db.movie.find({}, {"_id": 0})
    movies = list(movies_collection)

    if movies:
        return app.response_class(dumps({'movies': movies}), mimetype='application/json'), 200
    else:
        return jsonify({'message': 'Publishers not found'}), 400

@app.route('/users', methods=['GET'])
def getUsers():
    users_collection = mongo.db.user.find({}, {"_id": 0})
    users = list(users_collection)
    if users:
        return app.response_class(dumps({'users': users}), mimetype='application/json'), 200
    else:
        return jsonify({'message': 'Publishers not found'}), 400

# realiza la clasificacion segun la review
@app.route('/predict', methods=['POST'])
def predict():
    res = model.runExamples(request.json['rotten_link'], request.json['publisher'], request.json['review'],
                                 request.json['user'])
    if res:
        data = {}
        data['movie_title'] = request.json['movie_title']
        data['publisher'] = request.json['publisher']
        data['review'] = request.json['review']
        data['review_type'] = res

        # Guardar datos review
        mongo.db.review.insert_one(data)

        return jsonify({'classification': res}), 200
    else:
        return jsonify({'message': 'Publishers not found'}), 400

# consultar reviews por pelicula
@app.route('/get-reviews', methods=['POST'])
def getReviews():
    data = request.get_json()
    reviews_collection = mongo.db.review.find({"movie_title": data['movie_title']}, {"_id": 0})
    reviews = list(reviews_collection)

    if reviews_collection:
        return jsonify({'reviews': reviews}), 200
    else:
        return jsonify({'message': 'Publishers not found'}), 400

@app.route('/movies-detail', methods=['GET'])
def getMoviesDetail():
    movies_collection = mongo.db.movie.find({}, {"_id": 0})

    if movies_collection:
        for movie in movies_collection:
            url = f'http://www.omdbapi.com/?apikey=ccbef632&t={movie["movie_title"]}'
            response = requests.get(url)
            data = response.json()
            movie["year"] = data.get("Year")
            movie["plot"] = data.get("Plot")
            movie["actors"] = data.get("Actors")
            movie["poster"] = data.get("Poster")

            mongo.db.movie.update_one({"movie_title": movie["movie_title"]},
                                      {"$set": movie}, upsert=True)
        return jsonify({'classification': "success"}), 200
    else:
        return jsonify({'message': 'Publishers not found'}), 400

if __name__ == '__main__':
    app.run(debug=True)
