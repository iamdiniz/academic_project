#!/bin/bash
# Wrapper para entrypoint do MySQL que aplica configuração TLS 1.2

# Executa o entrypoint original do MySQL em background
docker-entrypoint.sh mysqld "$@" &
MYSQL_PID=$!

# Aguarda MySQL estar pronto (máximo 60 segundos)
echo "[TLS] Aguardando MySQL iniciar..."
for i in {1..60}; do
    mysqladmin ping -h localhost --silent 2>/dev/null && break
    sleep 1
done

# Verifica se MySQL está rodando
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "[TLS] ERRO: MySQL não iniciou corretamente"
    exit 1
fi

# Aplica configuração TLS 1.2 (desabilita TLS 1.0 e 1.1)
echo "[TLS] Aplicando configuração TLS 1.2 (desabilitando TLS 1.0/1.1)..."
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null || \
mysql -u root -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null

# Verifica se a configuração foi aplicada
TLS_VERSION=$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null || \
              mysql -u root -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null)

if [ "$TLS_VERSION" = "TLSv1.2" ]; then
    echo "[TLS] ✓ Configuração TLS 1.2 aplicada com sucesso!"
    echo "[TLS] ✓ TLS 1.0 e TLS 1.1 DESABILITADOS"
else
    echo "[TLS] ⚠ AVISO: Não foi possível verificar configuração TLS"
fi

# Mantém MySQL rodando em foreground
wait $MYSQL_PID

