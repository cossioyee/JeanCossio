FROM python:3.14-rc-alpine

WORKDIR /app

COPY web.py /app

RUN pip install flask

EXPOSE 2000

RUN ls -la /app

ENTRYPOINT ["python", "web.py"]
