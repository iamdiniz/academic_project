#!/bin/bash
# Script executado automaticamente pelo MySQL na primeira inicialização
# Gera certificados SSL e aplica configuração TLS 1.2

set -e

echo "[SSL] Gerando certificados SSL..."

# Cria diretório se não existir
mkdir -p /etc/mysql/ssl

# Gera certificados SSL se não existirem
if [ ! -f /etc/mysql/ssl/server-cert.pem ]; then
    openssl genrsa -out /etc/mysql/ssl/ca-key.pem 2048
    openssl req -new -x509 -nodes -days 3650 -key /etc/mysql/ssl/ca-key.pem -out /etc/mysql/ssl/ca.pem -subj '/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=MySQL-CA'
    openssl genrsa -out /etc/mysql/ssl/server-key.pem 2048
    openssl req -new -key /etc/mysql/ssl/server-key.pem -out /etc/mysql/ssl/server-req.pem -subj '/C=BR/ST=Estado/L=Cidade/O=Organizacao/CN=mysql-server'
    openssl x509 -req -in /etc/mysql/ssl/server-req.pem -days 3650 -CA /etc/mysql/ssl/ca.pem -CAkey /etc/mysql/ssl/ca-key.pem -CAcreateserial -out /etc/mysql/ssl/server-cert.pem
    chmod 600 /etc/mysql/ssl/*.pem
    chmod 644 /etc/mysql/ssl/ca.pem
    chmod 644 /etc/mysql/ssl/server-cert.pem
    echo "[SSL] Certificados SSL gerados com sucesso!"
else
    echo "[SSL] Certificados SSL já existem."
fi

echo "[TLS] Aguardando MySQL estar pronto para aplicar TLS 1.2..."
sleep 5

# Aplica TLS 1.2 (desabilita TLS 1.0 e 1.1)
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<EOF
SET GLOBAL tls_version = 'TLSv1.2';
SELECT @@GLOBAL.tls_version AS 'TLS Version Configurado';
EOF

echo "[TLS] ✓ Configuração TLS 1.2 aplicada com sucesso!"


