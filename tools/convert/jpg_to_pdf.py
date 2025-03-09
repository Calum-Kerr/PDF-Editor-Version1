from flask import Flask, request, send_file, render_template, jsonify
from PIL import Image
import io

def jpg_to_pdf_view():
    """
    Handles requests for JPG to PDF conversion.
    """
    if request.method == 'POST':  # Check if the request method is POST (form submission)
        if 'file' not in request.files:  # Check if a file was uploaded in the request
            return jsonify(error="No file part in the request"), 400  # Return error if no file part

        file = request.files['file']  # Get the uploaded file object

        if file.filename == '':  # Check if the user selected a file
            return jsonify(error="No selected file"), 400  # Return error if no file selected

        if file and file.filename.lower().endswith(('.jpg', '.jpeg')):  # Check if the file is a JPG or JPEG
            try:
                img = Image.open(file).convert('RGB')  # Open the image using PIL and convert to RGB (important for PDF)
                pdf_bytes = io.BytesIO()  # Create an in-memory byte stream to store the PDF
                img.save(pdf_bytes, format='PDF')  # Save the image to the byte stream in PDF format
                pdf_bytes.seek(0)  # Reset the stream position to the beginning

                return send_file(  # Return the PDF file as a response
                    pdf_bytes,
                    as_attachment=True,  # Force download
                    download_name="converted.pdf",  # Set the downloaded file name
                    mimetype="application/pdf"  # Set the correct MIME type
                )

            except Exception as e:  # Catch any exceptions during the conversion process
                return jsonify(error="Failed to convert image to PDF"), 500  # Return error if conversion fails

        else:
            return jsonify(error="Invalid file type. Only .jpg and .jpeg are allowed"), 400  # Return error for invalid file types

    return render_template('pages/convert/jpg_to_pdf.html')  # Render the HTML template for the conversion form (for GET requests