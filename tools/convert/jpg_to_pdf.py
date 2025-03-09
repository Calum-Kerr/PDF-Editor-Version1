from flask import Flask, request, send_file, render_template, jsonify
from PIL import Image
import io

def jpg_to_pdf_view():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify(error="No file part in the request"), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify(error="No selected file"), 400

        if file and file.filename.lower().endswith(('.jpg', '.jpeg')):
            try:
                img = Image.open(file).convert('RGB')
                pdf_bytes = io.BytesIO()
                img.save(pdf_bytes, format="PDF")
                pdf_bytes.seek(0)
                return send_file(pdf_bytes, as_attachment=True, download_name="converted.pdf", mimetype="application/pdf")
            except Exception as e:
                return jsonify(error="Failed to convert image to PDF"), 500
        else:
            return jsonify(error="Invalid file type. Only .jpg and .jpeg are allowed"), 400

    return render_template('pages/convert/jpg_to_pdf.html')