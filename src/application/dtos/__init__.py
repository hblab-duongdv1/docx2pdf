from dataclasses import dataclass
from typing import List, Optional
from src.domain.entities.document import Document, FontInfo, DocumentStatus

# Request DTO for document conversion
@dataclass
class ConvertDocumentRequest:
    """Request DTO for document conversion"""
    docx_url: Optional[str] = None
    docx_path: Optional[str] = None
    font_urls: List[dict] = None
    output_filename: Optional[str] = None
    
    def __post_init__(self):
        if self.font_urls is None:
            self.font_urls = []
    
    def to_font_infos(self) -> List[FontInfo]:
        """Convert font URLs to FontInfo objects"""
        return [FontInfo(url=font['url'], name=font['name']) for font in self.font_urls]


# Response DTO for document conversion
@dataclass
class ConvertDocumentResponse:
    """Response DTO for document conversion"""
    success: bool
    document_id: Optional[str] = None
    output_path: Optional[str] = None
    error_message: Optional[str] = None