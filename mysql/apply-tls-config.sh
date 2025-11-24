#!/bin/bash
# Script para aplicar configuração TLS 1.2 após MySQL já estar rodando
# Use este script se o MySQL já foi inicializado antes da configuração TLS

echo "Aplicando configuração TLS 1.2..."

# Aguarda MySQL estar pronto
sleep 5

# Aplica configuração TLS 1.2
docker-compose exec -T db mysql -u root -p${MYSQL_ROOT_PASSWORD:-jonas1385} <<EOF
SET GLOBAL tls_version = 'TLSv1.2';
SELECT @@GLOBAL.tls_version AS 'TLS Version Configurado';
SHOW VARIABLES LIKE 'tls_version';
SHOW VARIABLES LIKE 'have_ssl';
EOF

echo "Configuração TLS aplicada!"

