from flask import render_template, request, send_file, current_app, flash, redirect, url_for, jsonify
from forms.security import ProtectPDFForm
from tools.security.protect import protect_pdf
from werkzeug.utils import secure_filename
import os
import tempfile
from io import BytesIO
from tools.security.flatten import flatten_pdf
from app import app

from tools.convert.jpg_to_pdf import jpg_to_pdf_view
from tools.optimise.compress import compress_view
from tools.convert.pdf_to_panoramic import pdf_to_panoramic_view
from tools.organise.split import split_view
from tools.organise.merge import merge_view
from tools.organise.rotate import rotate_view
from tools.security.flatten import flatten_pdf


#------------------------- Main Pages -------------------------

@app.route('/')
def index():
    print("Rendering index.html")
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/optimise')
def optimise():
    return render_template('optimise.html')

@app.route('/convert')
def convert():
    return render_template('convert.html')

@app.route('/edit')
def edit():
    return render_template('edit.html')

@app.route('/organise')
def organise():
    return render_template('organise.html')

@app.route('/security')
def security():
    return render_template('security.html')

@app.route('/creative')
def creative():
    return render_template('creative.html')

@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

@app.route('/developer')
def developer():
    return render_template('developer.html')

@app.route('/analysis')
def analysis():
    return render_template('analysis.html')

#------------------------- Pages for each feature -------------------------

# Accessibility
@app.route('/pages/accessibility/accessibility_checker')
def accessibility_checker():
    return render_template('pages/accessibility/accessibility_checker.html')

@app.route('/pages/accessibility/add_tags')
def add_tags():
    return render_template('pages/accessibility/add_tags.html')

@app.route('/pages/accessibility/read_aloud')
def read_aloud():
    return render_template('pages/accessibility/read_aloud.html')

# Analysis
@app.route('/pages/analysis/citation_tool')
def citation_tool():
    return render_template('pages/analysis/citation_tool.html')

@app.route('/pages/analysis/snapshot_tool')
def snapshot_tool():
    return render_template('pages/analysis/snapshot_tool.html')

@app.route('/pages/analysis/size_optimizer')
def size_optimizer():
    return render_template('pages/analysis/size_optimizer.html')

@app.route('/pages/analysis/task_generator')
def task_generator():
    return render_template('pages/analysis/task_generator.html')

# Convert
@app.route('/pages/convert/jpg_to_pdf', methods=['GET', 'POST'])
def jpg_to_pdf():
    return jpg_to_pdf_view()

@app.route('/pages/convert/word_to_pdf')
def word_to_pdf():
    return render_template('pages/convert/word_to_pdf.html')

@app.route('/pages/convert/ppt_to_pdf')
def ppt_to_pdf():
    return render_template('pages/convert/ppt_to_pdf.html')

@app.route('/pages/convert/excel_to_pdf')
def excel_to_pdf():
    return render_template('pages/convert/excel_to_pdf.html')

@app.route('/pages/convert/html_to_pdf')
def html_to_pdf():
    return render_template('pages/convert/html_to_pdf.html')

@app.route('/pages/convert/zip_to_pdf')
def zip_to_pdf():
    return render_template('pages/convert/zip_to_pdf.html')

@app.route('/pages/convert/pdf_to_jpg')
def pdf_to_jpg():
    return render_template('pages/convert/pdf_to_jpg.html')

@app.route('/pages/convert/pdf_to_panoramic', methods=['GET', 'POST'])
def pdf_to_panoramic():
    return pdf_to_panoramic_view()

@app.route('/pages/convert/pdf_to_word')
def pdf_to_word():
    return render_template('pages/convert/pdf_to_word.html')

@app.route('/pages/convert/pdf_to_ppt')
def pdf_to_ppt():
    return render_template('pages/convert/pdf_to_ppt.html')

@app.route('/pages/convert/pdf_to_excel')
def pdf_to_excel():
    return render_template('pages/convert/pdf_to_excel.html')

@app.route('/pages/convert/pdf_to_pdfa')
def pdf_to_pdfa():
    return render_template('pages/convert/pdf_to_pdfa.html')

# Creative
@app.route('/pages/creative/cover_creator')
def cover_creator():
    return render_template('pages/creative/cover_creator.html')

@app.route('/pages/creative/page_designer')
def page_designer():
    return render_template('pages/creative/page_designer.html')

@app.route('/pages/creative/watermark_designer')
def watermark_designer():
    return render_template('pages/creative/watermark_designer.html')

# Developer
@app.route('/pages/developer/code_to_flowchart')
def code_to_flowchart():
    return render_template('pages/developer/code_to_flowchart.html')

@app.route('/pages/developer/layer_viewer')
def layer_viewer():
    return render_template('pages/developer/layer_viewer.html')

@app.route('/pages/developer/map_extractor')
def map_extractor():
    return render_template('pages/developer/map_extractor.html')

@app.route('/pages/developer/metadata_cleaner')
def metadata_cleaner():
    return render_template('pages/developer/metadata_cleaner.html')

# Edit
@app.route('/pages/edit/add_watermark')
def add_watermark():
    return render_template('pages/edit/add_watermark.html')

