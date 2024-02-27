import os
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# connect to the database
# cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
# db = cxn[os.getenv("MONGO_DBNAME")]  # store a reference to the database

# the following try/except block is a way to verify that the database connection is alive (or not)
# try:
    # cxn.admin.command("ping")  # The ping command is cheap and does not require auth.
    # print(" *", "Connected to MongoDB!")  # if we get here, the connection worked!
# except Exception as e:
    # print(" * MongoDB connection error:", e)  # debug

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app.run(port=FLASK_PORT)
