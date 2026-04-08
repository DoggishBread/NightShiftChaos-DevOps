FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --default-timeout=100 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501 8000

CMD ["sh", "-c", "python api.py & streamlit run App.py --server.port 8501 --server.address 0.0.0.0"]