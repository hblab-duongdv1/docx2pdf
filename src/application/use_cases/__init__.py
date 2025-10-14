import uuid
import logging
from typing import List
from src.domain.entities.document import Document, FontInfo, DocumentStatus
from src.domain.services.interfaces import DocumentRepository, FontService, ConversionService
from src.application.dtos import (
    ConvertDocumentRequest, 
    ConvertDocumentResponse
)
from src.application.services import ConvertDocumentUseCase

logger = logging.getLogger(__name__)

# Implementation of document conversion use case
# Includes document creation, validation, and conversion
# Provides a high-quality conversion
class ConvertDocumentUseCaseImpl(ConvertDocumentUseCase):
    """Implementation of document conversion use case"""
    
    def __init__(self, 
                 document_repository: DocumentRepository,
                 font_service: FontService,
                 conversion_service: ConversionService):
        self.document_repository = document_repository
        self.font_service = font_service
        self.conversion_service = conversion_service
    
    def execute(self, request: ConvertDocumentRequest) -> ConvertDocumentResponse:
        """Execute document conversion"""
        try:
            # Create document entity
            document_id = str(uuid.uuid4())
            fonts = request.to_font_infos()
            
            document = Document(
                id=document_id,
                source_url=request.docx_url,
                source_path=request.docx_path,
                filename=request.output_filename,
                fonts=fonts
            )
            
            # Save document
            document = self.document_repository.save(document)
            
            # Mark as processing
            document.mark_as_processing()
            self.document_repository.save(document)
            
            # Validate document
            if not self.conversion_service.validate_document(document):
                document.mark_as_failed("Document validation failed")
                self.document_repository.save(document)
                return ConvertDocumentResponse(
                    success=False,
                    document_id=document_id,
                    error_message="Document validation failed"
                )
            
            # Convert document
            success = self.conversion_service.convert_document(document)
            
            if success:
                document.mark_as_completed(document.output_path)
                self.document_repository.save(document)
                return ConvertDocumentResponse(
                    success=True,
                    document_id=document_id,
                    output_path=document.output_path
                )
            else:
                document.mark_as_failed("Conversion failed")
                self.document_repository.save(document)
                return ConvertDocumentResponse(
                    success=False,
                    document_id=document_id,
                    error_message="Conversion failed"
                )
                
        except Exception as e:
            logger.error(f"Error in convert document use case: {str(e)}")
            return ConvertDocumentResponse(
                success=False,
                error_message=f"Internal error: {str(e)}"
            )