# Dockerfile for Leipzig Transport Display
# RGB LED Matrix on Raspberry Pi

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for building rpi-rgb-led-matrix
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    python3-dev \
    libfreetype6-dev \
    libopenjp2-7-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone and build rpi-rgb-led-matrix library
RUN git clone https://github.com/hzeller/rpi-rgb-led-matrix.git /tmp/rpi-rgb-led-matrix && \
    cd /tmp/rpi-rgb-led-matrix && \
    make build-python PYTHON=$(which python3) && \
    make install-python PYTHON=$(which python3) && \
    cd / && \
    rm -rf /tmp/rpi-rgb-led-matrix

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .
COPY led_matrix_display.py .
COPY transport_service.py .
COPY config_example.py .

# Copy config_local.py if it exists (optional)
COPY config_local.py* ./ 2>/dev/null || true

# Run as root (required for GPIO access)
USER root

# Start application
CMD ["python3", "main.py"]
