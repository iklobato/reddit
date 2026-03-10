FROM python:3.9-slim

WORKDIR /app

# Install OpenCV dependencies and netcat for network checks
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libfontconfig1 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies with specific pip version
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy OpenCV check script and verify installation
COPY check_opencv.py .
RUN chmod +x check_opencv.py && \
    python check_opencv.py || exit 1

# Copy application files
COPY t1.py .
COPY config-docker.yaml config.yaml
COPY usernames.txt .
COPY passwords.txt .
COPY docker-entrypoint.sh .

# Make entrypoint script executable
RUN chmod +x docker-entrypoint.sh

# Create directories
RUN mkdir -p frames

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Use the entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"] 