import os
import tempfile
from flask import render_template, request, send_file
import fitz  # PyMuPDF
from werkzeug.utils import secure_filename
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from app import app

def add_text_watermark(input_file, text, font_size=30, opacity=0.5, position="center", color=(128, 128, 128), 
                       rotation=0, page_range=None):
    """
    Add a text watermark to PDF pages.
    
    Args:
        input_file: Path to the input PDF file
        text: Text to use as watermark
        font_size: Size of the font for the watermark
        opacity: Watermark opacity (0.0 to 1.0)
        position: Position of watermark (center, top-left, top-right, bottom-left, bottom-right)
        color: RGB color tuple for the watermark
        rotation: Rotation angle in degrees
        page_range: Range of pages to include (None for all pages)
    
    Returns:
        Path to the generated PDF with watermark
    """
    # Open the input PDF
    doc = fitz.open(input_file)
    
    # Determine which pages to include
    if page_range:
        pages_to_process = [i for i in range(doc.page_count) if i+1 in page_range]
    else:
        pages_to_process = range(doc.page_count)
    
    # Process each page
    for page_num in pages_to_process:
        page = doc[page_num]
        
        # Get page dimensions
        rect = page.rect
        
        # Set the position based on the page dimensions
        if position == "center":
            x = rect.width / 2
            y = rect.height / 2
        elif position == "top-left":
            x = rect.width * 0.1
            y = rect.height * 0.1
        elif position == "top-right":
            x = rect.width * 0.9
            y = rect.height * 0.1
        elif position == "bottom-left":
            x = rect.width * 0.1
            y = rect.height * 0.9
        elif position == "bottom-right":
            x = rect.width * 0.9
            y = rect.height * 0.9
        else:  # Default to center
            x = rect.width / 2
            y = rect.height / 2
        
        # Create a transparent image with the text for watermarking
        # This approach is more compatible across different PyMuPDF versions
        text_img = create_text_image(
            text, 
            int(rect.width), 
            int(rect.height), 
            font_size, 
            opacity, 
            color, 
            rotation,
            position
        )
        
        # Add the image to the page
        page.insert_image(rect, stream=text_img.getvalue(), overlay=True)
    
    # Create temporary file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
    os.close(output_fd)
    
    # Save the watermarked PDF
    doc.save(output_path)
    doc.close()
    
    return output_path

def add_image_watermark(input_file, image_file, scale=0.3, opacity=0.5, position="center", 
                         rotation=0, page_range=None):
    """
    Add an image watermark to PDF pages.
    
    Args:
        input_file: Path to the input PDF file
        image_file: Path to the image for watermark
        scale: Scale factor for the image (0.0 to 1.0)
        opacity: Watermark opacity (0.0 to 1.0)
        position: Position of watermark (center, top-left, top-right, bottom-left, bottom-right)
        rotation: Rotation angle in degrees
        page_range: Range of pages to include (None for all pages)
    
    Returns:
        Path to the generated PDF with watermark
    """
    # Open the input PDF
    doc = fitz.open(input_file)
    
    # Determine which pages to include
    if page_range:
        pages_to_process = [i for i in range(doc.page_count) if i+1 in page_range]
    else:
        pages_to_process = range(doc.page_count)
    
    # Load and process image
    img = Image.open(image_file)
    
    # Rotate image if needed
    if rotation != 0:
        img = img.rotate(rotation, expand=True, resample=Image.BICUBIC)
    
    # Apply scale
    if scale != 1.0:
        original_width, original_height = img.size
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        img = img.resize((new_width, new_height), Image.BICUBIC)
    
    # Apply opacity
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
    
    # Apply transparency
    alpha = Image.new('L', img.size, int(255 * opacity))
    img.putalpha(alpha)
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Process each page
    for page_num in pages_to_process:
        page = doc[page_num]
        
        # Get page dimensions
        rect = page.rect
        
        # Set the position based on the page dimensions
        img_width, img_height = img.size
        
        if position == "center":
            x = (rect.width - img_width) / 2
            y = (rect.height - img_height) / 2
        elif position == "top-left":
            x = rect.width * 0.05
            y = rect.height * 0.05
        elif position == "top-right":
            x = rect.width * 0.95 - img_width
            y = rect.height * 0.05
        elif position == "bottom-left":
            x = rect.width * 0.05
            y = rect.height * 0.95 - img_height
        elif position == "bottom-right":
            x = rect.width * 0.95 - img_width
            y = rect.height * 0.95 - img_height
        else:  # Default to center
            x = (rect.width - img_width) / 2
            y = (rect.height - img_height) / 2
        
        # Create rectangle for the image insertion
        image_rect = fitz.Rect(x, y, x + img_width, y + img_height)
        
        # Insert the image
        page.insert_image(image_rect, stream=img_bytes.getvalue())
    
    # Create temporary file for the output
    output_fd, output_path = tempfile.mkstemp(suffix=".pdf")
    os.close(output_fd)
    
    # Save the watermarked PDF
    doc.save(output_path)
    doc.close()
    
    return output_path

