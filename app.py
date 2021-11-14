from datetime import datetime
import os

import docx2txt
import pyttsx3
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

engine = pyttsx3.init()
rate = engine.getProperty('rate')   
engine.setProperty('rate', 190) 
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id) 

UPLOAD_FOLDER = "static/"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///story.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config["MAX_CONTENT_PATH"] = 16 * 1024 * 1024

db = SQLAlchemy(app)

class Stories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(255), nullable = False)
    email = db.Column(db.String(255), nullable = False)
    title = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String(255), nullable = False)
    audio = db.Column(db.String(255), nullable=False)
    word = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, title, description, audio, word):
        self.title = title
        self.description = description
        self.author = name
        self.email = email
        self.audio = audio
        self.word = word

    def __repr__(self):
        return f"Story id. {self.id}"


@app.route("/")
@app.route("/home")
def hello_world():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/story")
def story():
    return render_template("story.html", stories=Stories.query.all())

@app.route("/add", methods = ['POST', 'GET'])
def add():
    if request.method == "POST":
        name = request.form["title"]
        email = request.form["email"]
        title = request.form["story"]
        desc = request.form["desc"]
        word = request.files['file']
        word.save(os.path.join(app.config["UPLOAD_FOLDER"], word.filename))
        audio_file = docx2txt.process(f'static/uploads/{word.filename}')
        engine.save_to_file(audio_file, f"static/{word.filename}.mp3")
        audio = f"{word.filename}.mp3"
        engine.runAndWait()
        story_to_add = Stories(name, email, title, desc, audio, word.filename)
        db.session.add(story_to_add)
        db.session.commit()
        return redirect("/story")
    else:
        return render_template("add.html")

app.run(debug=True)
