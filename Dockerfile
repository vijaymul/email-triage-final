FROM python:3.11-slim
WORKDIR /app

# Set PYTHONPATH to ensure 'server' common module is found
ENV PYTHONPATH=/app

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Install the current directory as a package to register 'server'
RUN pip install --no-cache-dir -e .

EXPOSE 7860
# Use python -m to ensure the path is correctly handled
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
