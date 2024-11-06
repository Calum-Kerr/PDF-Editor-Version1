from flask import render_template, request
from app import app
@app.route('/')
def index():return render_template('index.html')

@app.route('/about')
def about():return render_template('about.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        pdf = request.files['pdf']
        return f"Uploaded file: {pdf.filename}"
    return render_template('upload.html')