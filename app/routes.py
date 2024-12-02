from flask import render_template, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from app import app
from io import BytesIO
import os
import fitz

UPLOAD_FOLDER = 'app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():return render_template('index.html')

@app.route('/about')
def about():return render_template('about.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'pdf' not in request.files: return redirect(url_for('upload'))
        file = request.files['pdf']
        if file.filename == '': return redirect(url_for('upload'))
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return redirect(url_for('edit_pdf', filename=filename))
    return render_template('upload.html')

@app.route('/edit/<filename>')
def edit_pdf(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path): return redirect(url_for('upload'))
        text_blocks = []
        doc = fitz.open(file_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]

            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:text_blocks.append({'page': page_num,'bbox': span['bbox'],'text': span['text'],'font': span['font'],'size': span['size']})
        doc.close()
        return render_template('edit.html', filename=filename, text_blocks=text_blocks)
    except Exception as e:
        print(f"Error in edit_pdf: {str(e)}")
        return redirect(url_for('upload'))