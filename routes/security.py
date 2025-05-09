from flask import render_template, request, send_file, session
from werkzeug.utils import secure_filename
import os
import fitz
import difflib

@app.route('/compare', methods=['GET', 'POST'])
def compare_pdfs():
    if request.method == 'POST':
        if 'pdf1' not in request.files or 'pdf2' not in request.files:
            return render_template('pages/security/compare.html', 
                                 error="Please upload both PDF files")

        pdf1 = request.files['pdf1']
        pdf2 = request.files['pdf2']
        
        if pdf1.filename == '' or pdf2.filename == '':
            return render_template('pages/security/compare.html',
                                 error="No files selected")
        
        # Save files temporarily
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        pdf1_path = os.path.join(temp_dir, secure_filename(pdf1.filename))
        pdf2_path = os.path.join(temp_dir, secure_filename(pdf2.filename))
        
        pdf1.save(pdf1_path)
        pdf2.save(pdf2_path)
        
        # Store paths in session for later retrieval
        session['pdf1_path'] = pdf1_path
        session['pdf2_path'] = pdf2_path
        
        # Compare PDFs
        comparison_result = compare_pdf_files(pdf1_path, pdf2_path)
        
        return render_template('pages/security/compare.html',
                             comparison_result=comparison_result)
    
    return render_template('pages/security/compare.html')

def compare_pdf_files(pdf1_path, pdf2_path):
    """Compare two PDF files and return differences"""
    doc1 = fitz.open(pdf1_path)
    doc2 = fitz.open(pdf2_path)
    
    differences = []
    matching_pages = 0
    different_pages = 0
    
    max_pages = min(doc1.page_count, doc2.page_count)
    
    for page_num in range(max_pages):
        # Extract text from both pages
        text1 = doc1[page_num].get_text()
        text2 = doc2[page_num].get_text()
        
        # Compare texts
        if text1 != text2:
            different_pages += 1
            # Get detailed differences using difflib
            diff = difflib.unified_diff(
                text1.splitlines(keepends=True),
                text2.splitlines(keepends=True)
            )
            
            # Store difference information
            differences.append({
                'page': page_num + 1,
                'description': f"Text content differs",
                'diff': list(diff)
            })
        else:
            matching_pages += 1
    
    # Check if documents have different number of pages
    if doc1.page_count != doc2.page_count:
        differences.append({
            'page': min(doc1.page_count, doc2.page_count) + 1,
            'description': f"Document length differs: PDF1 has {doc1.page_count} pages, PDF2 has {doc2.page_count} pages"
        })
    
    doc1.close()
    doc2.close()
    
    return {
        'matching_pages': matching_pages,
        'different_pages': different_pages,
        'differences': differences
    }

@app.route('/get_pdf1')
def get_pdf1():
    if 'pdf1_path' in session:
        return send_file(session['pdf1_path'])
    return '', 404

@app.route('/get_pdf2')
def get_pdf2():
    if 'pdf2_path' in session:
        return send_file(session['pdf2_path'])
    return '', 404