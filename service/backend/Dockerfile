FROM python:3.11-slim

WORKDIR /app

COPY service/backend/requirements.txt .

RUN pip install --no-cache-dir --timeout 600 \
    torch==2.7.1 \
    --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY service/backend/app/ ./app/
COPY service/backend/download_model.py ./

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
