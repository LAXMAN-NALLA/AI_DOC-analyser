FROM python:3.10-slim

# Install OCR and PDF system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app files into the container
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy and allow execution of the startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose for local testing (Render uses PORT env instead)
EXPOSE 10000

# Use the startup script
CMD ["/app/start.sh"]
