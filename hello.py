from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import cv2
import os
from AnalyzerClass import ExerciseAnalyzer
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from hashlib import sha256
import random

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users111.db"
app.secret_key = 'secret'

analyzer = ExerciseAnalyzer()

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password: Mapped[str]




with app.app_context():
    db.create_all()






@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        existing_user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if not existing_user:
            return jsonify(success=False, error="User not found")

        if existing_user.password != sha256(password.encode()).hexdigest():
            return jsonify(success=False, error="Incorrect password")
        
        print("^^^^^^^^^^^^^^^lala")
        session['user'] = existing_user.username
        return jsonify(success=True, message="Login successful")
        
        
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if not username or not email or not password or not confirm_password:
            return jsonify(success=False, error="All fields are required")


        if password != confirm_password:
            return jsonify(success=False, error="Passwords do not match")
        
        if len(password) < 6:
            return jsonify(success=False, error="Password must be at least 6 characters long")
        
        existing_user = db.session.execute(db.select(User).where(User.username == username)).scalar()

        if existing_user:
            return jsonify(success=False, error="Username already exists")
        
        try:
            user_id = random.randint(100000, 999999)
            while db.session.execute(db.select(User).where(User.id == user_id)).scalar():
                user_id = random.randint(100000, 999999)


            user = User(id=user_id, username=username, email=email, password=sha256(password.encode()).hexdigest())
            db.session.add(user)
            db.session.commit()
            return jsonify(success=True, message="User registered successfully")
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=f"Error registering user: {str(e)}")


    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

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
        cap = cv2.VideoCapture(path)
        try:
            mark, message = analyzer.analyzeVideo(path, exercise)
            return jsonify(success = True, mark=mark, message=message)
            
        except Exception as e:
            return jsonify(success=False, error=f"Error analyzing video: {str(e)}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            if os.path.exists(path):
                os.remove(path)
    
    return jsonify(success=False, error="Unknown error")

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)