"""
RevisePDF Error Handlers Module

This module defines error handlers for the RevisePDF application.
It includes handlers for common HTTP errors and custom application errors.
"""

import os
import logging
from flask import render_template, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PDFProcessingError(Exception):
    """Base exception for PDF processing errors."""

    def __init__(self, message, status_code=500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


def register_error_handlers(app):
    """
    Register error handlers for the Flask application.

    Args:
        app (Flask): The Flask application instance.
    """

    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors."""
        logger.error(f"400 Bad Request: {request.url} - {error}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error=str(error)), 400
        return render_template('errors/400.html', error=error), 400

    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors."""
        logger.error(f"404 Not Found: {request.url}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Resource not found"), 404
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle 413 Request Entity Too Large errors."""
        logger.error(f"413 Request Entity Too Large: {request.url}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="File too large"), 413
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handle 500 Internal Server Error errors."""
        logger.error(f"500 Internal Server Error: {request.url} - {error}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error="Internal server error"), 500
        return render_template('errors/500.html'), 500

    @app.errorhandler(PDFProcessingError)
    def handle_pdf_processing_error(error):
        """Handle custom PDF processing errors."""
        logger.error(f"PDF Processing Error: {error.message}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(error=error.message), error.status_code
        return render_template('errors/generic.html', error=error), error.status_code