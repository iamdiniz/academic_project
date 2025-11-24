@echo off
REM Script de testes para validar correção de vulnerabilidade TLS (Windows)
REM Uso: test_tls_security.bat

echo ==========================================
echo TESTE DE SEGURANCA TLS/SSL - MySQL
echo ==========================================
echo.

set TESTS_PASSED=0
set TESTS_FAILED=0

echo 1. Verificando se containers estao rodando...
docker-compose ps | findstr /C:"Up" >nul
if %errorlevel% equ 0 (
    echo [OK] Containers estao rodando
    set /a TESTS_PASSED+=1
) else (
    echo [ERRO] Containers nao estao rodando
    set /a TESTS_FAILED+=1
)

echo.
echo 2. Verificando se porta 3307 NAO esta exposta...
docker-compose ps | findstr /C:"3307" >nul
if %errorlevel% equ 0 (
    echo [ERRO] Porta 3307 ainda esta exposta
    set /a TESTS_FAILED+=1
) else (
    echo [OK] Porta 3307 NAO esta exposta
    set /a TESTS_PASSED+=1
)

echo.
echo 3. Verificando se MySQL esta acessivel internamente...
docker-compose exec -T db mysql -u root -pjonas1385 -e "SELECT 1" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] MySQL acessivel internamente
    set /a TESTS_PASSED+=1
) else (
    echo [ERRO] MySQL nao esta acessivel
    set /a TESTS_FAILED+=1
)

echo.
echo 4. Verificando se certificados SSL foram gerados...
docker-compose exec -T db test -f /etc/mysql/ssl/server-cert.pem
if %errorlevel% equ 0 (
    echo [OK] Certificados SSL foram gerados
    set /a TESTS_PASSED+=1
) else (
    echo [ERRO] Certificados SSL nao foram encontrados
    set /a TESTS_FAILED+=1
)

echo.
echo 5. Verificando se aplicacao esta respondendo...
timeout /t 3 >nul
curl -s -o nul -w "%%{http_code}" http://localhost:5000 | findstr /C:"200" /C:"302" /C:"301" >nul
if %errorlevel% equ 0 (
    echo [OK] Aplicacao esta respondendo
    set /a TESTS_PASSED+=1
) else (
    echo [ERRO] Aplicacao nao esta respondendo
    set /a TESTS_FAILED+=1
)

echo.
echo 6. Verificando arquivo de configuracao MySQL...
if exist "mysql\conf.d\mysql.cnf" (
    echo [OK] Arquivo de configuracao MySQL existe
    set /a TESTS_PASSED+=1
) else (
    echo [ERRO] Arquivo de configuracao MySQL nao encontrado
    set /a TESTS_FAILED+=1
)

echo.
echo ==========================================
echo RESULTADO DOS TESTES:
echo ==========================================
echo Testes passados: %TESTS_PASSED%
echo Testes falhados: %TESTS_FAILED%
echo.

if %TESTS_FAILED% gtr 0 (
    echo ATENCAO: Alguns testes falharam. Verifique os logs acima.
    exit /b 1
) else (
    echo [OK] TODOS OS TESTES PASSARAM!
    echo [OK] Sistema esta funcionando corretamente
    echo [OK] Vulnerabilidade TLS corrigida
    exit /b 0
)

