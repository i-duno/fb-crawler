# Use Selenium image with Chrome + Python
FROM selenium/standalone-chrome:latest

# Switch to root to install Python packages
USER root

# Set working directory
WORKDIR /app

# Install xvfb
#RUN apt-get update && apt-get install -y xvfb \
#    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-create undetected_chromedriver cache folder
RUN mkdir -p /home/seluser/.local/share/undetected_chromedriver \
    && chown -R seluser:seluser /home/seluser/.local

# Copy crawler code
COPY . .

EXPOSE 10000
#Flask port

# Switch back to selenium user for security
USER seluser

# Run crawler
#CMD ["xvfb-run", "python", "src/crawler.py"]
CMD ["python", "src/crawler.py"]
