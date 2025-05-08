"""
PDF Flatten Module

This module provides functionality for flattening form fields and annotations in PDF files.
It uses PyMuPDF (fitz) to convert interactive elements to static content.
"""

import os
import logging
import fitz  # PyMuPDF
from app.errors import PDFProcessingError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def flatten_pdf(input_path, output_path, flatten_annotations=True, flatten_form_fields=True):
    """
    Flatten form fields and annotations in a PDF file.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path where the flattened PDF will be saved.
        flatten_annotations (bool, optional): Whether to flatten annotations. Defaults to True.
        flatten_form_fields (bool, optional): Whether to flatten form fields. Defaults to True.

    Returns:
        dict: A dictionary containing information about the operation:
            - 'input_page_count': Number of pages in the input PDF.
            - 'form_fields_count': Number of form fields flattened.
            - 'annotations_count': Number of annotations flattened.

    Raises:
        PDFProcessingError: If the operation fails.
    """
    doc = None
    try:
        # Validate input file
        if not os.path.exists(input_path):
            raise PDFProcessingError(f"Input file not found: {input_path}")

        # Open the input PDF
        doc = fitz.open(input_path)

        # Get the input page count
        input_page_count = doc.page_count

        # Count form fields and annotations
        form_fields_count = 0
        annotations_count = 0

        # Process each page
        for page_num in range(input_page_count):
            page = doc[page_num]

            # Count and flatten form fields
            if flatten_form_fields and doc.is_form_pdf:
                widgets = list(page.widgets())  # Convert generator to list
                form_fields_count += len(widgets)

                for widget in widgets:
                    # Update the widget to ensure its appearance is current
                    widget.update()

                    # Add the widget appearance to the page
                    if widget.has_js:
                        # Handle JavaScript-enabled widgets
                        field_rect = widget.rect
                        field_type = widget.field_type
                        field_value = widget.field_value

                        # Add text for text fields
                        if field_type == fitz.PDF_WIDGET_TYPE_TEXT and field_value:
                            page.insert_text(
                                point=(field_rect.x0 + 2, field_rect.y0 + field_rect.height / 2),
                                text=str(field_value),
                                fontsize=10
                            )
                    else:
                        # For widgets without JavaScript, use the appearance stream
                        page.show_pdf_page(
                            rect=widget.rect,
                            src=doc,
                            pno=page_num,
                            keep_proportion=True,
                            overlay=True
                        )

                    # Remove the widget
                    page.delete_widget(widget)

            # Count and flatten annotations
            if flatten_annotations:
                annots = list(page.annots())  # Convert generator to list
                annotations_count += len(annots)

                for annot in annots:
                    # Get annotation type and appearance
                    annot_type = annot.type[0]
                    annot_rect = annot.rect

                    # For text annotations, add the text content to the page
                    if annot_type == fitz.PDF_ANNOT_TEXT and annot.info.get("content"):
                        page.insert_text(
                            point=(annot_rect.x0, annot_rect.y0),
                            text=annot.info["content"],
                            fontsize=10
                        )

                    # For highlight annotations, add a yellow rectangle
                    elif annot_type == fitz.PDF_ANNOT_HIGHLIGHT:
                        page.draw_rect(annot_rect, color=(1, 1, 0), fill=(1, 1, 0, 0.3))

                    # For other annotations, try to render them as they appear
                    else:
                        # Use the annotation appearance if available
                        page.show_pdf_page(
                            rect=annot_rect,
                            src=doc,
                            pno=page_num,
                            keep_proportion=True,
                            overlay=True
                        )

                    # Remove the annotation
                    page.delete_annot(annot)

        # Save the document
        doc.save(output_path)

        # Close the document
        doc.close()

        return {
            'input_page_count': input_page_count,
            'form_fields_count': form_fields_count,
            'annotations_count': annotations_count
        }

    except Exception as e:
        if doc:
            doc.close()
        raise PDFProcessingError(f"Failed to flatten PDF: {str(e)}")


def has_form_fields_or_annotations(pdf_path):
    """
    Check if a PDF file has form fields or annotations.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        dict: A dictionary containing information about the PDF:
            - 'has_form_fields': Whether the PDF has form fields.
            - 'has_annotations': Whether the PDF has annotations.
            - 'form_fields_count': Number of form fields.
            - 'annotations_count': Number of annotations.

    Raises:
        PDFProcessingError: If the operation fails.
    """
    try:
        # Validate input file
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"File not found: {pdf_path}")

        # Open the PDF
        doc = fitz.open(pdf_path)

        # Check if the PDF has form fields
        has_form_fields = doc.is_form_pdf

        # Count form fields and annotations
        form_fields_count = 0
        annotations_count = 0

        # Process each page
        for page_num in range(doc.page_count):
            page = doc[page_num]

            # Count form fields
            if has_form_fields:
                widgets = page.widgets()
                form_fields_count += len(widgets)

            # Count annotations
            annots = page.annots()
            annotations_count += len(annots)

        # Close the document
        doc.close()

        return {
            'has_form_fields': has_form_fields,
            'has_annotations': annotations_count > 0,
            'form_fields_count': form_fields_count,
            'annotations_count': annotations_count
        }

    except PDFProcessingError:
        # Re-raise PDFProcessingError
        raise

    except Exception as e:
        logger.error(f"Error checking PDF for form fields and annotations: {str(e)}")
        raise PDFProcessingError(f"Failed to check PDF for form fields and annotations: {str(e)}")