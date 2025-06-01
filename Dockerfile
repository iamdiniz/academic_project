FROM python:3

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev default-mysql-client netcat-openbsd dos2unix

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Certifique-se de copiar o script por último e ajustar permissões
COPY wait-for-db.sh /wait-for-db.sh
RUN dos2unix /wait-for-db.sh && chmod +x /wait-for-db.sh

EXPOSE 5000

# Executa o wait-for-db.sh passando os comandos finais
CMD ["/wait-for-db.sh", "python", "app.py"]