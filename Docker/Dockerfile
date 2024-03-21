FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["uwsgi", "--ini", "uwsgi.ini"]

CMD ["nginx", "-g", "daemon off;"]