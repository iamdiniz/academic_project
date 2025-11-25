#!/bin/bash

# Script de testes para validar correção de vulnerabilidade TLS
# Uso: ./test_tls_security.sh

echo "=========================================="
echo "TESTE DE SEGURANÇA TLS/SSL - MySQL"
echo "=========================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Contador de testes
TESTS_PASSED=0
TESTS_FAILED=0

# Função para testar
test_check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "1. Verificando se containers estão rodando..."
docker-compose ps | grep -q "Up"
test_check "Containers estão rodando"

echo ""
echo "2. Verificando se porta 3307 NÃO está exposta..."
# Verifica se a porta 3307 não está sendo usada pelo Docker
docker-compose ps | grep -q "3307" && test_check "Porta 3307 NÃO está exposta (FALHOU - ainda exposta)" || test_check "Porta 3307 NÃO está exposta (OK)"

echo ""
echo "3. Verificando se MySQL está acessível apenas internamente..."
# Tenta conectar via nome do serviço (deve funcionar)
docker-compose exec -T db mysql -u root -p${DB_PASS:-jonas1385} -e "SELECT 1" > /dev/null 2>&1
test_check "MySQL acessível internamente (via nome 'db')"

echo ""
echo "4. Verificando se certificados SSL foram gerados..."
docker-compose exec -T db test -f /etc/mysql/ssl/server-cert.pem
test_check "Certificados SSL foram gerados"

echo ""
echo "5. Verificando configuração TLS no MySQL..."
docker-compose exec -T db mysql -u root -p${DB_PASS:-jonas1385} -e "SHOW VARIABLES LIKE 'tls_version';" 2>/dev/null | grep -q "TLSv1.2"
test_check "TLS 1.2+ configurado no MySQL"

echo ""
echo "6. Verificando se SSL está habilitado..."
docker-compose exec -T db mysql -u root -p${DB_PASS:-jonas1385} -e "SHOW VARIABLES LIKE 'have_ssl';" 2>/dev/null | grep -q "YES"
test_check "SSL habilitado no MySQL"

echo ""
echo "7. Testando conexão da aplicação ao banco..."
# Verifica se a aplicação consegue conectar
sleep 2
docker-compose logs backend --tail 20 | grep -q "Tabelas criadas com sucesso"
test_check "Aplicação conectou ao banco com sucesso"

echo ""
echo "8. Verificando se aplicação está respondendo..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302\|301"
test_check "Aplicação está respondendo (HTTP 200/302/301)"

echo ""
echo "9. Verificando arquivo de configuração MySQL..."
test -f mysql/conf.d/mysql.cnf
test_check "Arquivo de configuração MySQL existe"

echo ""
echo "10. Verificando conteúdo da configuração TLS..."
grep -q "tls_version = TLSv1.2" mysql/conf.d/mysql.cnf
test_check "Configuração TLS 1.2+ presente no arquivo"

echo ""
echo "=========================================="
echo "RESULTADO DOS TESTES:"
echo "=========================================="
echo -e "${GREEN}Testes passados: ${TESTS_PASSED}${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "${RED}Testes falhados: ${TESTS_FAILED}${NC}"
    echo ""
    echo -e "${YELLOW}ATENÇÃO: Alguns testes falharam. Verifique os logs acima.${NC}"
    exit 1
else
    echo -e "${GREEN}Testes falhados: 0${NC}"
    echo ""
    echo -e "${GREEN}✓ TODOS OS TESTES PASSARAM!${NC}"
    echo -e "${GREEN}✓ Sistema está funcionando corretamente${NC}"
    echo -e "${GREEN}✓ Vulnerabilidade TLS corrigida${NC}"
    exit 0
fi


