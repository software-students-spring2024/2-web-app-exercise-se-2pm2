from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
app = Flask(__name__)
client = MongoClient("mongodb+srv://yl7408:tR%@Vw$5#Y6@r$c@se-2pm2.xbstfiu.mongodb.net/?retryWrites=true&w=majority")
db = client["todolist"]
task_collection = db["tasks"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_tasks", method = ["GET"])
def get_tasks():
    ten_tasks = task_collection.find().limit(10)
    task_list = [task for task in ten_tasks]
    return jsonify(task_list)

@app.route("/add_tasks", method =["POST"])
def add_task():
    task_data = request.json
    task = task_data.get("task")

    if task:
       task_collection.insert_one({"task": task})
       return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 400

if __name__ == "__main__":
    app.run(debug=True)
