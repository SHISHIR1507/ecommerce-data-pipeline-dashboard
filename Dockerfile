FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for layer caching
COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy FastAPI backend code
COPY backend/ backend/

# The API needs access to the processed data directory
# The docker-compose file will mount it as a volume, but we create the directory just in case
RUN mkdir -p data/processed

EXPOSE 8000

# Run uvicorn server
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
