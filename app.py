from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException, Depends  # pyright: ignore[reportMissingImports]
from fastapi.responses import FileResponse # pyright: ignore[reportMissingImports]
from fastapi.middleware.cors import CORSMiddleware # pyright: ignore[reportMissingImports]
from pydantic import BaseModel # pyright: ignore[reportMissingImports]
import os
import tempfile
import uuid
from pathlib import Path
import logging
import traceback
from typing import List, Optional
import json

from src.infrastructure.di_container import di_container
from src.presentation.controllers import DocumentController

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DOCX to PDF Converter",
    description="A service to convert DOCX documents to PDF format",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize dependency injection container
container = di_container()

# Get document controller from container
document_controller = container.get(DocumentController)

# Pydantic models for request/response validation
class FontUrl(BaseModel):
    url: str
    name: str

class ConvertRequest(BaseModel):
    docx_url: str
    font_urls: List[FontUrl] = []
    output_filename: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    response = document_controller.health_check()
    return response

@app.post("/convert")
async def convert_docx_to_pdf(request: ConvertRequest):
    """
    Convert DOCX to PDF endpoint
    
    Expected JSON payload:
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
        # Convert Pydantic model to dict for the controller
        data = request.model_dump()
        
        # Set default output filename if not provided
        if not data.get('output_filename'):
            data['output_filename'] = f"converted_{uuid.uuid4().hex[:8]}.pdf"
        
        # Call the controller method
        result = document_controller.convert_docx_to_pdf(data)
        
        # Check if result is a tuple (error case) or file path (success case)
        if isinstance(result, tuple):
            response, status_code = result
            raise HTTPException(status_code=status_code, detail=response.get("error", "Conversion failed"))
        else:
            # result is a file path (success case)
            return FileResponse(
                path=result,
                filename=data['output_filename'],
                media_type='application/pdf'
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/convert-file")
async def convert_uploaded_file(
    file: UploadFile = File(...),
    font_urls: Optional[str] = Form(None)
):
    """
    Convert uploaded DOCX file to PDF
    
    Expected form data:
    - file: DOCX file
    - font_urls: JSON string (optional)
    """
    try:
        # Validate file extension
        if not file.filename.lower().endswith('.docx'):
            raise HTTPException(status_code=400, detail="File must be a DOCX file")
        
        # Parse font URLs if provided
        font_urls_list = []
        if font_urls:
            try:
                font_urls_list = json.loads(font_urls)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid font_urls JSON format")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_docx_path = temp_file.name
        
        try:
            # Generate output filename
            original_name = Path(file.filename).stem
            pdf_filename = f"{original_name}_converted.pdf"
            
            # Prepare data for controller
            data = {
                'docx_path': temp_docx_path,
                'font_urls': font_urls_list,
                'output_filename': pdf_filename
            }
            
            # Call the controller method
            result = document_controller.convert_uploaded_file(data)
            
            # Check if result is a tuple (error case) or file path (success case)
            if isinstance(result, tuple):
                response, status_code = result
                raise HTTPException(status_code=status_code, detail=response.get("error", "Conversion failed"))
            else:
                # result is a file path (success case)
                return FileResponse(
                    path=result,
                    filename=pdf_filename,
                    media_type='application/pdf'
                )
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_docx_path):
                os.unlink(temp_docx_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == '__main__':
    # Create output directory
    output_dir = Path(tempfile.gettempdir()) / "docx2pdf_output"
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Starting DOCX to PDF converter service...")
    logger.info("Available endpoints:")
    logger.info("  GET /health - Health check")
    logger.info("  POST /convert - Convert DOCX from URL to PDF")
    logger.info("  POST /convert-file - Convert uploaded DOCX file to PDF")
    logger.info("  GET /docs - API documentation (Swagger UI)")
    logger.info("  GET /redoc - Alternative API documentation")
    
    import uvicorn  # pyright: ignore[reportMissingImports]
    uvicorn.run(app, host='0.0.0.0', port=8080, log_level='info')
