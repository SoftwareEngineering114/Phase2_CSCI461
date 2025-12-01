FROM python:3.11-slim

WORKDIR /app

# install deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy source
COPY . .

# Expose FastAPI on 8000 inside container
EXPOSE 8000

# NOTE:
# We DO NOT set CMD here because in CD we run uvicorn explicitly,
# passing LOG_FILE / LOG_LEVEL env vars.

