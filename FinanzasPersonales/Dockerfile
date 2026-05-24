FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY finanzaspersonales.py .
COPY cuentas.xlsx .

CMD ["python", "finanzaspersonales.py"]
