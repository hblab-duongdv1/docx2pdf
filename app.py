from flask import Flask, request, jsonify, send_file  # pyright: ignore[reportMissingImports]
from werkzeug.utils import secure_filename  # pyright: ignore[reportMissingImports]
import os
import tempfile
import uuid
from pathlib import Path
import logging
from converter import DocxToPdfConverter
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Initialize converter
converter = DocxToPdfConverter()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "docx2pdf-converter",
        "version": "1.0.0"
    })

@app.route('/convert', methods=['POST'])
def convert_docx_to_pdf():
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
        # Validate request
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json"
            }), 400
        
        data = request.get_json()
        
        # Validate required fields
        if 'docx_url' not in data:
            return jsonify({
                "error": "Missing required field: docx_url"
            }), 400
        
        docx_url = data['docx_url']
        font_urls = data.get('font_urls', [])
        output_filename = data.get('output_filename', f"converted_{uuid.uuid4().hex[:8]}.pdf")
        
        # Validate URL format
        if not docx_url.startswith(('http://', 'https://')):
            return jsonify({
                "error": "Invalid docx_url format. Must be a valid HTTP/HTTPS URL"
            }), 400
        
        # Validate font_urls format
        if font_urls:
            for font_info in font_urls:
                if not isinstance(font_info, dict) or 'url' not in font_info or 'name' not in font_info:
                    return jsonify({
                        "error": "Invalid font_urls format. Each font must have 'url' and 'name' fields"
                    }), 400
        
        # Create output directory
        output_dir = Path(tempfile.gettempdir()) / "docx2pdf_output"
        output_dir.mkdir(exist_ok=True)
        
        # Generate unique output path
        pdf_path = output_dir / secure_filename(output_filename)
        
        logger.info(f"Starting conversion: {docx_url} -> {pdf_path}")
        
        # Perform conversion
        success = converter.convert_from_url(
            docx_url=docx_url,
            pdf_path=str(pdf_path),
            font_urls=font_urls
        )
        
        if success and pdf_path.exists():
            logger.info(f"Conversion successful: {pdf_path}")
            
            # Return PDF file
            return send_file(
                str(pdf_path),
                as_attachment=True,
                download_name=output_filename,
                mimetype='application/pdf'
            )
        else:
            logger.error(f"Conversion failed for {docx_url}")
            return jsonify({
                "error": "Conversion failed. Please check the DOCX URL and try again."
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/convert-file', methods=['POST'])
def convert_uploaded_file():
    """
    Convert uploaded DOCX file to PDF
    
    Expected form data:
    - file: DOCX file
    - font_urls: JSON string (optional)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                "error": "No file provided"
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected"
            }), 400
        
        # Validate file extension
        if not file.filename.lower().endswith('.docx'):
            return jsonify({
                "error": "File must be a DOCX file"
            }), 400
        
        # Parse font URLs if provided
        font_urls = []
        if 'font_urls' in request.form:
            try:
                import json
                font_urls = json.loads(request.form['font_urls'])
            except json.JSONDecodeError:
                return jsonify({
                    "error": "Invalid font_urls JSON format"
                }), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
            file.save(temp_file.name)
            temp_docx_path = temp_file.name
        
        try:
            # Create output directory
            output_dir = Path(tempfile.gettempdir()) / "docx2pdf_output"
            output_dir.mkdir(exist_ok=True)
            
            # Generate output filename
            original_name = Path(file.filename).stem
            pdf_filename = f"{original_name}_converted.pdf"
            pdf_path = output_dir / pdf_filename
            
            logger.info(f"Converting uploaded file: {file.filename}")
            
            # Perform conversion
            success = converter.convert_docx_to_pdf(
                docx_path=temp_docx_path,
                pdf_path=str(pdf_path),
                font_urls=font_urls
            )
            
            if success and pdf_path.exists():
                logger.info(f"Conversion successful: {pdf_path}")
                
                # Return PDF file
                return send_file(
                    str(pdf_path),
                    as_attachment=True,
                    download_name=pdf_filename,
                    mimetype='application/pdf'
                )
            else:
                logger.error(f"Conversion failed for {file.filename}")
                return jsonify({
                    "error": "Conversion failed. Please check the DOCX file and try again."
                }), 500
                
        finally:
            # Clean up temporary file
            if os.path.exists(temp_docx_path):
                os.unlink(temp_docx_path)
                
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@app.route('/fonts/preview', methods=['POST'])
def preview_fonts():
    """
    Preview available fonts and their URLs
    """
    try:
        data = request.get_json()
        font_urls = data.get('font_urls', [])
        
        preview_results = []
        
        for font_info in font_urls:
            font_url = font_info.get('url')
            font_name = font_info.get('name')
            
            try:
                # Try to download font
                font_path = converter.download_font(font_url, font_name)
                preview_results.append({
                    "name": font_name,
                    "url": font_url,
                    "status": "available",
                    "path": font_path
                })
            except Exception as e:
                preview_results.append({
                    "name": font_name,
                    "url": font_url,
                    "status": "error",
                    "error": str(e)
                })
        
        return jsonify({
            "fonts": preview_results
        })
        
    except Exception as e:
        logger.error(f"Font preview error: {str(e)}")
        return jsonify({
            "error": f"Font preview failed: {str(e)}"
        }), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": "File too large. Maximum size is 50MB."
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error"
    }), 500

if __name__ == '__main__':
    # Create output directory
    output_dir = Path(tempfile.gettempdir()) / "docx2pdf_output"
    output_dir.mkdir(exist_ok=True)
    
    logger.info("Starting DOCX to PDF converter service...")
    logger.info("Available endpoints:")
    logger.info("  POST /convert - Convert DOCX from URL to PDF")
    logger.info("  POST /convert-file - Convert uploaded DOCX file to PDF")
    logger.info("  POST /fonts/preview - Preview font availability")
    logger.info("  GET /health - Health check")
    
    app.run(host='0.0.0.0', port=8080, debug=True)
