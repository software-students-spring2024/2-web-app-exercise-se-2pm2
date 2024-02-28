import os
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# connect to the database
cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")] 

# the following try/except block is a way to verify that the database connection is alive (or not)
try:
    cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    print(" * MongoDB connection error:", e)  

@app.route('/signin')
def signin():
    return render_template('signin.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route("/")
def home():
    return render_template("index.html")
@app.route("/get_tasks", methods=["GET"])
def get_tasks():
    ten_tasks = task_collection.find().limit(10)
    task_list = [task for task in ten_tasks]
    return jsonify(task_list)

@app.route("/add_task", methods=["POST"])
def add_task():
    task_data = request.json
    task = task_data.get("task")

    if task:
        task_collection.insert_one({"task": task})
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "error": "Task not provided"}), 400
if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app.run(port=FLASK_PORT)
