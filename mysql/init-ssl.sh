#!/bin/bash
# Script para gerar certificados SSL antes de iniciar MySQL

SSL_DIR="/etc/mysql/ssl"

# Cria diretório se não existir
mkdir -p "$SSL_DIR"

# Verifica se certificados já existem
if [ -f "$SSL_DIR/server-cert.pem" ]; then
    echo "Certificados SSL já existem, pulando geração..."
    exit 0
fi

echo "Gerando certificados SSL..."

# Gera chave privada da CA
openssl genrsa -out "$SSL_DIR/ca-key.pem" 2048

# Gera certificado da CA
openssl req -new -x509 -nodes -days 3650 \
    -key "$SSL_DIR/ca-key.pem" \
    -out "$SSL_DIR/ca.pem" \
    -subj "/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=MySQL-CA"

# Gera chave privada do servidor
openssl genrsa -out "$SSL_DIR/server-key.pem" 2048

# Gera requisição de certificado do servidor
openssl req -new -key "$SSL_DIR/server-key.pem" \
    -out "$SSL_DIR/server-req.pem" \
    -subj "/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=mysql-server"

# Gera certificado do servidor assinado pela CA
openssl x509 -req -in "$SSL_DIR/server-req.pem" \
    -days 3650 \
    -CA "$SSL_DIR/ca.pem" \
    -CAkey "$SSL_DIR/ca-key.pem" \
    -CAcreateserial \
    -out "$SSL_DIR/server-cert.pem"

# Ajusta permissões
chmod 600 "$SSL_DIR"/*.pem 2>/dev/null || true
chmod 644 "$SSL_DIR/ca.pem"
chmod 644 "$SSL_DIR/server-cert.pem"

echo "Certificados SSL gerados com sucesso!"

