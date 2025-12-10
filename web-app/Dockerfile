# web-app/Dockerfile
FROM python:3.10-slim

# Workdir inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Flask will listen on 5000
EXPOSE 5000

# Run startup script (seeds DB, then starts Flask)
CMD ["./start.sh"]