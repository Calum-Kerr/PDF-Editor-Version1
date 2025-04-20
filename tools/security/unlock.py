"""
PDF Unlock Module

This module provides functionality for removing password protection from PDF files.
It uses PyMuPDF (fitz) to decrypt PDFs with the provided password.
"""

import logging
import fitz
from app.errors import PDFProcessingError
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def unlock_pdf(input_stream, password):
    """
    Remove password protection from a PDF file.
    
    Args:
        input_stream (BytesIO): Input PDF file stream
        password (str): Password to unlock the PDF
        
    Returns:
        BytesIO: Unprotected PDF file stream
        
    Raises:
        PDFProcessingError: If the operation fails
    """
    try:
        # Create output stream
        output_stream = BytesIO()
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(stream=input_stream.read(), filetype="pdf")
        
        # Check if PDF is encrypted
        if not doc.is_encrypted:
            raise PDFProcessingError("This PDF is not password protected")
            
        # Try to authenticate with the password
        if not doc.authenticate(password):
            raise PDFProcessingError("Incorrect password")
            
        # Save the unencrypted PDF to the output stream
        doc.save(output_stream, encryption=fitz.PDF_ENCRYPT_NONE)
        
        # Close the document
        doc.close()
        
        # Reset stream position
        output_stream.seek(0)
        
        return output_stream
        
    except PDFProcessingError:
        raise
        
    except Exception as e:
        logger.error(f"Error unlocking PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to unlock PDF: {str(e)}")
