# DOCX to PDF Converter

Ứng dụng Python chuyển đổi file DOCX sang PDF với chất lượng cao và hỗ trợ embed fonts từ URL.

## Tính năng chính

- ✅ Chuyển đổi DOCX sang PDF với chất lượng cao
- ✅ Hỗ trợ download và embed fonts từ URL
- ✅ API REST để nhận DOCX từ URL và trả về PDF
- ✅ Upload file DOCX trực tiếp
- ✅ Error handling và validation đầy đủ
- ✅ Hỗ trợ nhiều platform (macOS, Windows, Linux)
- ✅ Sử dụng LibreOffice để đảm bảo chất lượng conversion

## Yêu cầu hệ thống

### Phần mềm cần thiết
- **Python 3.7+**
- **LibreOffice** (để conversion chất lượng cao)

### Cài đặt LibreOffice

#### macOS
```bash
# Sử dụng Homebrew
brew install --cask libreoffice

# Hoặc download từ https://www.libreoffice.org/download/download/
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install libreoffice
```

#### Windows
Download và cài đặt từ: https://www.libreoffice.org/download/download/

## Cài đặt

### Cách 1: Sử dụng setup script (Khuyến nghị)

```bash
# Clone repository
git clone <repository-url>
cd docx2pdf

# Chạy setup script
chmod +x setup.sh
./setup.sh
```

### Cách 2: Cài đặt thủ công

1. **Clone repository**
```bash
git clone <repository-url>
cd docx2pdf
```

2. **Tạo virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

4. **Cài đặt LibreOffice** (nếu chưa có)
```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt install libreoffice
```

## Sử dụng

### 1. Chạy API Server

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:8080`

### 2. API Endpoints

#### Health Check
```bash
GET /health
```

#### Convert từ URL
```bash
POST /convert
Content-Type: application/json

{
    "docx_url": "https://example.com/document.docx",
    "font_urls": [
        {
            "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
            "name": "Roboto-Regular"
        }
    ],
    "output_filename": "output.pdf"
}
```

#### Convert từ file upload
```bash
POST /convert-file
Content-Type: multipart/form-data

file: [DOCX file]
font_urls: [JSON string of font URLs]
```

#### Preview fonts
```bash
POST /fonts/preview
Content-Type: application/json

{
    "font_urls": [
        {
            "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
            "name": "Roboto-Regular"
        }
    ]
}
```

### 3. Sử dụng trực tiếp Converter

```python
from converter import DocxToPdfConverter

# Khởi tạo converter
converter = DocxToPdfConverter()

# Convert từ URL
success = converter.convert_from_url(
    docx_url="https://example.com/document.docx",
    pdf_path="output.pdf",
    font_urls=[
        {
            "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
            "name": "Roboto-Regular"
        }
    ]
)

if success:
    print("Conversion successful!")
else:
    print("Conversion failed!")
```

## Testing

### Chạy test suite đầy đủ:

```bash
# Test URL conversion
./test.sh

# Test health check
curl -s http://localhost:8080/health | jq .

# Test font preview
curl -X POST http://localhost:8080/fonts/preview \
  -H "Content-Type: application/json" \
  -d '{
    "font_urls": [
      {
        "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
        "name": "Roboto-Regular"
      }
    ]
  }' | jq .

# Test file upload (cần có file test_document.docx)
curl -X POST http://localhost:8080/convert-file \
  -F "file=@test_document.docx" \
  -F "font_urls=[]" \
  -o upload_test.pdf
