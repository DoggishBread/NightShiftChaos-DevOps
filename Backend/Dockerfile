FROM python:3.9-slim

RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "python api.py > /app/api_logs.txt 2>&1 & sleep 3 && streamlit run App.py --server.port 8501 --server.address 0.0.0.0"]