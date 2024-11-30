FROM python:3

WORKDIR /app

COPY requirements.txt ./
COPY uwsgi.ini /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN ["uwsgi", "--ini", "uwsgi.ini"]
czxc
CMD ["nginx", "-g", "daemon off;"]