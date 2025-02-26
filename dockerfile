FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["python3.11", "-m", "streamlit", "run", "app2/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

