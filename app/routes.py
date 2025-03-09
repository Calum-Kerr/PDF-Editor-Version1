from flask import render_template, request, redirect, send_from_directory, url_for
from werkzeug.utils import secure_filename
from app import app
from io import BytesIO
import os
import fitz

from tools.convert.jpg_to_pdf import jpg_to_pdf_view
from tools.optimise.compress import compress_view
from tools.convert.pdf_to_panoramic import pdf_to_panoramic_view

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

@app.route('/pages/organise/merge')
def merge():
    return render_template('pages/organise/merge.html')

@app.route('/pages/organise/remove')
def remove():
    return render_template('pages/organise/remove.html')

@app.route('/pages/organise/sort')
def sort():
    return render_template('pages/organise/sort.html')

@app.route('/pages/organise/rotate')
def rotate():
    return render_template('pages/organise/rotate.html')

@app.route('/pages/organise/split')
def split():
    return render_template('pages/organise/split.html')

# Security
@app.route('/pages/security/unlock')
def unlock():
    return render_template('pages/security/unlock.html')

@app.route('/pages/security/protect')
def protect():
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

@app.route('/pages/security/flatten')
def flatten():
    return render_template('pages/security/flatten.html')

#------------------------- File Uploads -------------------------

@app.route('/pages/optimise/compress', methods=['GET', 'POST'], endpoint='compress_pdf')
def compress():
    return compress_view()

if __name__ == "__main__":
    app.run(debug=True)