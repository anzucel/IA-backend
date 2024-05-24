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

app.config["MONGO_URI"] = "mongodb+srv://admin:12345@atlascluster.rwws8fw.mongodb.net/db?retryWrites=true&w=majority&appName=AtlasCluster"
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
        return jsonify(), 200


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
    movies = NaiveBayes.getMovies()

    if movies:
        return jsonify({'movies': movies})
    else:
        return jsonify({'message': 'Publishers not found'}), 400

@app.route('/users', methods=['GET'])
def getUsers():
    users_collection = mongo.db.user.find({})
    users = list(users_collection)
    if users:
        return app.response_class(dumps({'users': users}), mimetype='application/json')
    else:
        return jsonify({'message': 'Publishers not found'}), 400

@app.route('/predict', methods=['POST'])
def predict():
    review = request.json['review']
    prediction = model.predict(request.json['rotten_link'], request.json['publisher'], request.json['review'], request.json['user'])
    return jsonify({"prediction": prediction})


@app.route('/run-examples', methods=['POST'])
def getExample():
    examples = model.runExamples(request.json['rotten_link'], request.json['publisher'], request.json['review'],
                                 request.json['user'])
    if examples:
        return jsonify({'classification': examples})
    else:
        return jsonify({'message': 'Publishers not found'}), 400



if __name__ == '__main__':
    app.run(debug=True)
