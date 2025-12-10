# web-app/Dockerfile
FROM python:3.10-slim

# Workdir inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Make startup script executable and fix line endings (Windows compatibility)
RUN chmod +x start.sh && \
    sed -i 's/\r$//' start.sh || true

# Flask will listen on 5000
EXPOSE 5000

# Run startup script (seeds DB, then starts Flask)
# Use bash explicitly to ensure it works
CMD ["bash", "start.sh"]