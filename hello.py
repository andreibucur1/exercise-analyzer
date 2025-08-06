from flask import Flask, render_template, request, redirect, url_for, jsonify
import cv2
import os
from AnalyzerClass import ExerciseAnalyzer
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float
from werkzeug.security import generate_password_hash, check_password_hash
import random
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users111.db"
app.secret_key = 'secret'



login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

analyzer = ExerciseAnalyzer()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)






class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    password: Mapped[str]
    data = relationship('ExerciseData', back_populates='user', lazy=True)

class ExerciseData(db.Model):
    __tablename__ = 'exercise_data'
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey('users.id'))
    exercise: Mapped[str]
    mark: Mapped[float]
    timestamp: Mapped[str] = mapped_column(String(50))
    user = relationship('User', back_populates='data')


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

        if not check_password_hash(existing_user.password, password):
            return jsonify(success=False, error="Incorrect password")
        
        print("^^^^^^^^^^^^^^^lala")
        login_user(existing_user)
        return jsonify(success=True, message="Login successful", name = username)
        
        
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        print(f"Debug - Received data: username={username}, email={email}")  # pentru debug

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


            user = User(id=user_id, username=username, email=email, password=generate_password_hash(password,method='pbkdf2:sha256',salt_length=8))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return jsonify(success=True, message="User registered successfully", name=username)
        except Exception as e:
            db.session.rollback()
            return jsonify(success=False, error=f"Error registering user: {str(e)}")


    return render_template("register.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/change-username", methods=["GET", "POST"])
@login_required
def change_username():
    if request.method == "POST":
        old_username = request.form.get("oldusername")
        new_username = request.form.get("newusername")
        password = request.form.get("password")
        
        username_taken = db.session.execute(db.select(User).where(User.username == new_username)).scalar()
        existing_user = db.session.execute(db.select(User).where(User.username == old_username)).scalar()


        if username_taken:
            return jsonify(success=False, error="Username already exists")
        
        

        if not check_password_hash(existing_user.password, password):
            return jsonify(success=False, error="Incorrect password")


        existing_user.username = new_username
        db.session.commit()
        return jsonify(success=True, message="Login successful", name = new_username)
        
    return render_template("change-username.html")


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    return render_template("change-password.html")

@app.route("/upload")
@login_required
def upload():
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
@login_required
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
            if current_user.is_authenticated:
                exercise_data = ExerciseData(user_id=current_user.id, exercise=exercise, mark=mark, timestamp=str(datetime.datetime.now()))
                db.session.add(exercise_data)
                db.session.commit()
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
@login_required
def results():
    return render_template("results.html")


@app.route("/api/exercise-data", methods=["GET", "POST"])
@login_required
def get_results():
    user_data = db.session.execute(db.select(ExerciseData).where(ExerciseData.user_id == current_user.id)).scalars().all()
    results = []
    for data in user_data:
        results.append({
            'exercise': data.exercise,
            'mark': data.mark,
            'timestamp': data.timestamp
        })
    return jsonify(results=results)

@app.route("/chart", methods=["GET"])
@login_required
def chart():
    return render_template("chart.html")

if __name__ == "__main__":
    app.run(debug=True)