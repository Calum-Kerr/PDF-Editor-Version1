from flask import render_template, request, redirect, send_file, send_from_directory
from werkzeug.utils import secure_filename
from app import app
from io import BytesIO
import os
import logging
import fitz

UPLOAD_FOLDER = 'app/static/uploads'

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
        if file.filename == '': 
            return redirect('/upload')
        if file and file.filename.endswith('.pdf'):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect('/edit/' + filename)
    return redirect('/upload')

@app.route('/edit/<filename>')
def edit_pdf(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        if not os.path.exists(file_path):
            return redirect('/upload')
            
        text_blocks = []
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text_blocks.append({
                                'page': page_num,
                                'bbox': span['bbox'],
                                'text': span['text'],
                                'font': span['font'],
                                'size': span['size']})
        doc.close()
        return render_template('edit.html', filename=filename, text_blocks=text_blocks)
    except Exception as e:
        print(f"Error in edit_pdf: {str(e)}")
        return redirect('/upload')

@app.route('/save_changes/<filename>', methods=['POST'])
def save_changes(filename):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
        changes = request.get_json()['changes']
        doc = fitz.open(file_path)
        for change in changes:
            page = doc[int(change['page'])]
            bbox = fitz.Rect(change['bbox'])
            page.add_redact_annot(bbox)
            page.insert_textbox(
                rect=bbox,
                buffer=change['text'],
                fontsize=change['size'],
                fontname=change['font'],
                color=(0, 0, 0))
        for page in doc:
            page.apply_redactions()
        modified_path = os.path.join(UPLOAD_FOLDER, f'modified_{filename}')
        doc.save(modified_path)
        doc.close()
        return send_file(
            modified_path,
            as_attachment=True,
            download_name=f'modified_{filename}',
            mimetype='application/pdf'
        )
    
    except Exception as e:
        print(f"Error saving PDF: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        logging.info(f"Attempting to download file: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Error downloading file: {str(e)}")
        return {'error': str(e)}, 500