import os
import tempfile
import uuid
from pathlib import Path
import logging
import traceback
from typing import Dict, Any

# Controller for document operations
from src.application.services import DocumentApplicationService
from src.application.dtos import (
    ConvertDocumentRequest, 
    ConvertDocumentResponse
)

logger = logging.getLogger(__name__)


class DocumentController:
    """Controller for document operations"""
    
    def __init__(self, app_service: DocumentApplicationService):
        self.app_service = app_service
    
    def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "docx2pdf-converter",
            "version": "1.0.0"
        }
    
    def convert_docx_to_pdf(self, data: Dict[str, Any]) -> str | tuple[Dict[str, Any], int]:
        """
        Convert DOCX to PDF endpoint
        
        Expected data dict:
        {
            "docx_url": "https://example.com/document.docx",
            "font_urls": [
                {
                    "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
                    "name": "Roboto-Regular"
                }
            ],
            "output_filename": "output.pdf"  # optional
        }
        """
        try:
            # Validate required fields
            if 'docx_url' not in data:
                return {
                    "error": "Missing required field: docx_url"
                }, 400
            
            # Create request DTO
            convert_request = ConvertDocumentRequest(
                docx_url=data['docx_url'],
                font_urls=data.get('font_urls', []),
                output_filename=data.get('output_filename', f"converted_{uuid.uuid4().hex[:8]}.pdf")
            )
            
            # Execute conversion
            response = self.app_service.convert_document(convert_request)
            
            if response.success:
                # Return PDF file path for FastAPI FileResponse
                return response.output_path
            else:
                return {
                    "error": response.error_message or "Conversion failed"
                }, 500
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error": f"Internal server error: {str(e)}"
            }, 500
    
    def convert_uploaded_file(self, data: Dict[str, Any]) -> str | tuple[Dict[str, Any], int]:
        """
        Convert uploaded DOCX file to PDF
        
        Expected data dict:
        {
            "docx_path": "/path/to/temp/file.docx",
            "font_urls": [...],
            "output_filename": "output.pdf"
        }
        """
        try:
            # Validate required fields
            if 'docx_path' not in data:
                return {
                    "error": "Missing required field: docx_path"
                }, 400
            
            # Create request DTO
            convert_request = ConvertDocumentRequest(
                docx_path=data['docx_path'],
                font_urls=data.get('font_urls', []),
                output_filename=data.get('output_filename', f"converted_{uuid.uuid4().hex[:8]}.pdf")
            )
            
            # Execute conversion
            response = self.app_service.convert_document(convert_request)
            
            if response.success:
                # Return PDF file path for FastAPI FileResponse
                return response.output_path
            else:
                return {
                    "error": response.error_message or "Conversion failed"
                }, 500
                
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "error": f"Internal server error: {str(e)}"
            }, 500