#!/bin/bash
# Script para gerar certificados SSL automaticamente

if [ ! -f /etc/mysql/ssl/server-cert.pem ]; then
    echo '[SSL] Gerando certificados SSL...'
    mkdir -p /etc/mysql/ssl
    openssl genrsa -out /etc/mysql/ssl/ca-key.pem 2048
    openssl req -new -x509 -nodes -days 3650 -key /etc/mysql/ssl/ca-key.pem -out /etc/mysql/ssl/ca.pem -subj '/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=MySQL-CA'
    openssl genrsa -out /etc/mysql/ssl/server-key.pem 2048
    openssl req -new -key /etc/mysql/ssl/server-key.pem -out /etc/mysql/ssl/server-req.pem -subj '/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=mysql-server'
    openssl x509 -req -in /etc/mysql/ssl/server-req.pem -days 3650 -CA /etc/mysql/ssl/ca.pem -CAkey /etc/mysql/ssl/ca-key.pem -CAcreateserial -out /etc/mysql/ssl/server-cert.pem
    chmod 600 /etc/mysql/ssl/*.pem
    chmod 644 /etc/mysql/ssl/ca.pem
    chmod 644 /etc/mysql/ssl/server-cert.pem
    echo '[SSL] Certificados SSL gerados com sucesso!'
else
    echo '[SSL] Certificados SSL já existem.'
fi
