# Use Selenium image with Python and Chrome preinstalled
FROM selenium/standalone-chrome:latest

# Set working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your crawler code
COPY . .

# Run your crawler
CMD ["python", "main.py"]
