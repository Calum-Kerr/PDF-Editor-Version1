from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
from pypdf import PdfWriter, PdfReader

def merge_view():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if files:
            merger = PdfWriter()
            for file in files:
                if file and file.filename.lower().endswith('.pdf'):
                    try:
                        pdf_reader = PdfReader(BytesIO(file.read()))
                        for page in pdf_reader.pages:
                            merger.add_page(page)
                    except Exception as e:
                        print(f"Error processing {file.filename}: {e}")
                        continue

            output_buffer = BytesIO()
            merger.write(output_buffer)
            output_buffer.seek(0)

            return send_file(output_buffer, download_name='merged.pdf', as_attachment=True)



    return render_template('pages/organise/merge.html')