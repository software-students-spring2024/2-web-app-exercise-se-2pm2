import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import flask
import pymongo
import certifi
from bson.objectid import ObjectId
from dotenv import load_dotenv
import calendar
from datetime import datetime, timedelta
import certifi
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash
load_dotenv()
# All of the return requires further information regarding front-end design, whether a new page is created for each button or not"
app = Flask(__name__)

#login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
app.secret_key = os.getenv("SECRET_KEY")
# connect to the database

cxn = pymongo.MongoClient(os.getenv("MONGO_URI"), tlsCAFile=certifi.where())
db = cxn[str(os.getenv("MONGO_DBNAME"))]  

try:
    cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
except Exception as e:
    print(" * MongoDB connection error:", e)

# persistent counter for taskId generation (taskId can overlap values if counter is not saved)
def readCounter():
    counterSetting = db['settings'].find_one({'setting': 'counter'})
    if counterSetting:
        return int(counterSetting['value'])
    return 0

def writeCounter(counter):
    db['settings'].update_one({'setting': 'counter'}, {'$set': {'value': counter}}) 

def getCalendarDates(date):
    first = date.replace(day=1)
    prev_month = first - timedelta(days=1)

    # Extract the year and month from today's date
    year = date.year
    month = date.month

    last_year = prev_month.year
    last_month = prev_month.month

    tasks = db.tasks.find()
    event_dates = [task['date'] for task in tasks]
    
    # Get the number of days in the current month
    day_of_week, month_len = calendar.monthrange(year, month)
    _, prev_month_len = calendar.monthrange(last_year, last_month)
    prev_month_days = {}
    if day_of_week != 6:
        for day in range(prev_month_len - day_of_week, prev_month_len + 1):
            prev_month_days[datetime(last_year, last_month, day)] = "inactive"
    
    month_days = {datetime(year, month, day): "" for day in range(1, month_len + 1)}

    next_month = date.replace(month=date.month % 12 + 1, year=date.year + (1 if date.month == 12 else 0))
    next_month_days = {datetime(next_month.year, next_month.month, day): "inactive" for day in range(1, 8 - ((len(prev_month_days) + len(month_days)) % 7))}
    
    for event_date in event_dates:
        my_datetime = datetime.strptime(event_date, '%Y-%m-%d')
        if my_datetime in prev_month_days.keys():
            prev_month_days[my_datetime] += ' event'
        elif my_datetime in month_days.keys():
            month_days[my_datetime] += ' event'
        elif my_datetime in next_month_days.keys():
            next_month_days[my_datetime] += ' event'
    
    print(next_month_days)

    return prev_month_days, month_days, next_month_days

class User(flask_login.UserMixin):
   def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def user_loader(username):
    user_data = db.user_collection.find_one({"username": username})
    if not user_data: 
        return None
    if user_data['username'] != username:
        return
    user = User(username)
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if not username:
        return None
    user_data = db.user_collection.find_one({"username": username})
    if not user_data:
        return None
    if user_data['username'] != username:
        return
    user = User(username)
    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect('signin')

@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form['username']
        password = request.form["password"]
        #search in database using find_one()
        #curr_user = db.user_collection.find({username: username})
        curr_user = db.user_collection.find_one({"username": username})
        if not curr_user or not check_password_hash(curr_user['password'], password):
            error_message = "Username or password is incorrect."
            return render_template('signin.html', error_message=error_message)
        if  curr_user and check_password_hash(curr_user['password'], password):
            user = User(username)
            flask_login.login_user(user)
            return redirect(flask.url_for('home'))
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
        doc = {'username': username, 'password': generate_password_hash(password)}
        db.user_collection.insert_one(doc)
        return redirect('signin')
    return render_template('signup.html')

