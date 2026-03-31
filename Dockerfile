FROM python:3.11-slim
WORKDIR /app

# Set PYTHONPATH to ensure 'server' common module is found
ENV PYTHONPATH=/app

# Copy ALL files (required for pip install to work correctly for the package)
COPY . .

# Install the project and its dependencies from pyproject.toml
RUN pip install --no-cache-dir .

# Verification step: ensure 'server' is importable
RUN python -c "import server; print('Server package found')"

EXPOSE 7860
# Use uvicorn directly with the module path
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
