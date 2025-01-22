from flask import request, render_template, send_from_directory
import fitz  # PyMuPDF
import os
from app import app

UPLOAD_FOLDER = 'uploads'
COMPRESSED_FOLDER = 'compressed'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPRESSED_FOLDER, exist_ok=True)

@app.route('/pages/optimise/compress', methods=['GET', 'POST'])
def compress_pdf():
    if request.method == 'POST':
        # Get the uploaded file and compression level
        uploaded_file = request.files['pdfFile']
        compression_level = request.form['compressionLevel']

        if uploaded_file and uploaded_file.filename.endswith('.pdf'):
            # Save the uploaded file
            input_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(input_path)

            # Output file path
            output_filename = f"compressed_{uploaded_file.filename}"
            output_path = os.path.join(COMPRESSED_FOLDER, output_filename)

            # Compression logic using PyMuPDF
            doc = fitz.open(input_path)
            for page in doc:
                pix = page.get_pixmap()
                # Adjust DPI based on compression level
                if compression_level == "low":
                    pix.set_dpi(72, 72)
                elif compression_level == "medium":
                    pix.set_dpi(144, 144)
                elif compression_level == "high":
                    pix.set_dpi(300, 300)

                # Write the compressed page
                page.insert_image(fitz.Rect(0, 0, pix.width, pix.height), pixmap=pix)
            doc.save(output_path, deflate=True)
            doc.close()

            # Return the filename for downloading
            return render_template('pages/optimise/compress.html', compressed_file=output_filename)

    return render_template('pages/optimise/compress.html')


@app.route('/compressed/<filename>')
def serve_compressed_file(filename):
    return send_from_directory(COMPRESSED_FOLDER, filename)