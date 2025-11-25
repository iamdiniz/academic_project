#!/bin/bash
# Script master que executa tudo na ordem correta

set -e

# Gera certificados SSL se necessário
echo "[SSL] Verificando certificados SSL..."
/generate-ssl-certs.sh

# Encontra o entrypoint original do MySQL
# No MySQL 5.7, o entrypoint está em /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT_SCRIPT="/usr/local/bin/docker-entrypoint.sh"

if [ ! -f "$ENTRYPOINT_SCRIPT" ]; then
    echo "[ERRO] Entrypoint do MySQL não encontrado em $ENTRYPOINT_SCRIPT"
    echo "[ERRO] Tentando localizar entrypoint..."
    ENTRYPOINT_SCRIPT=$(find / -name "docker-entrypoint.sh" 2>/dev/null | head -1)
    if [ -z "$ENTRYPOINT_SCRIPT" ]; then
        echo "[ERRO] Entrypoint não encontrado. Usando entrypoint padrão."
        exec docker-entrypoint.sh mysqld "$@"
    fi
fi

echo "[MySQL] Usando entrypoint: $ENTRYPOINT_SCRIPT"

# Executa o entrypoint original do MySQL em background
echo "[MySQL] Iniciando MySQL..."
"$ENTRYPOINT_SCRIPT" mysqld "$@" &
MYSQL_PID=$!
echo "[MySQL] MySQL iniciado com PID: $MYSQL_PID"

# Aguarda MySQL estar pronto (máximo 120 segundos)
echo "[TLS] Aguardando MySQL iniciar..."
MAX_WAIT=120
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if mysqladmin ping -h localhost --silent 2>/dev/null; then
        echo "[TLS] MySQL está pronto!"
        break
    fi
    sleep 2
    WAITED=$((WAITED + 2))
    echo "[TLS] Aguardando... ($WAITED/$MAX_WAIT segundos)"
done

# Verifica se MySQL está rodando
if ! mysqladmin ping -h localhost --silent 2>/dev/null; then
    echo "[TLS] ERRO: MySQL não iniciou corretamente após $MAX_WAIT segundos"
    echo "[TLS] Verificando processo MySQL..."
    ps aux | grep mysqld || true
    exit 1
fi

# Aplica configuração TLS 1.2 (desabilita TLS 1.0 e 1.1)
echo "[TLS] Aplicando configuração TLS 1.2 (desabilitando TLS 1.0/1.1)..."
sleep 2
mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null || \
mysql -u root -e "SET GLOBAL tls_version = 'TLSv1.2';" 2>/dev/null || \
echo "[TLS] AVISO: Não foi possível aplicar TLS 1.2 via SQL (pode já estar configurado)"

# Verifica se a configuração foi aplicada
TLS_VERSION=$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null || \
              mysql -u root -se "SELECT @@GLOBAL.tls_version;" 2>/dev/null || echo "N/A")

if [ "$TLS_VERSION" = "TLSv1.2" ]; then
    echo "[TLS] ✓ Configuração TLS 1.2 aplicada com sucesso!"
    echo "[TLS] ✓ TLS 1.0 e TLS 1.1 DESABILITADOS"
else
    echo "[TLS] ⚠ AVISO: TLS version = $TLS_VERSION (esperado: TLSv1.2)"
fi

# Mantém MySQL rodando em foreground
echo "[MySQL] MySQL está rodando. Mantendo processo em foreground..."
echo "[MySQL] PID: $MYSQL_PID"

# Aguarda o processo MySQL (se ele terminar, o container também termina)
wait $MYSQL_PID
EXIT_CODE=$?
echo "[MySQL] Processo MySQL terminou com código: $EXIT_CODE"
exit $EXIT_CODE
