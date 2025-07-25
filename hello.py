from flask import Flask, render_template, request, redirect, url_for, jsonify
import cv2
import os
from AnalyzerClass import ExerciseAnalyzer
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'C:\Users\Andrei\OneDrive - Colegiul Național de Informatică Piatra-Neamț\Desktop\Exercise Project'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///USERS.db"


analyzer = ExerciseAnalyzer()

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]




with app.app_context():
    db.create_all()




@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        
        if not username or not email:
            return render_template("login.html", error="Please fill in all fields.")
        
        user = User(username=username, email=email)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for("home"))
    
    return render_template("login.html")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'video' not in request.files:
        return jsonify(success=False, message="No video file provided"), 400
    
    video = request.files['video']
    # trebuie sa salvez video-ul in upload folder si dupa sa-l sterg

    


    if video.filename == '':
        return jsonify(success=False, message="Empty file name"), 400
    
    if video:

        path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(path)
        
        exercise = request.form.get('exercise')

        try:
            mark, message = analyzer.analyzeVideo(path, exercise)
            return jsonify(success = True, mark=mark, message=message)
            
        except Exception as e:
            return jsonify(success=False, error=f"Error analyzing video: {str(e)}")
    
    return jsonify(success=False, error="Unknown error")

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)