def create_text_image(text, width, height, font_size=30, opacity=0.5, 
                     color=(128, 128, 128), rotation=0, position="center"):
    """
    Creates a high-quality image containing text for use as a watermark.
    
    Returns:
        BytesIO object containing the image data
    """
    # Create a transparent image with higher resolution
    img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            try:
                # Try to find a system font that might be available
                import matplotlib.font_manager as fm
                system_fonts = fm.findSystemFonts()
                if system_fonts:
                    font = ImageFont.truetype(system_fonts[0], font_size)
                else:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
    
    # Add alpha to color for transparency
    rgba_color = color + (int(opacity * 255),)
    
    # Calculate text size
    try:
        # For newer Pillow versions
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
    except AttributeError:
        # Fallback for older Pillow versions
        text_width, text_height = draw.textsize(text, font=font)
    
    # Set the position based on the page dimensions
    if position == "center":
        x = (width - text_width) // 2
        y = (height - text_height) // 2
    elif position == "top-left":
        x = int(width * 0.1)
        y = int(height * 0.1)
    elif position == "top-right":
        x = int(width * 0.9 - text_width)
        y = int(height * 0.1)
    elif position == "bottom-left":
        x = int(width * 0.1)
        y = int(height * 0.9 - text_height)
    elif position == "bottom-right":
        x = int(width * 0.9 - text_width)
        y = int(height * 0.9 - text_height)
    else:  # Default to center
        x = (width - text_width) // 2
        y = (height - text_height) // 2
    
    # Draw the text with anti-aliasing
    try:
        draw.text((x, y), text, font=font, fill=rgba_color)
    except:
        # Fallback method for older Pillow versions
        draw.text((x, y), text, font=font, fill=rgba_color)
    
    # Rotate if needed using high quality BICUBIC resampling
    if rotation != 0:
        img = img.rotate(rotation, expand=False, resample=Image.BICUBIC, fillcolor=(255, 255, 255, 0))
    
    # Convert to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG', quality=95)
    img_bytes.seek(0)
    
    return img_bytes

