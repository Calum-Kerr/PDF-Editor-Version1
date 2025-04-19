
from flask import render_template, request, send_file
from werkzeug.utils import secure_filename
from io import BytesIO
from pypdf import PdfWriter, PdfReader
import os
import tempfile
import zipfile

def parse_page_ranges(ranges_str, max_pages):
    """
    Parse page ranges string into list of tuples (start, end).
    Example: "1-3,5,7-9" -> [(1,3), (5,5), (7,9)]
    """
    ranges = []
    parts = ranges_str.replace(' ', '').split(',')
    
    for part in parts:
        try:
            if '-' in part:
                start, end = map(int, part.split('-'))
                if start < 1 or end > max_pages or start > end:
                    raise ValueError(f"Invalid range: {part}")
                ranges.append((start, end))
            else:
                page = int(part)
                if page < 1 or page > max_pages:
                    raise ValueError(f"Page {page} is out of range")
                ranges.append((page, page))
        except ValueError as e:
            raise ValueError(f"Invalid page range: {part}")
    
    return ranges

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
                
                split_type = request.form.get('splitType', 'individual')
                
                if split_type == 'range':
                    page_ranges_str = request.form.get('pageRanges', '').strip()
                    if not page_ranges_str:
                        return render_template('pages/organise/split.html', 
                                            error="Please specify page ranges")
                    
                    try:
                        # Parse the page ranges
                        ranges = parse_page_ranges(page_ranges_str, total_pages)
                        
                        # Create a PDF for each range
                        for i, (start, end) in enumerate(ranges):
                            output = PdfWriter()
                            
                            # Add pages for this range (converting to 0-based index)
                            for page_num in range(start - 1, end):
                                output.add_page(pdf_reader.pages[page_num])
                            
                            # Save to zip file
                            pdf_output = BytesIO()
                            output.write(pdf_output)
                            pdf_output.seek(0)
                            
                            # Generate filename for this range
                            if start == end:
                                filename = f'page_{start}.pdf'
                            else:
                                filename = f'pages_{start}-{end}.pdf'
                            
                            zip_file.writestr(filename, pdf_output.getvalue())
                    
                    except ValueError as e:
                        return render_template('pages/organise/split.html', 
                                            error=str(e))
                    
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
                download_name=f'split_{secure_filename(file.filename)}.zip'
            )
            
        except Exception as e:
            return render_template('pages/organise/split.html', 
                                error=f"Error processing PDF: {str(e)}")
            
    return render_template('pages/organise/split.html')