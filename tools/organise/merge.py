from flask import render_template, request, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
from pypdf import PdfWriter, PdfReader


def merge_view():
    if request.method == 'POST':
        files = request.files.getlist('files')
        output_filename = request.form.get('outputFilename', '').strip()

        # Set default filename if none is provided
        if not output_filename:
            output_filename = 'merged.pdf'
        else:
            output_filename = secure_filename(output_filename)  # Sanitize the filename
            # Ensure the filename ends with .pdf
            if not output_filename.lower().endswith('.pdf'):
                output_filename += '.pdf'

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
                        return render_template('pages/organise/merge.html', 
                                            error=f"Error processing {file.filename}: {str(e)}")

            output_buffer = BytesIO()
            merger.write(output_buffer)
            output_buffer.seek(0)

            return send_file(
                output_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=output_filename
            )

        return render_template('pages/organise/merge.html', 
                             error="No files were uploaded")

    return render_template('pages/organise/merge.html')