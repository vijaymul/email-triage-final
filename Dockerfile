FROM python:3.11-slim
WORKDIR /app

# Set PYTHONPATH to ensure 'server' common module is found
ENV PYTHONPATH=/app

# Copy configuration first to leverage Docker cache
COPY pyproject.toml .
COPY README.md .

# Install dependencies and the project
RUN pip install --no-cache-dir .

# Copy the rest of the application
COPY . .

# Re-install in editable mode to ensure 'server' is linked correctly
RUN pip install --no-cache-dir -e .

EXPOSE 7860
# Use python -m to ensure the path is correctly handled
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
