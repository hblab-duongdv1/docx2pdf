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

Chạy test suite:

```bash
python test_converter.py
```

## Cấu trúc dự án

```
docx2pdf/
├── app.py                 # Flask API server
├── converter.py           # Core conversion logic
├── test_converter.py      # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # Documentation
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

## Security

- File upload validation
- URL validation
- Temporary file cleanup
- Error message sanitization

## Roadmap

- [ ] Upload lên S3 storage
- [ ] Batch conversion
- [ ] Custom PDF settings (margins, page size)
- [ ] Watermark support
- [ ] Docker containerization
- [ ] CI/CD pipeline

## License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## Support

Nếu gặp vấn đề, vui lòng tạo issue trên GitHub repository.
