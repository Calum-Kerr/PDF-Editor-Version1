import os
import fitz  # PyMuPDF
from flask import render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import tempfile
from app import app

def create_panoramic_pdf(input_file, page_range=None, direction='horizontal'):
    """
    Create a panoramic PDF by stitching pages side by side.
    
    Args:
        input_file: Path to the input PDF file
        page_range: Range of pages to include (None for all pages)
        direction: 'horizontal' or 'vertical' stitching
    
    Returns:
        Path to the generated panoramic PDF
    """
    # Open the input PDF
    doc = fitz.open(input_file)
    
    # Determine which pages to include
    if page_range:
        pages_to_include = [i for i in range(doc.page_count) if i+1 in page_range]
    else:
        pages_to_include = range(doc.page_count)
    
    # Create a new PDF document
    new_doc = fitz.open()
    
    if direction == 'horizontal':
        # Calculate dimensions for the panoramic page
        total_width = sum(doc[i].rect.width for i in pages_to_include)
        max_height = max(doc[i].rect.height for i in pages_to_include)
        
        # Create a new page with the panoramic dimensions
        new_page = new_doc.new_page(width=total_width, height=max_height)
        
        # Copy content from each page
        x_offset = 0
        for page_num in pages_to_include:
            page = doc[page_num]
            rect = page.rect
            
            # Create a transformation matrix to position the page content
            # Instead of using rect.translate which doesn't exist, we'll create a new rect at offset position
            target_rect = fitz.Rect(
                x_offset, 0, 
                x_offset + rect.width, rect.height
            )
            
            # Copy the page content to the new panoramic page
            new_page.show_pdf_page(target_rect, doc, page_num)
            
            # Update offset for the next page
            x_offset += rect.width
    else:  # vertical
        # Calculate dimensions for the panoramic page
        max_width = max(doc[i].rect.width for i in pages_to_include)
        total_height = sum(doc[i].rect.height for i in pages_to_include)
        
        # Create a new page with the panoramic dimensions
        new_page = new_doc.new_page(width=max_width, height=total_height)
        
        # Copy content from each page
        y_offset = 0
        for page_num in pages_to_include:
            page = doc[page_num]
            rect = page.rect
            
            # Create a transformation matrix to position the page content
            # Instead of using rect.translate which doesn't exist, we'll create a new rect at offset position
            target_rect = fitz.Rect(
                0, y_offset, 
                rect.width, y_offset + rect.height
            )
            
            # Copy the page content to the new panoramic page
            new_page.show_pdf_page(target_rect, doc, page_num)
            
            # Update offset for the next page
            y_offset += rect.height
    
    # Create temporary file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
    os.close(output_fd)
    
    # Save the panoramic PDF
    new_doc.save(output_path)
    
    # Close documents
    doc.close()
    new_doc.close()
    
    return output_path

def pdf_to_panoramic_view():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            return render_template('pages/convert/pdf_to_panoramic.html', 
                                  error="No file selected")
        
        file = request.files['file']
        
        # Check if the file is empty
        if file.filename == '':
            return render_template('pages/convert/pdf_to_panoramic.html', 
                                  error="No file selected")
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return render_template('pages/convert/pdf_to_panoramic.html', 
                                  error="Please upload a PDF file")
        
        # Secure the filename and save the file temporarily
        filename = secure_filename(file.filename)
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        file.save(temp_path)
        
        # Get pagination options
        page_range_str = request.form.get('page_range', '')
        direction = request.form.get('direction', 'horizontal')
        
        # Process page range
        page_range = None
        if page_range_str.strip():
            try:
                # Parse page range like "1-3,5,7-9"
                page_range = []
                for part in page_range_str.split(','):
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        page_range.extend(range(start, end + 1))
                    else:
                        page_range.append(int(part))
            except ValueError:
                os.unlink(temp_path)  # Clean up the temp file
                return render_template('pages/convert/pdf_to_panoramic.html', 
                                      error="Invalid page range format")
        
        try:
            # Create the panoramic PDF
            output_path = create_panoramic_pdf(temp_path, page_range, direction)
            
            # Close and delete the temp input file
            try:
                os.unlink(temp_path)
            except (PermissionError, OSError):
                # If we can't delete it now, we'll just continue
                pass
            
            # Return the generated file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"panoramic_{filename}",
                mimetype='application/pdf'
            )
            
        except Exception as e:
            # Clean up temp files
            try:
                os.unlink(temp_path)
            except (PermissionError, OSError):
                pass
                
            if 'output_path' in locals():
                try:
                    os.unlink(output_path)
                except (PermissionError, OSError):
                    pass
                
            return render_template('pages/convert/pdf_to_panoramic.html', 
                                  error=f"Error creating panoramic PDF: {str(e)}")
            
    return render_template('pages/convert/pdf_to_panoramic.html')
