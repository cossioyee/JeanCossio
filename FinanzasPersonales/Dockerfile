FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["sqlite_web", "/data/finanzas.db", "--port", "1616", "--host", "0.0.0.0"]
