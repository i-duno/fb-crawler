# Use Selenium image with Chrome + Python
FROM selenium/standalone-chrome:latest

# Switch to root to install Python packages
USER root

# Set working directory
WORKDIR /app

# Set env variable
ENV CHROME_BIN="/usr/bin/google-chrome"

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
CMD ["python", "src/crawler.py"]