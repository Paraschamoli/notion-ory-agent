FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app

EXPOSE 8000

# Run the FastAPI app by default
CMD ["python", "scripts/run_app.py"]

