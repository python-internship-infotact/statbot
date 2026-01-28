FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p workspace static

# Create non-root user for security
RUN useradd -m -u 1000 statbot && chown -R statbot:statbot /app
USER statbot

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]