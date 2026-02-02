from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson import ObjectId

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": "*"}})


try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print("✅ Succès : Connecté à MongoDB Compass !")
except ConnectionFailure:
    print("❌ Erreur : Impossible de se connecter à MongoDB. Est-il lancé ?")

db = client.todo_db
tasks_collection = db.tasks


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response



@app.route('/tasks', methods=['GET', 'POST'])
def manage_tasks():
    if request.method == 'GET':
        tasks = []
        for doc in tasks_collection.find():
            tasks.append({
                "id": str(doc["_id"]),
                "title": doc["title"],
                "completed": doc.get("completed", False)
            })
        return jsonify(tasks)

    if request.method == 'POST':
        data = request.json
        if not data or 'title' not in data:
            return jsonify({"error": "Données invalides"}), 400
            
        new_task = {
            "title": data['title'],
            "completed": False
        }
        tasks_collection.insert_one(new_task)
        return jsonify({"message": "Tâche ajoutée avec succès !"}), 201

@app.route('/tasks/<id>', methods=['PUT', 'DELETE'])
def handle_task(id):
    
    if request.method == 'DELETE':
        tasks_collection.delete_one({'_id': ObjectId(id)})
        return jsonify({"status": "deleted"}), 200
        
    
    if request.method == 'PUT':
        data = request.json
        tasks_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {'completed': data.get('completed')}}
        )
        return jsonify({"status": "updated"}), 200

@app.route('/test-db')
def test_db():
    try:
        client.admin.command('ping')
        return jsonify({"status": "OK", "message": "Connexion MongoDB active"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)