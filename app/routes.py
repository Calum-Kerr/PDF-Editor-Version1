from flask import render_template, request, redirect
from werkzeug.utils import secure_filename
from app import app
import os
 
UPLOAD_FOLDER = 'app/static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16mb limit and it works perfectly fine with a 15mb file!

def allowed_file(filename):return filename.lower().endswith('.pdf')

@app.route('/')
def index():return render_template('index.html')

@app.route('/about')
def about():return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    if request.method == 'POST':
        if 'pdf' not in request.files:
            return redirect('/upload')
        file = request.files['pdf']
        if file.filename == '' or not allowed_file(file.filename):
            return redirect('/upload')
        try:
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect('/edit/' + filename)
        except:return redirect('/upload')

@app.route('/edit/<filename>')
def edit_pdf(filename):
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    if not os.path.exists(file_path):
        return redirect('/upload')
    return render_template('edit.html', filename=filename)