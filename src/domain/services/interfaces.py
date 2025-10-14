from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.document import Document, FontInfo


class DocumentRepository(ABC):
    """Abstract repository for document persistence"""
    
    @abstractmethod
    def save(self, document: Document) -> Document:
        """Save document to storage"""
        pass
    
    @abstractmethod
    def find_by_id(self, document_id: str) -> Optional[Document]:
        """Find document by ID"""
        pass
    
    @abstractmethod
    def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        pass


class FontService(ABC):
    """Abstract service for font operations"""
    
    @abstractmethod
    def download_font(self, font_info: FontInfo) -> str:
        """Download font and return local path"""
        pass
    
    @abstractmethod
    def install_font(self, font_path: str) -> bool:
        """Install font to system"""
        pass
    
    @abstractmethod
    def is_font_available(self, font_info: FontInfo) -> bool:
        """Check if font is available"""
        pass


class ConversionService(ABC):
    """Abstract service for document conversion"""
    
    @abstractmethod
    def convert_document(self, document: Document) -> bool:
        """Convert document from DOCX to PDF"""
        pass
    
    @abstractmethod
    def validate_document(self, document: Document) -> bool:
        """Validate document before conversion"""
        pass
