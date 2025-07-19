from flask import Flask, render_template, request, redirect, url_for, jsonify
import cv2
import os
from AnalyzerClass import ExerciseAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = r'C:\Users\Andrei\OneDrive - Colegiul Național de Informatică Piatra-Neamț\Desktop\Exercise Project'

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
        return jsonify(success=False, message="No video file provided"), 400
    
    video = request.files['video']
    
    if video.filename == '':
        return jsonify(success=False, message="Empty file name"), 400
    
    if video:

        path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(path)
        
        try:
            mark, message = analyzer.analyzeVideo(path)
            return jsonify(success = True, mark=mark, message=message)
            
        except Exception as e:
            return jsonify(success=False, error=f"Error analyzing video: {str(e)}")
    
    return jsonify(success=False, error="Unknown error")

@app.route("/results")
def results():
    return render_template("results.html")

if __name__ == "__main__":
    app.run(debug=True)