@app.route('/pages/edit/page_numbers')
def page_numbers():
    return render_template('pages/edit/page_numbers.html')

@app.route('/pages/edit/edit_content')
def edit_content():
    return render_template('pages/edit/edit_content.html')

# Optimise
@app.route('/pages/optimise/compress')
def compress():
    return render_template('pages/optimise/compress.html')

@app.route('/pages/optimise/ocr')
def ocr():
    return render_template('pages/optimise/ocr.html')

@app.route('/pages/optimise/repair')
def repair():
    return render_template('pages/optimise/repair.html')

# Organise
@app.route('/pages/organise/extract')
def extract():
    return render_template('pages/organise/extract.html')

@app.route('/pages/organise/merge', methods=['GET', 'POST'])
def merge():
    return merge_view()

@app.route('/pages/organise/remove')
def remove():
    return render_template('pages/organise/remove.html')

@app.route('/pages/organise/sort')
def sort():
    return render_template('pages/organise/sort.html')

@app.route('/pages/organise/rotate', methods=['GET', 'POST'])
def rotate():
    return rotate_view()

@app.route('/pages/organise/split', methods=['GET', 'POST'])
def split():
    return split_view()

# Security
@app.route('/pages/security/unlock')
def unlock():
    return render_template('pages/security/unlock.html')

@app.route('/pages/security/protect', methods=['GET', 'POST'])
def protect():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'})
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'})

        # Get form data
        user_password = request.form.get('user_password')
        owner_password = request.form.get('owner_password')
        
        if not all([user_password, owner_password]):
            return jsonify({'error': 'Passwords are required'})

        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Please upload a PDF file'})

        try:
            # Read the uploaded file into memory
            pdf_data = BytesIO(file.read())
            
            # Create a temporary file for the output
            output_pdf = BytesIO()
            
            # Protect the PDF
            protect_pdf(
                input_stream=pdf_data,
                output_stream=output_pdf,
                user_password=user_password,
                owner_password=owner_password
            )
            
            # Seek to the beginning of the output stream
            output_pdf.seek(0)
            
            # Prepare the response
            response = send_file(
                output_pdf,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"protected_{secure_filename(file.filename)}"
            )
            
            # Add headers to prevent caching
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            return response

        except Exception as e:
            app.logger.error(f"Error protecting PDF: {str(e)}")
            return jsonify({'error': f"Error protecting PDF: {str(e)}"})

    return render_template('pages/security/protect.html')

@app.route('/pages/security/sign')
def sign():
    return render_template('pages/security/sign.html')

@app.route('/pages/security/compare')
def compare():
    return render_template('pages/security/compare.html')

@app.route('/pages/security/redact')
def redact():
    return render_template('pages/security/redact.html')

@app.route('/pages/security/flatten', methods=['GET', 'POST'])
def flatten():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('pages/security/flatten.html', 
                                error="No file selected")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('pages/security/flatten.html', 
                                error="No file selected")
            
        if not file.filename.lower().endswith('.pdf'):
            return render_template('pages/security/flatten.html', 
                                error="Please upload a PDF file")
        
        temp_input = None
        temp_output = None
        
        try:
            # Create temporary files with unique names
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            
            # Close the temporary files immediately to release handles
            temp_input_path = temp_input.name
            temp_output_path = temp_output.name
            temp_input.close()
            temp_output.close()
            
            # Save uploaded file to temp input
            file.save(temp_input_path)
            
            # Get form parameters
            flatten_annotations = request.form.get('flatten_annotations', 'true').lower() == 'true'
            flatten_form_fields = request.form.get('flatten_form_fields', 'true').lower() == 'true'
            
            # Flatten the PDF
            result = flatten_pdf(
                input_path=temp_input_path,
                output_path=temp_output_path,
                flatten_annotations=flatten_annotations,
                flatten_form_fields=flatten_form_fields
            )
            
            # Read the output PDF into memory
            with open(temp_output_path, 'rb') as f:
                pdf_data = BytesIO(f.read())
            
            # Clean up temporary files
            try:
                os.unlink(temp_input_path)
                os.unlink(temp_output_path)
            except (PermissionError, OSError) as e:
                app.logger.warning(f"Failed to delete temporary files: {e}")
            
            # Send the flattened PDF
            return send_file(
                pdf_data,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"flattened_{secure_filename(file.filename)}"
            )
            
        except Exception as e:
            # Clean up temporary files in case of error
            if temp_input and os.path.exists(temp_input.name):
                try:
                    os.unlink(temp_input.name)
                except (PermissionError, OSError):
                    pass
                    
            if temp_output and os.path.exists(temp_output.name):
                try:
                    os.unlink(temp_output.name)
                except (PermissionError, OSError):
                    pass
                    
            return render_template('pages/security/flatten.html', 
                                error=f"Error flattening PDF: {str(e)}")
    
    return render_template('pages/security/flatten.html')

#------------------------- File Uploads -------------------------

@app.route('/pages/optimise/compress', methods=['GET', 'POST'], endpoint='compress_pdf')
def compress():
    return compress_view()

if __name__ == "__main__":
    app.run(debug=True)