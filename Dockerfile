FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the current WORKDIR (/app)
COPY . .

# Hugging Face Spaces strictly requires Port 7860
EXPOSE 7860

# Start the server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
