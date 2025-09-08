FROM python:3.12-slim

RUN apt-get update -y && \
    apt-get install -y build-essential default-mysql-client netcat-openbsd dos2unix libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Certifique-se de copiar o script por último e ajustar permissões
COPY wait-for-db.sh /wait-for-db.sh
RUN dos2unix /wait-for-db.sh && chmod +x /wait-for-db.sh

EXPOSE 5000

CMD ["/wait-for-db.sh"]