```

### Tạo file test DOCX:

```bash
python -c "
from docx import Document
doc = Document()
doc.add_heading('Test Document', 0)
doc.add_paragraph('This is a test document for conversion.')
doc.save('test_document.docx')
print('Test DOCX created!')
"
```

## Cấu trúc dự án

```
docx2pdf/
├── app.py                 # Flask API server
├── converter.py           # Core conversion logic
├── test.sh               # Test script for URL conversion
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── Dockerfile            # Docker container
├── docker-compose.yml    # Docker Compose
├── README.md             # Documentation
├── test_document.docx    # Sample DOCX file
└── docx_to_pdf.pdf       # Sample output PDF
```

## Font URLs phổ biến

### Google Fonts
```json
[
    {
        "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
        "name": "Roboto-Regular"
    },
    {
        "url": "https://fonts.gstatic.com/s/opensans/v34/memSYaGs126MiZpBA-UvWbX2vVnXBbObj2OVZyOOSr4dVJWUgsjZ0B4gaVIGxA.woff2",
        "name": "OpenSans-Regular"
    }
]
```

### Font Squirrel
```json
[
    {
        "url": "https://www.fontsquirrel.com/fonts/download/roboto",
        "name": "Roboto-Regular"
    }
]
```

## Troubleshooting

### LibreOffice không tìm thấy
```bash
# Kiểm tra LibreOffice có được cài đặt
which libreoffice  # Linux/macOS
where libreoffice  # Windows

# Hoặc kiểm tra đường dẫn mặc định
ls /Applications/LibreOffice.app/Contents/MacOS/soffice  # macOS
```

### Font không download được
- Kiểm tra URL font có hợp lệ
- Kiểm tra kết nối internet
- Font phải là định dạng TTF/OTF

### Conversion thất bại
- Kiểm tra DOCX file có hợp lệ
- Kiểm tra LibreOffice có hoạt động
- Xem logs để debug chi tiết

## Performance

- **File size limit**: 50MB
- **Timeout**: 60 giây cho conversion
- **Font cache**: Fonts được cache để tái sử dụng
- **Temporary files**: Tự động cleanup sau conversion
- **Conversion speed**: ~1-2 giây cho tài liệu đơn giản, ~10-30 giây cho tài liệu phức tạp
- **Memory usage**: ~100-200MB RAM
- **Concurrent requests**: Hỗ trợ multiple requests đồng thời

## Security

- File upload validation
- URL validation
- Temporary file cleanup
- Error message sanitization

## Docker Deployment

### Sử dụng Docker Compose (Khuyến nghị)

```bash
# Build và chạy với Docker Compose
docker-compose up --build

# Chạy trong background
docker-compose up -d --build
```

### Sử dụng Docker trực tiếp

```bash
# Build image
docker build -t docx2pdf .

# Chạy container
docker run -p 8080:8080 docx2pdf
```

## Roadmap

- [x] ✅ Core conversion với LibreOffice
- [x] ✅ Font embedding từ URL
- [x] ✅ REST API endpoints
- [x] ✅ Docker containerization
- [x] ✅ Error handling và validation
- [ ] Upload lên S3 storage
- [ ] Batch conversion
- [ ] Custom PDF settings (margins, page size)
- [ ] Watermark support
- [ ] CI/CD pipeline

## License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## Examples

### Test với tài liệu thực tế

```bash
# Test với tài liệu phức tạp từ S3
./test.sh

# Kiểm tra kết quả
ls -la docx_to_pdf.pdf
file docx_to_pdf.pdf
```

### Sử dụng với custom fonts

```bash
curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "docx_url": "https://example.com/document.docx",
    "font_urls": [
      {
        "url": "https://pdftron-fonts-assets.s3.ap-southeast-1.amazonaws.com/fonts/Arial.ttf",
        "name": "Arial"
      },
      {
        "url": "https://fonts.gstatic.com/s/roboto/v30/KFOmCnqEu92Fr1Mu4mxK.woff2",
        "name": "Roboto-Regular"
      }
    ],
    "output_filename": "custom_font_output.pdf"
  }' \
  -o custom_output.pdf
```

## Support

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository hoặc kiểm tra:

1. **Logs**: Xem logs của server để debug
2. **LibreOffice**: Đảm bảo LibreOffice được cài đặt đúng
3. **Dependencies**: Kiểm tra tất cả packages đã được cài đặt
4. **Network**: Kiểm tra kết nối internet cho font downloads
