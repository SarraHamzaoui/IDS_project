FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
COPY app_ids.py .
COPY IDS_RandomForest_v1.pkl .
COPY IDS_Scaler_v1.pkl .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app_ids.py", "--server.port=8501", "--server.address=0.0.0.0"]