@app.route('/logout', methods=["GET"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('signin')

@app.route('/back', methods=["GET"])
def back():
    return redirect(flask.url_for('home'))
@app.route("/")
@flask_login.login_required
def home():
    tasks = db.tasks.find().limit(10)
    see_tasks = db.tasks.find()
    see_docs = [task['date'] for task in see_tasks]
    
    docs = [task for task in tasks]
    today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    month_year = today.strftime("%B %Y")
    year = today.year
    month = today.month
    print(see_docs)
    prevMonthDays, monthDays, nextMonthDays = getCalendarDates(today)
    monthDays[today] += ' active'

    return render_template("index.html", docs = docs, month_year = month_year, prevDays = prevMonthDays.items(), monthDays = monthDays.items(), nextDays = nextMonthDays.items())

@app.route("/date/<date>")
@flask_login.login_required
def date_events(date):
    
    my_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
    data_date = str(my_datetime)
    data_date = data_date[:10]
    docs = db['tasks'].find({"date": data_date})
    formated_date = my_datetime.strftime("%B %d %Y")
    return render_template("events.html", date=formated_date, docs=docs, operation_date=data_date)


# editing route handler

@app.route("/edit/<date>", methods=['GET', 'POST'])
@flask_login.login_required
def edit_for_specific_date(date):

    # POST handler
    if request.method == 'POST':

        # get form data
        taskId = int(request.form['taskId'])
        task = request.form['task']
        date = request.form['date']

        # update collection
        db['tasks'].update_one({'taskId': taskId}, {'$set': {'task': task, 'date': date}})

        # refresh page
        return redirect(url_for('edit_for_specific_date', date=date))

    # load the edit template
    documents = list(db['tasks'].find({'date': date}, {'_id': 0}))
    return render_template('edit.html', documents = documents, date=date) 

@app.route("/edit", methods=['GET', 'POST'])
@flask_login.login_required
def edit():

    # POST handler
    if request.method == 'POST':

        # get form data
        taskId = int(request.form['taskId'])
        task = request.form['task']
        date = request.form['date']

        # update collection
        db['tasks'].update_one({'taskId': taskId}, {'$set': {'task': task, 'date': date}})

        # refresh page
        return redirect(url_for('edit'))

    # load the edit template
    documents = list(db['tasks'].find({}, {'_id': 0}))
    return render_template('edit.html', documents = documents) 

@app.route("/search",  methods = ['GET','POST'])
@flask_login.login_required
def search():
     query = request.form.get('query')
     results = []
     if query:
        task_results = list(db.tasks.find({"task": {"$regex": query, "$options": "i"}} ))
        data_results = list(db.tasks.find({"date":{"$regex": query, "$options": "i"}}))
        results = task_results+data_results
     return render_template("search.html", results=results)

# adding route handler
@app.route("/add/<date>", methods = ['GET', 'POST'])
@flask_login.login_required
def add_for_specific_date(date):

    # POST handler
    if request.method == 'POST':

        #set taskId and increment the counter
        taskId = readCounter()
        taskId += 1
        writeCounter(taskId)

        # get form data
        task = request.form['task']
        date = request.form['date']

        # update collection
        db['tasks'].insert_one({'taskId': taskId, 'task': task, 'date': date})

        # refresh page
        return redirect(url_for('add_for_specific_date', date=date))
    documents = list(db['tasks'].find({'date': date}, {'_id': 0}))
    # display add template
    return render_template('add.html', documents = documents, date=date)

@app.route("/add", methods = ['GET', 'POST'])
@flask_login.login_required
def add():

    # POST handler
    if request.method == 'POST':

        #set taskId and increment the counter
        taskId = readCounter()
        taskId += 1
        writeCounter(taskId)

        # get form data
        task = request.form['task']
        date = request.form['date']

        # update collection
        db['tasks'].insert_one({'taskId': taskId, 'task': task, 'date': date})

        # refresh page
        return redirect(url_for('add'))
    # display add template
    documents = list(db['tasks'].find({}, {'_id': 0}))
    return render_template('add.html', documents = documents)

# delete_handler for specific dates

@app.route("/delete/<date>", methods = ['GET', 'POST'])
@flask_login.login_required
def delete_for_specific_date(date):

    # POST handler
    if request.method == 'POST':

        # get taskId
        taskId = int(request.form['taskId'])

        # delete
        if taskId is not None:
            db['tasks'].delete_one({'taskId': taskId})

        # refresh
        return redirect(url_for('delete_for_specific_date', date=date))

    # display delete template
    documents = list(db['tasks'].find({'date': date}, {'_id': 0}))
    return render_template('delete.html', documents = documents, date=date) 

# delete handler
@app.route("/delete", methods = ['GET', 'POST'])
@flask_login.login_required
def delete():

    # POST handler
    if request.method == 'POST':

        # get taskId
        taskId = int(request.form['taskId'])

        # delete
        if taskId is not None:
            db['tasks'].delete_one({'taskId': taskId})

        # refresh
        return redirect(url_for('delete'))

    # display delete template
    documents = list(db['tasks'].find({}, {'_id': 0}))
    return render_template('delete.html', documents = documents) 


if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "3000")
    app.run(debug=True, port=FLASK_PORT)
