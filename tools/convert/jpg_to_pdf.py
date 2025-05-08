"""
Image to PDF Conversion Module

This module provides functionality for converting image files to PDF format
using PyMuPDF (fitz).
"""

import os
import logging
import fitz  # PyMuPDF
from PIL import Image
from app.errors import PDFProcessingError
from flask import render_template, request, send_file
from werkzeug.utils import secure_filename
import tempfile
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_image_to_pdf(input_path, output_path, page_size='a4', orientation='portrait'):
    """
    Convert an image file to PDF.

    Args:
        input_path (str): Path to the input image file.
        output_path (str): Path where the PDF will be saved.
        page_size (str, optional): Page size for the PDF. Options: 'a4', 'letter', 'legal', 'a3', 'a5', 'original'.
            Defaults to 'a4'.
        orientation (str, optional): Page orientation. Options: 'portrait', 'landscape'.
            Defaults to 'portrait'.

    Returns:
        dict: A dictionary containing information about the conversion:
            - 'image_width': Width of the original image in pixels.
            - 'image_height': Height of the original image in pixels.
            - 'pdf_width': Width of the PDF page in points.
            - 'pdf_height': Height of the PDF page in points.
            - 'page_size': Page size used for the PDF.
            - 'orientation': Orientation used for the PDF.

    Raises:
        PDFProcessingError: If the conversion fails.
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            raise PDFProcessingError(f"Input file not found: {input_path}")

        # Validate page size
        valid_page_sizes = ['a4', 'letter', 'legal', 'a3', 'a5', 'original']
        if page_size not in valid_page_sizes:
            logger.warning(f"Invalid page size: {page_size}. Using 'a4' instead.")
            page_size = 'a4'

        # Validate orientation
        valid_orientations = ['portrait', 'landscape']
        if orientation not in valid_orientations:
            logger.warning(f"Invalid orientation: {orientation}. Using 'portrait' instead.")
            orientation = 'portrait'

        # Open the image with PIL to get its dimensions
        with Image.open(input_path) as img:
            img_width, img_height = img.size

        # Define page sizes in points (1 point = 1/72 inch)
        page_sizes = {
            'a4': (595, 842),  # 210mm x 297mm
            'letter': (612, 792),  # 8.5in x 11in
            'legal': (612, 1008),  # 8.5in x 14in
            'a3': (842, 1191),  # 297mm x 420mm
            'a5': (420, 595),  # 148mm x 210mm
            'original': (img_width, img_height)  # Use image dimensions
        }

        # Get the page dimensions based on size and orientation
        if page_size == 'original':
            # For original size, we use the image dimensions directly
            pdf_width, pdf_height = img_width, img_height
        else:
            # For standard page sizes, we may need to swap dimensions for landscape
            pdf_width, pdf_height = page_sizes[page_size]
            if orientation == 'landscape' and page_size != 'original':
                pdf_width, pdf_height = pdf_height, pdf_width

        # Create a new PDF document
        doc = fitz.open()

        # Add a new page with the specified dimensions
        page = doc.new_page(width=pdf_width, height=pdf_height)

        # Calculate the rectangle for the image
        if page_size == 'original':
            # For original size, use the full page
            rect = fitz.Rect(0, 0, pdf_width, pdf_height)
        else:
            # For standard page sizes, fit the image within the page while maintaining aspect ratio
            img_aspect = img_width / img_height
            page_aspect = pdf_width / pdf_height

            if img_aspect > page_aspect:
                # Image is wider than the page (relative to height)
                # Scale based on width
                scaled_width = pdf_width
                scaled_height = scaled_width / img_aspect
                top_margin = (pdf_height - scaled_height) / 2
                rect = fitz.Rect(0, top_margin, pdf_width, top_margin + scaled_height)
            else:
                # Image is taller than the page (relative to width)
                # Scale based on height
                scaled_height = pdf_height
                scaled_width = scaled_height * img_aspect
                left_margin = (pdf_width - scaled_width) / 2
                rect = fitz.Rect(left_margin, 0, left_margin + scaled_width, pdf_height)

        # Insert the image into the page
        page.insert_image(rect, filename=input_path)

        # Save the PDF
        doc.save(output_path)
        doc.close()

        return {
            'image_width': img_width,
            'image_height': img_height,
            'pdf_width': pdf_width,
            'pdf_height': pdf_height,
            'page_size': page_size,
            'orientation': orientation
        }

    except Exception as e:
        logger.error(f"Error converting image to PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to convert image to PDF: {str(e)}")


def get_page_size_dimensions(page_size, orientation='portrait'):
    """
    Get the dimensions for a page size in points.

    Args:
        page_size (str): Page size. Options: 'a4', 'letter', 'legal', 'a3', 'a5'.
        orientation (str, optional): Page orientation. Options: 'portrait', 'landscape'.
            Defaults to 'portrait'.

    Returns:
        tuple: A tuple containing the width and height in points.
    """
    # Define page sizes in points (1 point = 1/72 inch)
    page_sizes = {
        'a4': (595, 842),  # 210mm x 297mm
        'letter': (612, 792),  # 8.5in x 11in
        'legal': (612, 1008),  # 8.5in x 14in
        'a3': (842, 1191),  # 297mm x 420mm
        'a5': (420, 595),  # 148mm x 210mm
    }

    # Get the dimensions
    width, height = page_sizes.get(page_size.lower(), page_sizes['a4'])

    # Swap dimensions for landscape orientation
    if orientation.lower() == 'landscape':
        width, height = height, width

    return width, height


def jpg_to_pdf_view():
    """
    Flask view function for handling JPG to PDF conversion requests.
    """
    temp_input = None
    temp_output = None
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('pages/convert/jpg_to_pdf.html', 
                                error="No file selected")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('pages/convert/jpg_to_pdf.html', 
                                error="No file selected")
            
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            return render_template('pages/convert/jpg_to_pdf.html', 
                                error="Please upload a JPG or PNG file")
            
        try:
            # Create temporary input file
            temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
            file.save(temp_input.name)
            temp_input.close()
            
            # Create temporary output file
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_output.close()
            
            # Get form parameters
            page_size = request.form.get('page_size', 'a4')
            orientation = request.form.get('orientation', 'portrait')
            
            # Convert the image to PDF
            result = convert_image_to_pdf(
                input_path=temp_input.name,
                output_path=temp_output.name,
                page_size=page_size,
                orientation=orientation
            )
            
            # Read the output PDF into memory
            with open(temp_output.name, 'rb') as f:
                pdf_data = BytesIO(f.read())
            
            # Prepare the response
            response = send_file(
                pdf_data,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f"{os.path.splitext(secure_filename(file.filename))[0]}.pdf"
            )
            
            # Clean up temporary files
            try:
                if os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary input file: {e}")
                
            try:
                if os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary output file: {e}")
            
            return response
            
        except Exception as e:
            # Clean up temporary files in case of error
            try:
                if temp_input and os.path.exists(temp_input.name):
                    os.unlink(temp_input.name)
            except Exception as cleanup_error:
                logger.warning(f"Failed to delete temporary input file: {cleanup_error}")
                
            try:
                if temp_output and os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
            except Exception as cleanup_error:
                logger.warning(f"Failed to delete temporary output file: {cleanup_error}")
                
            return render_template('pages/convert/jpg_to_pdf.html', 
                                error=f"Error converting image to PDF: {str(e)}")
            
    return render_template('pages/convert/jpg_to_pdf.html')
