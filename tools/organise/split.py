"""
PDF Split Module

This module provides functionality for splitting PDF files into multiple PDFs.
It supports splitting by individual pages, page ranges, or file size.
"""

import os
import logging
import fitz  # PyMuPDF
from app.errors import PDFProcessingError
from flask import render_template, request, send_file, jsonify
import tempfile
from werkzeug.utils import secure_filename
from pypdf import PdfReader, PdfWriter
from io import BytesIO
import zipfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def split_pdf(input_path, output_dir, split_method='pages', page_ranges=None, max_size=None):
    """
    Split a PDF file into multiple PDFs.

    Args:
        input_path (str): Path to the input PDF file.
        output_dir (str): Directory where the split PDFs will be saved.
        split_method (str, optional): Method to use for splitting. Options:
            - 'pages': Split into individual pages.
            - 'range': Split by page ranges.
            - 'size': Split by file size.
            Defaults to 'pages'.
        page_ranges (str, optional): Page ranges to split by, e.g., '1-3,4-6'.
            Required if split_method is 'range'.
        max_size (int, optional): Maximum size in MB for each split PDF.
            Required if split_method is 'size'.

    Returns:
        dict: A dictionary containing information about the split:
            - 'input_page_count': Number of pages in the input PDF.
            - 'output_count': Number of output PDFs created.
            - 'output_files': List of paths to the output PDFs.

    Raises:
        PDFProcessingError: If the split fails.
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            raise PDFProcessingError(f"Input file not found: {input_path}")

        # Validate output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Validate split method
        valid_methods = ['pages', 'range', 'size']
        if split_method not in valid_methods:
            raise PDFProcessingError(f"Invalid split method: {split_method}. Valid methods: {', '.join(valid_methods)}")

        # Validate page ranges if method is 'range'
        if split_method == 'range' and not page_ranges:
            raise PDFProcessingError("Page ranges must be provided when split method is 'range'")

        # Validate max size if method is 'size'
        if split_method == 'size' and not max_size:
            raise PDFProcessingError("Maximum size must be provided when split method is 'size'")

        # Open the input PDF
        doc = fitz.open(input_path)

        # Get the input page count
        input_page_count = doc.page_count

        # Get the base filename without extension
        base_filename = os.path.basename(input_path)
        base_filename = os.path.splitext(base_filename)[0]

        # Initialize output files list
        output_files = []

        # Split the PDF based on the specified method
        if split_method == 'pages':
            # Split into individual pages
            for page_num in range(input_page_count):
                # Create a new PDF document
                new_doc = fitz.open()

                # Insert the page
                new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

                # Generate output filename
                output_filename = f"{base_filename}_page_{page_num + 1}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                # Save the new document
                new_doc.save(output_path)

                # Add to output files list
                output_files.append(output_path)

                # Close the new document
                new_doc.close()

        elif split_method == 'range':
            # Parse page ranges
            ranges = parse_page_ranges(page_ranges, input_page_count)

            # Split by page ranges
            for i, page_range in enumerate(ranges):
                # Create a new PDF document
                new_doc = fitz.open()

                # Get start and end page numbers (0-based)
                start_page = page_range[0] - 1
                end_page = page_range[1] - 1

                # Insert the pages
                new_doc.insert_pdf(doc, from_page=start_page, to_page=end_page)

                # Generate output filename
                output_filename = f"{base_filename}_pages_{page_range[0]}-{page_range[1]}.pdf"
                output_path = os.path.join(output_dir, output_filename)

                # Save the new document
                new_doc.save(output_path)

                # Add to output files list
                output_files.append(output_path)

                # Close the new document
                new_doc.close()

        elif split_method == 'size':
            # Convert max size from MB to bytes
            max_bytes = max_size * 1024 * 1024

            # Split by file size
            current_doc = fitz.open()
            current_size = 0
            part_num = 1

            for page_num in range(input_page_count):
                # Create a temporary document with just this page
                temp_doc = fitz.open()
                temp_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

                # Save to a temporary file to get its size
                temp_path = os.path.join(output_dir, "_temp.pdf")
                temp_doc.save(temp_path)
                temp_size = os.path.getsize(temp_path)
                os.remove(temp_path)
                temp_doc.close()

                # Check if adding this page would exceed the max size
                if current_size + temp_size > max_bytes and current_doc.page_count > 0:
                    # Save the current document
                    output_filename = f"{base_filename}_part_{part_num}.pdf"
                    output_path = os.path.join(output_dir, output_filename)
                    current_doc.save(output_path)
                    output_files.append(output_path)

                    # Start a new document
                    current_doc.close()
                    current_doc = fitz.open()
                    current_size = 0
                    part_num += 1

                # Add the page to the current document
                current_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                current_size += temp_size

            # Save the last document if it has any pages
            if current_doc.page_count > 0:
                output_filename = f"{base_filename}_part_{part_num}.pdf"
                output_path = os.path.join(output_dir, output_filename)
                current_doc.save(output_path)
                output_files.append(output_path)
                current_doc.close()

        # Close the input document
        doc.close()

        return {
            'input_page_count': input_page_count,
            'output_count': len(output_files),
            'output_files': output_files
        }

    except PDFProcessingError:
        # Re-raise PDFProcessingError
        raise

    except Exception as e:
        logger.error(f"Error splitting PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to split PDF: {str(e)}")


def parse_page_ranges(ranges_str, max_pages):
    """Parse page ranges string into list of page numbers"""
    pages = set()
    ranges = ranges_str.replace(' ', '').split(',')
    
    for r in ranges:
        try:
            if '-' in r:
                start, end = map(int, r.split('-'))
                if start < 1 or end > max_pages or start > end:
                    raise ValueError
                pages.update(range(start - 1, end))
            else:
                page = int(r)
                if page < 1 or page > max_pages:
                    raise ValueError
                pages.add(page - 1)
        except ValueError:
            raise ValueError(f"Invalid page range: {r}")
    
    return sorted(list(pages))


def split_view():
    if request.method == 'POST':
        if 'fileElem' not in request.files:
            return render_template('pages/organise/split.html', 
                                error="No file selected")
        
        file = request.files['fileElem']
        
        if file.filename == '':
            return render_template('pages/organise/split.html', 
                                error="No file selected")
            
        if not file.filename.lower().endswith('.pdf'):
            return render_template('pages/organise/split.html', 
                                error="Please upload a PDF file")
            
        try:
            # Read the PDF file
            pdf_bytes = BytesIO(file.read())
            pdf_reader = PdfReader(pdf_bytes)
            total_pages = len(pdf_reader.pages)
            
            # Create a ZIP file in memory to store split PDFs
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                split_type = request.form.get('splitType', 'range')
                
                if split_type == 'range':
                    page_ranges = request.form.get('pageRanges', '').strip()
                    if not page_ranges:
                        return render_template('pages/organise/split.html', 
                                            error="Please specify page ranges")
                    
                    try:
                        pages = parse_page_ranges(page_ranges, total_pages)
                    except ValueError as e:
                        return render_template('pages/organise/split.html', 
                                            error=str(e))
                    
                    # Create PDF for specified range
                    output = PdfWriter()
                    for page_num in pages:
                        output.add_page(pdf_reader.pages[page_num])
                    
                    # Save to zip file
                    pdf_output = BytesIO()
                    output.write(pdf_output)
                    pdf_output.seek(0)
                    zip_file.writestr(f'split_pages_{page_ranges}.pdf', pdf_output.getvalue())
                    
                else:  # individual pages
                    # Split each page into a separate PDF
                    for page_num in range(total_pages):
                        output = PdfWriter()
                        output.add_page(pdf_reader.pages[page_num])
                        
                        # Save to zip file
                        pdf_output = BytesIO()
                        output.write(pdf_output)
                        pdf_output.seek(0)
                        zip_file.writestr(f'page_{page_num + 1}.pdf', pdf_output.getvalue())
            
            # Prepare zip file for download
            zip_buffer.seek(0)
            return send_file(
                zip_buffer,
                mimetype='application/zip',
                as_attachment=True,
                download_name='split_pdfs.zip'
            )
            
        except Exception as e:
            return render_template('pages/organise/split.html', 
                                error=f"Error processing PDF: {str(e)}")
            
    return render_template('pages/organise/split.html')