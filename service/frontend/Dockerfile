FROM python:3.11-slim

WORKDIR /app

COPY service/frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service/frontend/ .

EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
