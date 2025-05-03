FROM python:3

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev default-mysql-client netcat-openbsd

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

EXPOSE 5000

CMD ["/wait-for-db.sh", "db", "python", "./app.py"]