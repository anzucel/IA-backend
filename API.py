import asyncio
import aiohttp
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from pymongo.errors import ConnectionFailure

app = Flask(__name__)

CORS(app)
app.config["MONGO_URI"] = "mongodb+srv://admin:12345@cluster0.prvnm39.mongodb.net/dbexample?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

from model import Model
from naiveBayes import NaiveBayes

model = Model()


async def fetch_movie_details(session, movie_title):
    url = f'http://www.omdbapi.com/?apikey=ccbef632&t={movie_title}'
    async with session.get(url) as response:
        return await response.json()


async def fetch_all_movie_details(movie_titles):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_movie_details(session, title) for title in movie_titles]
        return await asyncio.gather(*tasks)


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


# Iniciar sesión
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    existing_user = mongo.db.user.find_one({"username": data['username']})

    if not data:
        return jsonify({'message': 'Bad Request'}), 500
    else:
        if existing_user:
            # Validar contraseña
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


# Obtener películas
@app.route('/movies', methods=['GET'])
def getMovies():
    movies_collection = mongo.db.movie.find({}, {"_id": 0})
    movies = list(movies_collection)

    if movies:
        return jsonify({'movies': movies}), 200
    else:
        return jsonify({'message': 'Movies not found'}), 400


@app.route('/users', methods=['GET'])
def getUsers():
    users_collection = mongo.db.user.find({}, {"_id": 0})
    users = list(users_collection)
    if users:
        return jsonify({'users': users}), 200
    else:
        return jsonify({'message': 'Users not found'}), 400


# Realizar la clasificación según la reseña
@app.route('/predict', methods=['POST'])
def predict():
    res = model.runExamples(request.json['rotten_link'], request.json['publisher'], request.json['review'],
                            request.json['user'])
    if res:
        data = {}
        data['movie_title'] = request.json['movie_title']
        data['publisher'] = request.json['publisher']
        data['review'] = request.json['review']
        data['user'] = request.json['user']
        data['review_type'] = res

        # Guardar datos de la reseña
        mongo.db.review.insert_one(data)

        return jsonify({'classification': res}), 200
    else:
        return jsonify({'message': 'Prediction failed'}), 400


# Consultar reseñas por película
@app.route('/get-reviews', methods=['POST'])
def getReviews():
    data = request.get_json()
    reviews_collection = mongo.db.review.find({"movie_title": data['movie_title']}, {"_id": 0})
    reviews = list(reviews_collection)

    if reviews_collection:
        return jsonify({'reviews': reviews}), 200
    else:
        return jsonify({'message': 'Reviews not found'}), 400


# Obtener clasificación película
@app.route('/movie-review', methods=['POST'])
def classifyMovie():
    data = request.get_json()

    if data:
        # buscar reviews por película
        reviews_collection = mongo.db.review.find({"movie_title": data['movie_title']}, {"_id": 0})
        reviews = list(reviews_collection)
        total_reviews = len(reviews)
        total_fresh = 0
        total_rotten = 0
        av_fresh = 0
        av_rotten = 0
        if total_reviews > 0:
            for review in reviews:
                if review['review_type'] == 'Fresh':
                    total_fresh += 1
                else:
                    total_rotten += 1

            av_fresh = total_fresh / total_reviews
            av_rotten = total_rotten / total_reviews

        res = {"fresh": av_fresh, "rotten": av_rotten}

        return jsonify({'result': res}), 200
    else:
        return jsonify({'message': 'Movie review failed, try again'}), 400

@app.route('/user-reviews', methods=['POST'])
def getUserReviews():
    data = request.get_json()

    if data:
        reviews_collection = mongo.db.review.find({"user": data['user']}, {"_id": 0})
        reviews = list(reviews_collection)
        return jsonify({'reviews': reviews}), 200
    else:
        return jsonify({'message': 'Movie reviews not found'}), 400

@app.route('/movies-detail', methods=['GET'])
def getMoviesDetail():
    movies_collection = mongo.db.movie.find({}, {"_id": 0})

    if movies_collection:
        movie_titles = [movie["movie_title"] for movie in movies_collection]
        movie_details = asyncio.run(fetch_all_movie_details(movie_titles))

        for movie, details in zip(movies_collection, movie_details):
            movie["year"] = details.get("Year")
            movie["plot"] = details.get("Plot")
            movie["actors"] = details.get("Actors")
            movie["poster"] = details.get("Poster")

            mongo.db.movie.update_one({"movie_title": movie["movie_title"]},
                                      {"$set": movie}, upsert=True)

        return jsonify({'classification': "success"}), 200
    else:
        return jsonify({'message': 'Movies not found'}), 400

if __name__ == '__main__':
    app.run(debug=True)
