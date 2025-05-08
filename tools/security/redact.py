import os
import tempfile
from flask import render_template, request, send_file, jsonify
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw
import io
import base64
import json
from app import app

def redact_pdf(input_file, redaction_areas, redaction_color=(0, 0, 0)):
    """
    Permanently redact content from a PDF based on specified areas.
    
    Args:
        input_file: Path to the input PDF file
        redaction_areas: Dict mapping page numbers to lists of redaction rectangles
                        {page_num: [(x1, y1, x2, y2), ...], ...}
        redaction_color: RGB color tuple for the redaction area (default black)
    
    Returns:
        Path to the redacted PDF file
    """
    # Open the input PDF
    doc = fitz.open(input_file)
    
    # Process each page with redactions
    for page_num_str, areas in redaction_areas.items():
        page_num = int(page_num_str)
        if page_num < 0 or page_num >= len(doc):
            continue  # Skip invalid page numbers
            
        page = doc[page_num]
        
        # Add each redaction area to the page
        for rect in areas:
            x1, y1, x2, y2 = map(float, rect)
            redact_rect = fitz.Rect(x1, y1, x2, y2)
            
            # First - add redaction annotation
            annot = page.add_redact_annot(redact_rect, fill=redaction_color)
            
            # Then - apply the redaction to permanently remove content
            page.apply_redactions()
    
    # Create temporary file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
    os.close(output_fd)
    
    # Save the redacted PDF
    doc.save(output_path)
    doc.close()
    
    return output_path

def get_page_image(pdf_path, page_num, zoom=2.0):
    """
    Extract an image of a specific page from a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to extract (0-indexed)
        zoom: Zoom factor for higher resolution images
    
    Returns:
        Base64 encoded string of the page image and page dimensions
    """
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        if page_num < 0 or page_num >= len(doc):
            return None
            
        # Get the page
        page = doc[page_num]
        
        # Set the transformation matrix for higher resolution
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Get original page dimensions
        page_rect = page.rect
        original_width = page_rect.width
        original_height = page_rect.height
        
        # Convert to PIL Image
        img_data = pix.tobytes("png")
        img_bytes = io.BytesIO(img_data)
        
        # Convert to base64
        img_str = base64.b64encode(img_bytes.getvalue()).decode()
        
        doc.close()
        
        return {
            "image": img_str,
            "width": original_width,
            "height": original_height,
            "zoom": zoom
        }
        
    except Exception as e:
        print(f"Error generating page image: {e}")
        return None

def detect_text_areas(pdf_path, page_num):
    """
    Detect text areas on a page for assisted redaction.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number to analyze (0-indexed)
    
    Returns:
        List of rectangles (x1, y1, x2, y2) containing text
    """
    try:
        # Open the PDF file
        doc = fitz.open(pdf_path)
        
        if page_num < 0 or page_num >= len(doc):
            return []
            
        # Get the page
        page = doc[page_num]
        
        # Extract text blocks
        text_areas = []
        for block in page.get_text("blocks"):
            # Each block is (x0, y0, x1, y1, text, block_no, block_type)
            if block[4].strip():  # Non-empty text
                rect = fitz.Rect(block[0], block[1], block[2], block[3])
                # Add a small margin around the text
                rect.x0 -= 2
                rect.y0 -= 2
                rect.x1 += 2
                rect.y1 += 2
                text_areas.append((rect.x0, rect.y0, rect.x1, rect.y1))
        
        doc.close()
        return text_areas
        
    except Exception as e:
        print(f"Error detecting text areas: {e}")
        return []

