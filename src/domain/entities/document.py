from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class DocumentStatus(Enum):
    """Document processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentFormat(Enum):
    """Supported document formats"""
    DOCX = "docx"
    PDF = "pdf"


@dataclass
class FontInfo:
    """Font information value object"""
    url: str
    name: str
    
    def __post_init__(self):
        if not self.url or not self.name:
            raise ValueError("Font URL and name are required")
        
        if not self.url.startswith(('http://', 'https://')):
            raise ValueError("Font URL must be a valid HTTP/HTTPS URL")


@dataclass
class Document:
    """Document entity"""
    id: str
    source_url: Optional[str] = None
    source_path: Optional[str] = None
    output_path: Optional[str] = None
    filename: Optional[str] = None
    status: DocumentStatus = DocumentStatus.PENDING
    error_message: Optional[str] = None
    fonts: List[FontInfo] = None
    
    def __post_init__(self):
        if self.fonts is None:
            self.fonts = []
        
        if not self.source_url and not self.source_path:
            raise ValueError("Either source_url or source_path must be provided")
    
    def mark_as_processing(self):
        """Mark document as processing"""
        self.status = DocumentStatus.PROCESSING
    
    def mark_as_completed(self, output_path: str):
        """Mark document as completed with output path"""
        self.status = DocumentStatus.COMPLETED
        self.output_path = output_path
    
    def mark_as_failed(self, error_message: str):
        """Mark document as failed with error message"""
        self.status = DocumentStatus.FAILED
        self.error_message = error_message
    
    def is_ready_for_conversion(self) -> bool:
        """Check if document is ready for conversion"""
        return self.status == DocumentStatus.PENDING and (self.source_url or self.source_path)
    
    def add_font(self, font: FontInfo):
        """Add font to document"""
        self.fonts.append(font)
