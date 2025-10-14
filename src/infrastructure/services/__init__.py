import os
import tempfile
import requests
import subprocess
import platform
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

from src.domain.entities.document import Document, FontInfo
from src.domain.services.interfaces import DocumentRepository, FontService, ConversionService

logger = logging.getLogger(__name__)

# Document repository implementation
# In-memory implementation of document repository
# TODO: Use a more efficient document repository
class InMemoryDocumentRepository(DocumentRepository):
    """In-memory implementation of document repository"""
    
    def __init__(self):
        self._documents: Dict[str, Document] = {}
    
    def save(self, document: Document) -> Document:
        """Save document to memory"""
        self._documents[document.id] = document
        return document
    
    def find_by_id(self, document_id: str) -> Optional[Document]:
        """Find document by ID"""
        return self._documents.get(document_id)
    
    def delete(self, document_id: str) -> bool:
        """Delete document by ID"""
        if document_id in self._documents:
            del self._documents[document_id]
            return True
        return False


# Font service implementation
# Downloads and installs fonts locally
# TODO: Use a more efficient font service
class FontServiceImpl(FontService):
    """Implementation of font service"""
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.font_cache = {}
    
    def download_font(self, font_info: FontInfo) -> str:
        """Download font from URL and cache it locally"""
        try:
            # Create fonts directory if it doesn't exist
            fonts_dir = Path(self.temp_dir) / "fonts"
            fonts_dir.mkdir(exist_ok=True)
            
            font_path = fonts_dir / f"{font_info.name}.ttf"
            
            # Skip download if already cached
            if font_path.exists():
                logger.info(f"Font {font_info.name} already cached")
                return str(font_path)
            
            # Download font
            logger.info(f"Downloading font from {font_info.url}")
            response = requests.get(font_info.url, timeout=30)
            response.raise_for_status()
            
            # Save font
            with open(font_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Font {font_info.name} downloaded successfully")
            return str(font_path)
            
        except Exception as e:
            logger.error(f"Failed to download font {font_info.name}: {str(e)}")
            raise
    
    def install_font(self, font_path: str) -> bool:
        """Install font to system"""
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                user_fonts = Path.home() / "Library" / "Fonts"
                user_fonts.mkdir(exist_ok=True)
                
                font_name = Path(font_path).name
                dest_path = user_fonts / font_name
                
                if not dest_path.exists():
                    shutil.copy2(font_path, dest_path)
                    logger.info(f"Font installed to {dest_path}")
                
            elif system == "Windows":
                logger.warning("Windows font installation not implemented")
                
            elif system == "Linux":
                user_fonts = Path.home() / ".fonts"
                user_fonts.mkdir(exist_ok=True)
                
                font_name = Path(font_path).name
                dest_path = user_fonts / font_name
                
                if not dest_path.exists():
                    shutil.copy2(font_path, dest_path)
                    logger.info(f"Font installed to {dest_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install font: {str(e)}")
            return False
    
    def is_font_available(self, font_info: FontInfo) -> bool:
        """Check if font is available"""
        try:
            response = requests.head(font_info.url, timeout=10)
            return response.status_code == 200
        except:
            return False


# Conversion service implementation
# Uses LibreOffice for conversion
# Includes font installation, document validation, and LibreOffice command execution, provides a high-quality conversion.
class ConversionServiceImpl(ConversionService):
    """Implementation of conversion service"""
    
    def __init__(self, font_service: FontService, temp_dir: Optional[str] = None):
        self.font_service = font_service
        self.temp_dir = temp_dir or tempfile.gettempdir()
    
    def convert_document(self, document: Document) -> bool:
        """Convert document from DOCX to PDF"""
        try:
            # Download and install fonts if provided
            if document.fonts:
                for font_info in document.fonts:
                    font_path = self.font_service.download_font(font_info)
                    self.font_service.install_font(font_path)
            
            # Use LibreOffice for high-quality conversion
            return self._convert_with_libreoffice(document)
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            return False
    
    def validate_document(self, document: Document) -> bool:
        """Validate document before conversion"""
        try:
            if document.source_url:
                # Validate URL format
                if not document.source_url.startswith(('http://', 'https://')):
                    return False
                
                # Check if URL is accessible
                response = requests.head(document.source_url, timeout=10)
                return response.status_code == 200
            
            elif document.source_path:
                # Check if file exists
                return os.path.exists(document.source_path)
            
            return False
            
        except Exception as e:
            logger.error(f"Document validation failed: {str(e)}")
            return False
    
    def _convert_with_libreoffice(self, document: Document) -> bool:
        """Convert using LibreOffice headless mode"""
        try:
            # Check if LibreOffice is available
            libreoffice_cmd = self._get_libreoffice_command()
            if not libreoffice_cmd:
                logger.error("LibreOffice not found. Please install LibreOffice.")
                return False
            
            # Determine input path
            if document.source_url:
                # Download DOCX file
                response = requests.get(document.source_url, timeout=60)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                    temp_file.write(response.content)
                    docx_path = temp_file.name
            else:
                docx_path = document.source_path
            
            try:
                # Create output directory
                output_dir = Path(self.temp_dir) / "docx2pdf_output"
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate output filename
                if document.filename:
                    pdf_filename = document.filename
                else:
                    docx_name = Path(docx_path).stem
                    pdf_filename = f"{docx_name}.pdf"
                
                pdf_path = output_dir / pdf_filename
                document.output_path = str(pdf_path)
                
                # LibreOffice command for conversion
                cmd = [
                    libreoffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", str(output_dir),
                    docx_path
                ]
                
                logger.info(f"Running conversion command: {' '.join(cmd)}")
                
                # Run conversion
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    # LibreOffice creates PDF with same name as DOCX
                    docx_name = Path(docx_path).stem
                    generated_pdf = output_dir / f"{docx_name}.pdf"
                    
                    if generated_pdf.exists():
                        # Move to desired output path if different
                        if generated_pdf != pdf_path:
                            shutil.move(str(generated_pdf), str(pdf_path))
                        
                        logger.info(f"PDF created successfully: {pdf_path}")
                        return True
                    else:
                        logger.error("PDF file not found after conversion")
                        return False
                else:
                    logger.error(f"LibreOffice conversion failed: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temporary file if it was downloaded
                if document.source_url and os.path.exists(docx_path):
                    os.unlink(docx_path)
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return False
        except Exception as e:
            logger.error(f"LibreOffice conversion error: {str(e)}")
            return False
    
    def _get_libreoffice_command(self) -> Optional[str]:
        """Get LibreOffice command for current platform"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            possible_paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
                "/usr/local/bin/libreoffice",
                "/opt/homebrew/bin/libreoffice"
            ]
        elif system == "Windows":
            possible_paths = [
                "C:\\Program Files\\LibreOffice\\program\\soffice.exe",
                "C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe"
            ]
        else:  # Linux
            possible_paths = [
                "/usr/bin/libreoffice",
                "/usr/local/bin/libreoffice",
                "/snap/bin/libreoffice"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(
                ["which", "libreoffice"] if system != "Windows" else ["where", "libreoffice"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None