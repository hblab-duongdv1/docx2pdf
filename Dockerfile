# ---------- Stage 1: Builder ----------
    FROM python:3.10-slim-bookworm AS builder

    # Disable .pyc & buffering
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1
    
    WORKDIR /app
    
    # Copy and install dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir --user -r requirements.txt \
        && find /root/.local -type d -name "__pycache__" -exec rm -rf {} +
    
    # ---------- Stage 2: Runtime ----------
    FROM python:3.10-slim-bookworm
    
    # Environment setup
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PATH=/root/.local/bin:$PATH
    
    # Install minimal LibreOffice (headless only)
    RUN apt-get update && \
        apt-get install -y --no-install-recommends \
            libreoffice-core \
            libreoffice-writer \
            libreoffice-common \
            libreoffice-java-common \
            fonts-dejavu-core \
            curl \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Set working directory
    WORKDIR /app
    
    # Copy only installed packages & app code
    COPY --from=builder /root/.local /root/.local
    COPY . .
    
    # Create necessary directories
    RUN mkdir -p /tmp/fonts /tmp/docx2pdf_output
    
    # Expose port
    EXPOSE 8080
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
        CMD curl -fs http://localhost:8080/health || exit 1
    
    # Run with uvicorn
    CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]