def create_watermark_preview(text=None, image_path=None, width=1200, height=800, font_size=30, opacity=0.5, 
                            color=(128, 128, 128), rotation=0, position="center", scale=0.3):
    """
    Creates a preview image of just the watermark text or image.
    Higher resolution (1200x800) for better quality.
    
    Returns:
        Base64 encoded string of the preview image
    """
    # Create a white page as background with higher resolution
    img = Image.new('RGB', (width, height), (255, 255, 255))
    
    # Add watermark
    if text:
        # Create transparent image with text
        overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Try to load a font, fall back to default if not available
        # Scale the font size to match the higher resolution
        scaled_font_size = int(font_size * 2)  # Scale font size for higher resolution
        try:
            font = ImageFont.truetype("arial.ttf", scaled_font_size)
        except IOError:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", scaled_font_size)
            except IOError:
                try:
                    # Try to find a system font that might be available
                    import matplotlib.font_manager as fm
                    system_fonts = fm.findSystemFonts()
                    if system_fonts:
                        font = ImageFont.truetype(system_fonts[0], scaled_font_size)
                    else:
                        font = ImageFont.load_default()
                except:
                    font = ImageFont.load_default()
        
        # Calculate text size
        try:
            # For newer Pillow versions
            text_bbox = draw_overlay.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except AttributeError:
            # Fallback for older Pillow versions
            text_width, text_height = draw_overlay.textsize(text, font=font)
            
        # Set position
        if position == "center":
            x = (width - text_width) // 2
            y = (height - text_height) // 2
        elif position == "top-left":
            x = int(width * 0.1)
            y = int(height * 0.1)
        elif position == "top-right":
            x = int(width * 0.9 - text_width)
            y = int(height * 0.1)
        elif position == "bottom-left":
            x = int(width * 0.1)
            y = int(height * 0.9 - text_height)
        elif position == "bottom-right":
            x = int(width * 0.9 - text_width)
            y = int(height * 0.9 - text_height)
        else:  # Default to center
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
        # Draw text with the specified color and opacity
        rgba_color = color + (int(opacity * 255),)
        draw_overlay.text((x, y), text, font=font, fill=rgba_color)
        
        # Use BICUBIC resampling for rotation instead of LANCZOS
        if rotation != 0:
            overlay = overlay.rotate(rotation, expand=False, resample=Image.BICUBIC, fillcolor=(255, 255, 255, 0))
            
        # Composite the overlay onto the background
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        
        # Add grid lines to show boundaries (light gray)
        draw = ImageDraw.Draw(img)
        grid_color = (240, 240, 240)
        # Vertical centerline
        draw.line([(width//2, 0), (width//2, height)], fill=grid_color, width=1)
        # Horizontal centerline
        draw.line([(0, height//2), (width, height//2)], fill=grid_color, width=1)
        
    elif image_path:
        try:
            # Load the image
            overlay = Image.open(image_path)
            
            # Resize if needed - with BICUBIC resampling instead of LANCZOS
            if scale != 1.0:
                original_width, original_height = overlay.size
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)
                overlay = overlay.resize((new_width, new_height), Image.BICUBIC)
            
            # Rotate if needed - with BICUBIC resampling instead of LANCZOS
            if rotation != 0:
                overlay = overlay.rotate(rotation, expand=True, resample=Image.BICUBIC)
                
            # Apply transparency
            if overlay.mode != 'RGBA':
                overlay = overlay.convert('RGBA')
                
            # Apply opacity
            alpha = Image.new('L', overlay.size, int(255 * opacity))
            overlay.putalpha(alpha)
            
            # Calculate position
            overlay_width, overlay_height = overlay.size
            if position == "center":
                x = (width - overlay_width) // 2
                y = (height - overlay_height) // 2
            elif position == "top-left":
                x = int(width * 0.05)
                y = int(height * 0.05)
            elif position == "top-right":
                x = int(width * 0.95 - overlay_width)
                y = int(height * 0.05)
            elif position == "bottom-left":
                x = int(width * 0.05)
                y = int(height * 0.95 - overlay_height)
            elif position == "bottom-right":
                x = int(width * 0.95 - overlay_width)
                y = int(height * 0.95 - overlay_height)
            else:  # Default to center
                x = (width - overlay_width) // 2
                y = (height - overlay_height) // 2
                
            # Create a full-size transparent image
            full_overlay = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            # Paste the watermark at the calculated position
            full_overlay.paste(overlay, (x, y))
            
            # Composite the overlay onto the background
            img = Image.alpha_composite(img.convert('RGBA'), full_overlay).convert('RGB')
            
            # Add grid lines
            draw = ImageDraw.Draw(img)
            grid_color = (240, 240, 240)
            # Vertical centerline
            draw.line([(width//2, 0), (width//2, height)], fill=grid_color, width=1)
            # Horizontal centerline
            draw.line([(0, height//2), (width, height//2)], fill=grid_color, width=1)
            
        except Exception as e:
            # If there's an error with the image, draw an error message
            draw = ImageDraw.Draw(img)
            draw.text((width//2 - 100, height//2), f"Image Error: {str(e)}", fill=(255, 0, 0))
    
    # Resize to a reasonable display size to reduce file size but maintain quality
    display_width = 800
    display_height = int((display_width / width) * height)
    img = img.resize((display_width, display_height), Image.BICUBIC)  # Use BICUBIC instead of LANCZOS
    
    # Convert to base64 with higher quality
    buffered = io.BytesIO()
    img.save(buffered, format="PNG", quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return img_str

def add_watermark_view():
    if request.method == 'POST':
        # Check if it's a preview request
        if 'preview' in request.form and request.form.get('preview') == '1':
            try:
                watermark_type = request.form.get('watermark_type', 'text')
                opacity = float(request.form.get('opacity', 0.3))
                position = request.form.get('position', 'center')
                rotation = int(request.form.get('rotation', 0))
                
                preview_img = None
                
                if watermark_type == 'text':
                    text = request.form.get('watermark_text', 'Watermark')
                    font_size = int(request.form.get('font_size', 30))
                    color_str = request.form.get('color', '#808080')
                    
                    # Convert color from hex to RGB
                    color = tuple(int(color_str.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    
                    preview_img = create_watermark_preview(
                        text=text, font_size=font_size, opacity=opacity, 
                        color=color, rotation=rotation, position=position
                    )
                else:
                    # For image preview, we can't handle the file upload in AJAX
                    # So we'll return a placeholder or error message
                    preview_img = None
                
                return {'status': 'success', 'preview': preview_img}
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # Normal file processing for actual watermark creation
        if 'file' not in request.files:
            return render_template('pages/edit/add_watermark.html', 
                                  error="No file selected")
        
        file = request.files['file']
        
        # Check if the file is empty
        if file.filename == '':
            return render_template('pages/edit/add_watermark.html', 
                                  error="No file selected")
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            return render_template('pages/edit/add_watermark.html', 
                                  error="Please upload a PDF file")
        
        # Secure the filename and save the file temporarily
        filename = secure_filename(file.filename)
        temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(temp_fd)
        file.save(temp_path)
        
        # Get watermark options
        watermark_type = request.form.get('watermark_type', 'text')
        page_range_str = request.form.get('page_range', '')
        opacity = float(request.form.get('opacity', 0.3))
        position = request.form.get('position', 'center')
        rotation = int(request.form.get('rotation', 0))
        
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
                return render_template('pages/edit/add_watermark.html', 
                                      error="Invalid page range format")
        
        try:
            output_path = None
            
            # Process based on watermark type
            if watermark_type == 'text':
                text = request.form.get('watermark_text', 'Watermark')
                font_size = int(request.form.get('font_size', 30))
                color_str = request.form.get('color', '#808080')  # Default gray
                
                # Convert color from hex to RGB
                color = tuple(int(color_str.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                
                # Add text watermark
                output_path = add_text_watermark(
                    temp_path, text, font_size, opacity, position, color, rotation, page_range
                )
            else:  # image watermark
                # Check if image was uploaded
                if 'watermark_image' not in request.files:
                    os.unlink(temp_path)
                    return render_template('pages/edit/add_watermark.html', 
                                          error="No watermark image selected")
                
                image_file = request.files['watermark_image']
                if image_file.filename == '':
                    os.unlink(temp_path)
                    return render_template('pages/edit/add_watermark.html', 
                                          error="No watermark image selected")
                
                # Save the image temporarily
                image_fd, image_path = tempfile.mkstemp()
                os.close(image_fd)
                image_file.save(image_path)
                
                scale = float(request.form.get('scale', 0.3))
                
                # Add image watermark
                output_path = add_image_watermark(
                    temp_path, image_path, scale, opacity, position, rotation, page_range
                )
                
                # Clean up the temp image
                try:
                    os.unlink(image_path)
                except:
                    pass
            
            # Clean up the temp input file
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Return the generated file
            response = send_file(
                output_path,
                as_attachment=True,
                download_name=f"watermarked_{filename}",
                mimetype='application/pdf'
            )
            
            # Add cache control headers to prevent caching
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            
            return response
            
        except Exception as e:
            # Clean up temp files
            if temp_path:
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
            if 'output_path' in locals() and output_path:
                try:
                    os.unlink(output_path)
                except:
                    pass
                
            if 'image_path' in locals():
                try:
                    os.unlink(image_path)
                except:
                    pass
                
            return render_template('pages/edit/add_watermark.html', 
                                  error=f"Error adding watermark: {str(e)}")
            
    return render_template('pages/edit/add_watermark.html')
