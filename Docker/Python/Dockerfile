FROM python:3.14-slim

WORKDIR /climapp

COPY climapp/. /app

RUN pip install --no-cache-dir -r /app/requerimientos.txt

EXPOSE 5000

ENV FLASK_APP=app.py

ENTRYPOINT ["python", "/app/app.py"]
