FROM python:3.11-slim
WORKDIR /app

# Explicitly copy the server directory to ensure visibility
COPY server/ ./server/
# Also copy everything else
COPY . .

# Install from the explicit path
RUN pip install --no-cache-dir -r ./server/requirements.txt

EXPOSE 7860
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