def redact_view():
    if request.method == 'POST':
        # Check if it's an AJAX request for page preview
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if 'get_page' in request.form:
                # Get PDF file from session or temp storage
                temp_pdf = request.form.get('pdf_path')
                # Replace forward slashes back to backslashes for Windows paths
                temp_pdf = temp_pdf.replace('/', '\\')
                page_num = int(request.form.get('page_num', 0))
                
                # Add debugging output
                print(f"Attempting to access PDF file: {temp_pdf}")
                print(f"File exists: {os.path.exists(temp_pdf)}")
                
                if not temp_pdf or not os.path.exists(temp_pdf):
                    return jsonify({"status": "error", "message": f"PDF file not found at: {temp_pdf}"})
                    
                # Get the page image
                page_data = get_page_image(temp_pdf, page_num)
                
                if page_data:
                    # Add total pages information
                    doc = fitz.open(temp_pdf)
                    page_data["total_pages"] = len(doc)
                    doc.close()
                    
                    # Also detect text areas if requested
                    if request.form.get('detect_text', '0') == '1':
                        text_areas = detect_text_areas(temp_pdf, page_num)
                        page_data["text_areas"] = text_areas
                        
                    return jsonify({"status": "success", "page": page_data})
                else:
                    return jsonify({"status": "error", "message": "Failed to get page image"})
                    
            elif 'apply_redactions' in request.form:
                # Apply redactions to PDF
                temp_pdf = request.form.get('pdf_path')
                # Replace forward slashes back to backslashes for Windows paths
                temp_pdf = temp_pdf.replace('/', '\\')
                redaction_data = json.loads(request.form.get('redaction_data', '{}'))
                
                print(f"Applying redactions to PDF at: {temp_pdf}")
                print(f"File exists: {os.path.exists(temp_pdf)}")
                
                if not temp_pdf or not os.path.exists(temp_pdf):
                    return jsonify({"status": "error", "message": f"PDF file not found at: {temp_pdf}"})
                    
                try:
                    # Apply redactions
                    output_path = redact_pdf(temp_pdf, redaction_data)
                    
                    # Return success with the path to download
                    return jsonify({
                        "status": "success", 
                        "message": "Redactions applied successfully",
                        "output_path": output_path
                    })
                except Exception as e:
                    print(f"Error applying redactions: {str(e)}")
                    return jsonify({"status": "error", "message": f"Error applying redactions: {str(e)}"})
                
            return jsonify({"status": "error", "message": "Invalid request"})
        
        # Regular form submission - initial PDF upload
        if 'file' not in request.files:
            return render_template('pages/security/redact.html', 
                                  error="No file selected")
        
        file = request.files['file']
        
        # Check if the file is empty
        if file.filename == '':
            return render_template('pages/security/redact.html', 
                                  error="No file selected")
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return render_template('pages/security/redact.html', 
                                  error="Please upload a PDF file")
        
        try:
            # Secure the filename and save the file temporarily
            filename = secure_filename(file.filename)
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"redact_{filename}")
            
            # Save file
            file.save(temp_path)
            
            # Verify file was saved and is valid
            if not os.path.exists(temp_path):
                return render_template('pages/security/redact.html', 
                                      error="Failed to save uploaded file")
                                      
            # Verify it's a valid PDF by trying to open it
            try:
                doc = fitz.open(temp_path)
                page_count = len(doc)
                doc.close()
                print(f"Successfully saved PDF with {page_count} pages at: {temp_path}")
            except Exception as e:
                os.remove(temp_path)
                return render_template('pages/security/redact.html', 
                                      error=f"Invalid PDF file: {str(e)}")
            
            # Convert backslashes to forward slashes for the template
            # This avoids escaping issues in HTML/JavaScript
            template_path = temp_path.replace('\\', '/')
            
            # Redirect to the redaction interface with the temp file path
            return render_template('pages/security/redact.html', 
                                  pdf_path=template_path,
                                  filename=filename)
        except Exception as e:
            print(f"Error processing upload: {str(e)}")
            return render_template('pages/security/redact.html', 
                                  error=f"Error processing file: {str(e)}")
        
    # Handle the download request after redaction
    if 'download' in request.args:
        output_path = request.args.get('output_path')
        # Replace forward slashes back to backslashes if needed
        output_path = output_path.replace('/', '\\')
        filename = request.args.get('filename', 'redacted.pdf')
        
        if output_path and os.path.exists(output_path):
            return send_file(
                output_path,
                as_attachment=True,
                download_name=f"redacted_{filename}",
                mimetype='application/pdf'
            )
        else:
            return render_template('pages/security/redact.html',
                                  error=f"Redacted file not found at: {output_path}")
    
    # GET request - show initial upload form
    return render_template('pages/security/redact.html')
