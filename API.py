from flask import Flask
#from flask_pymongo import pymongo
#from pymongo import MongoClient
from flask import Flask, Response
import requests
from flask import request
from flask import jsonify
import naiveBayes
import User
#from bson.json_util import dumps
import json

app = Flask(__name__)

# Crear usuario
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or not 'username' in data or not 'password' in data:
        return jsonify({'message': 'Username and password required!'}), 400

    new_user = User.user(data['username'], request.json['password'])
    #collection_user.insert_one(new_user.toDict())
    return jsonify({'status': 'success'}), 200

# Obtener publisher
@app.route('/publishers', methods=['GET'])
def getPublisher():
    publishers = naiveBayes.getPublishers()

    if publishers:
        return jsonify({'publishers': publishers})
    else :
        return jsonify({'message': 'Publishers not found'}), 400


if __name__ == '__main__':
    app.run(debug=True)
