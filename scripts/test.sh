curl -X POST http://localhost:8080/convert \
  -H "Content-Type: application/json" \
  -d '{
    "docx_url": "https://sample-public-bucket-new.s3.ap-southeast-1.amazonaws.com/Nominee+Resident+Director+Agreement.docx",
    "font_urls": [
      {
        "url": "https://pdftron-fonts-assets.s3.ap-southeast-1.amazonaws.com/fonts/Arial.ttf",
        "name": "Arial"
      }
    ],
    "output_filename": "custom_output.pdf"
  }' \
  -o custom_output.pdf