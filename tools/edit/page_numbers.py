"""
Page Numbers Module

This module provides functionality for adding page numbers to PDF files.
It uses PyMuPDF (fitz) to add page numbers in various styles and positions.
"""

import os
import logging
import fitz  # PyMuPDF
from app.errors import PDFProcessingError
from tools.organise.split import parse_page_ranges  # Fixed import path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def add_page_numbers(input_path, output_path, start_number=1, position='bottom-center',
                     font_name='helv', font_size=10, color=(0, 0, 0),
                     margin=36, prefix='', suffix='', pages='all'):
    """
    Add page numbers to a PDF file.
    """
    doc = None
    try:
        # Validate input file
        if not os.path.exists(input_path):
            raise PDFProcessingError(f"Input file not found: {input_path}")

        # Validate position
        valid_positions = ['top-left', 'top-center', 'top-right',
                           'bottom-left', 'bottom-center', 'bottom-right']
        if position not in valid_positions:
            raise PDFProcessingError(f"Invalid position: {position}. Valid positions: {', '.join(valid_positions)}")

        # Validate font
        valid_fonts = ['helv', 'tiro', 'cour', 'times']
        if font_name not in valid_fonts:
            raise PDFProcessingError(f"Invalid font: {font_name}. Valid fonts: {', '.join(valid_fonts)}")

        # Validate font size
        try:
            font_size = int(font_size)
            if font_size < 6 or font_size > 72:
                raise PDFProcessingError(f"Invalid font size: {font_size}. Valid range: 6-72")
        except ValueError:
            raise PDFProcessingError(f"Invalid font size: {font_size}. Must be an integer.")

        # Validate start number
        try:
            start_number = int(start_number)
            if start_number < 1:
                raise PDFProcessingError(f"Invalid start number: {start_number}. Must be at least 1.")
        except ValueError:
            raise PDFProcessingError(f"Invalid start number: {start_number}. Must be an integer.")

        # Normalize color to 0-1 range for PyMuPDF
        color = (color[0] / 255, color[1] / 255, color[2] / 255)

        # Open the input PDF
        doc = fitz.open(input_path)

        # Get the input page count
        input_page_count = doc.page_count

        # Determine which pages to number
        pages_to_number = []
        if not pages or pages.lower().strip() == 'all':  # Changed this line to handle empty string
            # Number all pages
            pages_to_number = list(range(1, input_page_count + 1))
        else:
            # Parse the page ranges
            page_ranges = parse_page_ranges(pages, input_page_count)

            # Create a list of all pages to number
            for start, end in page_ranges:
                pages_to_number.extend(range(start, end + 1))

            # Remove duplicates and sort
            pages_to_number = sorted(set(pages_to_number))

        # Add page numbers to the specified pages
        current_number = start_number
        for page_num in pages_to_number:
            # Page numbers are 1-based in the input, but 0-based in PyMuPDF
            page = doc[page_num - 1]

            # Get page dimensions
            rect = page.rect
            
            # Create the page number text
            text = f"{prefix}{current_number}{suffix}"
            
            # Get text width for alignment calculations
            tw = fitz.get_text_length(text, fontname=font_name, fontsize=font_size)
            
            # Get base position
            x, y = get_position_coordinates(position, rect, margin)
            
            # Adjust x position based on alignment
            if 'center' in position:
                x -= tw / 2
            elif 'right' in position:
                x -= tw

            # Add the page number
            page.insert_text(
                point=(x, y),
                text=text,
                fontname=font_name,
                fontsize=font_size,
                color=color,
                render_mode=0  # 0 = fill, 1 = stroke, 2 = fill+stroke
            )

            # Increment the page number
            current_number += 1

        # Save the document
        doc.save(output_path)

        # Store the result before closing
        result = {
            'input_page_count': input_page_count,
            'numbered_pages': pages_to_number,
            'start_number': start_number,
            'position': position,
            'font': font_name,
            'font_size': font_size
        }

        # Close the document
        doc.close()

        return result

    except PDFProcessingError:
        if doc:
            doc.close()
        raise

    except Exception as e:
        if doc:
            doc.close()
        logger.error(f"Error adding page numbers: {str(e)}")
        raise PDFProcessingError(f"Failed to add page numbers: {str(e)}")


def get_position_coordinates(position, rect, margin):
    """
    Get the coordinates for a given position on the page.

    Args:
        position (str): Position name ('top-left', 'bottom-center', etc.).
        rect (fitz.Rect): Page rectangle.
        margin (int): Margin in points from the edge.

    Returns:
        tuple: (x, y) coordinates for the position.
    """
    width = rect.width
    height = rect.height

    if position == 'top-left':
        return margin, margin
    elif position == 'top-center':
        return width / 2, margin
    elif position == 'top-right':
        return width - margin, margin
    elif position == 'bottom-left':
        return margin, height - margin
    elif position == 'bottom-center':
        return width / 2, height - margin
    elif position == 'bottom-right':
        return width - margin, height - margin
    else:
        # Default to bottom-center
        return width / 2, height - margin


def get_alignment(position):
    """
    Get the text alignment for a given position.

    Args:
        position (str): Position name ('top-left', 'bottom-center', etc.).

    Returns:
        int: Alignment value (0 = left, 1 = center, 2 = right).
    """
    if 'left' in position:
        return 0  # Left-aligned
    elif 'center' in position:
        return 1  # Center-aligned
    elif 'right' in position:
        return 2  # Right-aligned
    else:
        # Default to center
        return 1


def get_font_name(font_code):
    """
    Get the human-readable font name for a font code.

    Args:
        font_code (str): Font code ('helv', 'tiro', etc.).

    Returns:
        str: Human-readable font name.
    """
    font_names = {
        'helv': 'Helvetica',
        'tiro': 'Times Roman',
        'cour': 'Courier',
        'times': 'Times New Roman'
    }

    return font_names.get(font_code, font_code)


def get_position_name(position_code):
    """
    Get the human-readable position name for a position code.

    Args:
        position_code (str): Position code ('top-left', 'bottom-center', etc.).

    Returns:
        str: Human-readable position name.
    """
    position_names = {
        'top-left': 'Top Left',
        'top-center': 'Top Center',
        'top-right': 'Top Right',
        'bottom-left': 'Bottom Left',
        'bottom-center': 'Bottom Center',
        'bottom-right': 'Bottom Right'
    }

    return position_names.get(position_code, position_code)