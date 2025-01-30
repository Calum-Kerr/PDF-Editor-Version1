from io import BytesIO
from flask import request, render_template, send_file

def compress_view():
    if request.method == 'POST':
        pdf_file = request.files.get('pdf_file')
        if not pdf_file or pdf_file.filename == '':
            return "No file selected!", 400
        in_memory_file = BytesIO(pdf_file.read())
        in_memory_file.seek(0)
        return send_file(
            in_memory_file,
            as_attachment=True,
            download_name="compressed.pdf"
        )
    return render_template('pages/optimise/compress.html')