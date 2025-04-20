"""
PDF Protection Module

This module provides functionality for adding password protection to PDF files.
It uses PyMuPDF (fitz) to encrypt PDFs with user and/or owner passwords.
"""

import os
import logging
import fitz  # PyMuPDF
from app.errors import PDFProcessingError
from PyPDF2 import PdfReader, PdfWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Permission constants
PERM_PRINT = 1 << 2
PERM_MODIFY = 1 << 3
PERM_COPY = 1 << 4
PERM_ANNOTATE = 1 << 5
PERM_FORM = 1 << 8
PERM_ACCESSIBILITY = 1 << 9
PERM_ASSEMBLE = 1 << 10
PERM_PRINT_HQ = 1 << 11


def protect_pdf(input_path, output_path, user_password='', owner_password='',
                allow_print=True, allow_modify=False, allow_copy=True,
                allow_annotate=True, allow_forms=True, allow_accessibility=True,
                allow_assemble=False, allow_print_hq=True):
    """
    Add password protection to a PDF file.

    Args:
        input_path (str): Path to the input PDF file.
        output_path (str): Path where the protected PDF will be saved.
        user_password (str, optional): Password required to open the document. Defaults to ''.
        owner_password (str, optional): Password required for full access. Defaults to ''.
        allow_print (bool, optional): Allow printing. Defaults to True.
        allow_modify (bool, optional): Allow content modification. Defaults to False.
        allow_copy (bool, optional): Allow content copying. Defaults to True.
        allow_annotate (bool, optional): Allow annotations. Defaults to True.
        allow_forms (bool, optional): Allow form filling. Defaults to True.
        allow_accessibility (bool, optional): Allow accessibility extraction. Defaults to True.
        allow_assemble (bool, optional): Allow document assembly. Defaults to False.
        allow_print_hq (bool, optional): Allow high-quality printing. Defaults to True.

    Returns:
        dict: A dictionary containing information about the operation:
            - 'input_page_count': Number of pages in the input PDF.
            - 'has_user_password': Whether a user password was set.
            - 'has_owner_password': Whether an owner password was set.
            - 'permissions': Dictionary of permissions set.

    Raises:
        PDFProcessingError: If the operation fails.
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            raise PDFProcessingError(f"Input file not found: {input_path}")

        # Validate passwords
        if not user_password and not owner_password:
            raise PDFProcessingError("At least one password (user or owner) must be provided")

        # If only user password is provided, use it for owner password too
        if user_password and not owner_password:
            owner_password = user_password

        # Open the input PDF
        doc = fitz.open(input_path)

        # Get the input page count
        input_page_count = doc.page_count

        # Calculate permissions
        permissions = 0
        if allow_print:
            permissions |= PERM_PRINT
        if allow_modify:
            permissions |= PERM_MODIFY
        if allow_copy:
            permissions |= PERM_COPY
        if allow_annotate:
            permissions |= PERM_ANNOTATE
        if allow_forms:
            permissions |= PERM_FORM
        if allow_accessibility:
            permissions |= PERM_ACCESSIBILITY
        if allow_assemble:
            permissions |= PERM_ASSEMBLE
        if allow_print_hq:
            permissions |= PERM_PRINT_HQ

        # Encrypt the document
        # PyMuPDF uses AES-256 encryption by default
        doc.save(
            output_path,
            encryption=fitz.PDF_ENCRYPT_AES_256,
            user_pw=user_password,
            owner_pw=owner_password,
            permissions=permissions
        )

        # Close the document
        doc.close()

        # Return information about the operation
        return {
            'input_page_count': input_page_count,
            'has_user_password': bool(user_password),
            'has_owner_password': bool(owner_password),
            'permissions': {
                'print': allow_print,
                'modify': allow_modify,
                'copy': allow_copy,
                'annotate': allow_annotate,
                'forms': allow_forms,
                'accessibility': allow_accessibility,
                'assemble': allow_assemble,
                'print_hq': allow_print_hq
            }
        }

    except PDFProcessingError:
        # Re-raise PDFProcessingError
        raise

    except Exception as e:
        logger.error(f"Error protecting PDF: {str(e)}")
        raise PDFProcessingError(f"Failed to protect PDF: {str(e)}")


def check_pdf_encryption(pdf_path):
    """
    Check if a PDF file is encrypted and get its encryption information.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        dict: A dictionary containing information about the PDF encryption:
            - 'is_encrypted': Whether the PDF is encrypted.
            - 'encryption_method': The encryption method used (if encrypted).
            - 'has_user_password': Whether a user password is required.
            - 'has_owner_password': Whether an owner password is required.
            - 'permissions': Dictionary of permissions (if encrypted).

    Raises:
        PDFProcessingError: If the operation fails.
    """
    try:
        # Validate input file
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"File not found: {pdf_path}")

        # Open the PDF
        doc = fitz.open(pdf_path)

        # Check if the PDF is encrypted
        is_encrypted = doc.is_encrypted

        # Get encryption information
        result = {
            'is_encrypted': is_encrypted,
            'encryption_method': None,
            'has_user_password': False,
            'has_owner_password': False,
            'permissions': {}
        }

        if is_encrypted:
            # Get encryption method
            if doc.encryption_method == 1:
                result['encryption_method'] = 'RC4 (40-bit)'
            elif doc.encryption_method == 2:
                result['encryption_method'] = 'RC4 (128-bit)'
            elif doc.encryption_method == 3:
                result['encryption_method'] = 'AES (128-bit)'
            elif doc.encryption_method == 4:
                result['encryption_method'] = 'AES (256-bit)'
            else:
                result['encryption_method'] = f'Unknown ({doc.encryption_method})'

            # Check if passwords are required
            result['has_user_password'] = doc.needs_pass
            result['has_owner_password'] = doc.needs_pass

            # Get permissions
            permissions = doc.permissions
            result['permissions'] = {
                'print': bool(permissions & PERM_PRINT),
                'modify': bool(permissions & PERM_MODIFY),
                'copy': bool(permissions & PERM_COPY),
                'annotate': bool(permissions & PERM_ANNOTATE),
                'forms': bool(permissions & PERM_FORM),
                'accessibility': bool(permissions & PERM_ACCESSIBILITY),
                'assemble': bool(permissions & PERM_ASSEMBLE),
                'print_hq': bool(permissions & PERM_PRINT_HQ)
            }

        # Close the document
        doc.close()

        return result

    except PDFProcessingError:
        # Re-raise PDFProcessingError
        raise

    except Exception as e:
        logger.error(f"Error checking PDF encryption: {str(e)}")
        raise PDFProcessingError(f"Failed to check PDF encryption: {str(e)}")


def protect_pdf(input_stream, output_stream, user_password, owner_password):
    """
    Protect a PDF with passwords using PyPDF2.
    
    Args:
        input_stream (BytesIO): Input PDF file stream
        output_stream (BytesIO): Output PDF file stream
        user_password (str): Password for opening the PDF
        owner_password (str): Password for editing the PDF
    """
    # Create PDF reader and writer objects
    reader = PdfReader(input_stream)
    writer = PdfWriter()

    # Copy pages from reader to writer
    for page in reader.pages:
        writer.add_page(page)

    # Encrypt the PDF with the passwords
    writer.encrypt(
        user_password=user_password,
        owner_password=owner_password,
        use_128bit=True
    )

    # Write the protected PDF to the output stream
    writer.write(output_stream)
