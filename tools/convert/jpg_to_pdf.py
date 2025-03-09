from flask import Flask, request, send_file, render_template
from PIL import Image
import io

def jpg_to_pdf_view():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file uploaded", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        if file:
            img = Image.open(file).convert('RGB')
            pdf_bytes = io.BytesIO()
            img.save(pdf_bytes, format="PDF")
            pdf_bytes.seek(0)

            return send_file(pdf_bytes, as_attachment=True, download_name="converted.pdf", mimetype="application/pdf")

    return render_template('pages/convert/jpg_to_pdf.html')