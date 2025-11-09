FROM python:3.14-slim

WORKDIR /climapp

COPY /c/JeanCossio/Python/climapp /app

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 5000

ENV FLASK_APP=app.py

CMD ["python", "app.py"]
