FROM python:3.9-slim

RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && apt-get install -y procps

CMD python api.py > api_logs.txt 2>&1 & sleep 2 && streamlit run App.py --server.port 8501 --server.address 0.0.0.0