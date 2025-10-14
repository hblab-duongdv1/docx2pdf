from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.document import Document, FontInfo
from src.application.dtos import (
    ConvertDocumentRequest, 
    ConvertDocumentResponse
)


# Abstract use case for document conversion
class ConvertDocumentUseCase(ABC):
    """Abstract use case for document conversion"""
    
    @abstractmethod
    def execute(self, request: ConvertDocumentRequest) -> ConvertDocumentResponse:
        """Execute document conversion"""
        pass 

# Application service for document operations
class DocumentApplicationService:
    """Application service for document operations"""
    
    def __init__(self, convert_use_case: ConvertDocumentUseCase):
        self.convert_use_case = convert_use_case
    
    def convert_document(self, request: ConvertDocumentRequest) -> ConvertDocumentResponse:
        """Convert document using the use case"""
        return self.convert_use_case.execute(request)