import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import flask
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import flask_login
import datetime
load_dotenv()
# All of the return requires further information regarding front-end design, whether a new page is created for each button or not"
app = Flask(__name__)
#login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv("SECRET_KEY")
# connect to the database
cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")] 

# the following try/except block is a way to verify that the database connection is alive (or not)
#try:
   #cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
   #print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
#except Exception as e:
   #print(" * MongoDB connection error:", e)  
users = {'foo@bar.tld': {'password': 'secret'}} # mock data
class User(flask.login.UserMixin):
    def __init__(self, username):
        self.username = username
    def __str__(self):
        return self.username
@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user
@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email
    return user
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form["password"]
        #search in database using find_one()
        curr_user = db.user_collection.find({username: username})
        if  curr_user and password == curr_user[password]:
            user = User(username)
            flask_login.login_user(user)
            return render_template('index.html')
    return render_template('signin.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form["password"]
        password2 = request.form["password2"]
        if password != password2:
            error_message = "Passwords do not match."
            return render_template('signup.html', error_message=error_message)
        if db.user_collection.find_one({'username': username}):
            error_message = "Username is already taken."
            return render_template('signup.html', error_message=error_message)
        doc = {'username': username, 'password': password}
        db.user_collection.insert_one(doc)
        return render_template('signin.html')
    return render_template('signup.html')

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return render_template('signin.html')

@app.route("/")
def home():
    tasks = db.tasks.find().limit(10)
    docs = [task for task in tasks]
    return render_template("index.html", docs = docs)
@app.route("/edit/<post_id>")
def edit(task_id):
     doc = db.tasks.find_one({"_id": ObjectId(task_id)})
     return render_template("edit.html", doc=doc) 
    # return redirect(
    #     url_for("home")
    # ) 
    #  change to the whateber html page for editing if not home. If home, don't mind the return redirect code
@app.route("/search")
def search():
     query = request.form.get('query')
     results = {}
     if query:
         results = db.tasks.find({"task": {"search": query}}, {"date": {"$search": query}})
     return render_template("search.html", results=results) 
@app.route("/edit/<post_id>", methods=["POST"])
def edit_task(task_id):
    task = request.form["task"]
    date = request.form["date"]
    doc = {
        "_id": ObjectId(task_id),
        "task": task,
        "date": date,
    }
    doc = db.tasks.update_one({"_id": ObjectId(task_id)},{"$set": doc})
    # return redirect(
    #     url_for("home")
    # )  
    # change to the whateber html page for editing if not home. If home, don't mind the return redirect code
    return render_template("edit.html", doc=doc)
@app.route("/delete/<post_id>")
def delete(task_id):
    db.messages.delete_one({"_id": ObjectId(task_id)})
    return render_template("delete.html")
    # or
    # return redirect(
    #     url_for("home")
    # ) 
@app.route("/add_task", methods=["POST"])
def add_task():
    task = request.form["task"]
    date = request.form["date"]
    doc = {"task":task, "date": date}
    if task and date:
        db.tasks.insert_one(doc)
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "error": "Task not provided"}), 400
if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app.run(port=FLASK_PORT)
