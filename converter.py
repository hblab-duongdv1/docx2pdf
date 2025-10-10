import os
import tempfile
import requests  # pyright: ignore[reportMissingModuleSource]
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import subprocess
import platform

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocxToPdfConverter:
    """
    High-quality DOCX to PDF converter with font embedding support
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.font_cache = {}
        
    def download_font(self, font_url: str, font_name: str) -> str:
        """
        Download font from URL and cache it locally
        
        Args:
            font_url: URL to download font from
            font_name: Name to save the font as
            
        Returns:
            Path to downloaded font file
        """
        try:
            # Create fonts directory if it doesn't exist
            fonts_dir = Path(self.temp_dir) / "fonts"
            fonts_dir.mkdir(exist_ok=True)
            
            font_path = fonts_dir / f"{font_name}.ttf"
            
            # Skip download if already cached
            if font_path.exists():
                logger.info(f"Font {font_name} already cached")
                return str(font_path)
            
            # Download font
            logger.info(f"Downloading font from {font_url}")
            response = requests.get(font_url, timeout=30)
            response.raise_for_status()
            
            # Save font
            with open(font_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Font {font_name} downloaded successfully")
            return str(font_path)
            
        except Exception as e:
            logger.error(f"Failed to download font {font_name}: {str(e)}")
            raise
    
    def install_font(self, font_path: str) -> bool:
        """
        Install font to system (for better PDF rendering)
        
        Args:
            font_path: Path to font file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            system = platform.system()
            
            if system == "Darwin":  # macOS
                # Copy to user fonts directory
                user_fonts = Path.home() / "Library" / "Fonts"
                user_fonts.mkdir(exist_ok=True)
                
                font_name = Path(font_path).name
                dest_path = user_fonts / font_name
                
                if not dest_path.exists():
                    import shutil
                    shutil.copy2(font_path, dest_path)
                    logger.info(f"Font installed to {dest_path}")
                
            elif system == "Windows":
                # Windows font installation would require additional permissions
                logger.warning("Windows font installation not implemented")
                
            elif system == "Linux":
                # Linux font installation
                user_fonts = Path.home() / ".fonts"
                user_fonts.mkdir(exist_ok=True)
                
                font_name = Path(font_path).name
                dest_path = user_fonts / font_name
                
                if not dest_path.exists():
                    import shutil
                    shutil.copy2(font_path, dest_path)
                    logger.info(f"Font installed to {dest_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install font: {str(e)}")
            return False
    
    def convert_docx_to_pdf(self, 
                           docx_path: str, 
                           pdf_path: str,
                           font_urls: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        Convert DOCX to PDF with high quality and font embedding
        
        Args:
            docx_path: Path to input DOCX file
            pdf_path: Path to output PDF file
            font_urls: List of font dictionaries with 'url' and 'name' keys
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Download and install fonts if provided
            if font_urls:
                for font_info in font_urls:
                    font_url = font_info.get('url')
                    font_name = font_info.get('name')
                    
                    if font_url and font_name:
                        font_path = self.download_font(font_url, font_name)
                        self.install_font(font_path)
            
            # Use LibreOffice for high-quality conversion
            return self._convert_with_libreoffice(docx_path, pdf_path)
            
        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            return False
    
    def _convert_with_libreoffice(self, docx_path: str, pdf_path: str) -> bool:
        """
        Convert using LibreOffice headless mode for best quality
        
        Args:
            docx_path: Path to input DOCX file
            pdf_path: Path to output PDF file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if LibreOffice is available
            libreoffice_cmd = self._get_libreoffice_command()
            if not libreoffice_cmd:
                logger.error("LibreOffice not found. Please install LibreOffice.")
                return False
            
            # Create output directory
            output_dir = Path(pdf_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)
            
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
                    if generated_pdf != Path(pdf_path):
                        import shutil
                        shutil.move(str(generated_pdf), pdf_path)
                    
                    logger.info(f"PDF created successfully: {pdf_path}")
                    return True
                else:
                    logger.error("PDF file not found after conversion")
                    return False
            else:
                logger.error(f"LibreOffice conversion failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Conversion timed out")
            return False
        except Exception as e:
            logger.error(f"LibreOffice conversion error: {str(e)}")
            return False
    
    def _get_libreoffice_command(self) -> Optional[str]:
        """
        Get LibreOffice command for current platform
        
        Returns:
            LibreOffice command path or None if not found
        """
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
    
    def convert_from_url(self, 
                        docx_url: str, 
                        pdf_path: str,
                        font_urls: Optional[List[Dict[str, str]]] = None) -> bool:
        """
        Download DOCX from URL and convert to PDF
        
        Args:
            docx_url: URL to DOCX file
            pdf_path: Path to output PDF file
            font_urls: List of font dictionaries with 'url' and 'name' keys
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Download DOCX file
            logger.info(f"Downloading DOCX from {docx_url}")
            response = requests.get(docx_url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(response.content)
                temp_docx_path = temp_file.name
            
            try:
                # Convert to PDF
                success = self.convert_docx_to_pdf(temp_docx_path, pdf_path, font_urls)
                return success
            finally:
                # Clean up temporary file
                if os.path.exists(temp_docx_path):
                    os.unlink(temp_docx_path)
                    
        except Exception as e:
            logger.error(f"Failed to convert from URL: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    converter = DocxToPdfConverter()
    
    # Example with font embedding
    font_urls = [
        {
            "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
            "name": "Roboto-Regular"
        }
    ]
    
    # Test conversion
    success = converter.convert_from_url(
        docx_url="https://example.com/document.docx",
        pdf_path="output.pdf",
        font_urls=font_urls
    )
    
    if success:
        print("Conversion successful!")
    else:
        print("Conversion failed!")
