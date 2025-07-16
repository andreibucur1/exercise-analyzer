from flask import Flask, render_template, request, redirect, url_for
import cv2
import os
from AnalyzerClass import ExerciseAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = ''

analyzer = ExerciseAnalyzer()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if 'video' not in request.files:
        return redirect(url_for('upload'))
    
    video = request.files['video']
    
    if video.filename == '':
        return redirect(url_for('upload'))
    
    if video:

        path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(path)
        
        try:
            mark, message = analyzer.analyzeVideo(path)
            return render_template("results.html", mark=mark, message=message)
            
        except Exception as e:
            return render_template("results.html", mark=0, message=f"Error analyzing video: {str(e)}")
    
    return redirect(url_for('upload'))

@app.route("/results")
def results():
    return render_template("results.html", mark=0, message="No analysis available")

if __name__ == "__main__":
    app.run(debug=True)