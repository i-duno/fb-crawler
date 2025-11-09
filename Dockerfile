# Use Selenium image with Chrome + Python
FROM python:3.11-slim

# Switch to root to install Python packages
USER root

# Set working directory
WORKDIR /app

# Install system dependencies & Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-liberation \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    wget \
    unzip \
    ca-certificates \
    gnupg \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install packages
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy crawler code
COPY . .

# Run crawler
CMD ["python", "src/crawler.py"]