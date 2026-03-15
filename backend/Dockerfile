FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy full project so `backend` package is importable
COPY backend/ backend/
COPY scripts/ scripts/

RUN chmod +x backend/entrypoint.sh

EXPOSE 8000
CMD ["backend/entrypoint.sh"]
