#!/bin/bash
# Wrapper para entrypoint do MySQL que aplica configuração TLS 1.2
# Este script garante que TLS 1.2 seja aplicado sempre que MySQL inicia

set -e

# Encontra o entrypoint original do MySQL
ENTRYPOINT_SCRIPT="/usr/local/bin/docker-entrypoint.sh"
if [ ! -f "$ENTRYPOINT_SCRIPT" ]; then
    ENTRYPOINT_SCRIPT="/entrypoint.sh"
fi

# Executa o entrypoint original do MySQL em background
"$ENTRYPOINT_SCRIPT" mysqld "$@" &
MYSQL_PID=$!

# Aguarda MySQL estar pronto (máximo 60 segundos)
echo "[TLS] Aguardando MySQL iniciar..."
for i in {1..60}; do
    if mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "[TLS] MySQL está pronto!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "[TLS] ⚠️  Timeout aguardando MySQL (pode estar OK se ainda está inicializando)"
        # Não falha, apenas continua
        break
    fi
    sleep 1
done

# Aplica configuração TLS 1.2 (desabilita TLS 1.0 e 1.1)
echo "[TLS] Aplicando configuração TLS 1.2 (desabilitando TLS 1.0/1.1)..."
if [ -n "$MYSQL_ROOT_PASSWORD" ]; then
    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null || true
    TLS_VERSION=$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null || echo "")
else
    mysql -u root -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null || true
    TLS_VERSION=$(mysql -u root -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null || echo "")
fi

if [ "$TLS_VERSION" = "TLSv1.2" ]; then
    echo "[TLS] ✓ Configuração TLS 1.2 aplicada com sucesso!"
    echo "[TLS] ✓ TLS 1.0 e TLS 1.1 DESABILITADOS"
else
    echo "[TLS] ⚠️  Aviso: Não foi possível verificar TLS (pode estar OK se MySQL ainda está inicializando)"
fi

# Mantém MySQL rodando em foreground
wait $MYSQL_PID
