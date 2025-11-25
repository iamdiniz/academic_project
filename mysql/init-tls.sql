-- Script de inicialização para configurar TLS 1.2 APENAS
-- Este script é executado automaticamente na primeira inicialização do MySQL
-- Desabilita TLS 1.0 e TLS 1.1, permitindo apenas TLS 1.2

-- Configura tls_version para aceitar APENAS TLS 1.2
-- Isso desabilita automaticamente TLS 1.0 e TLS 1.1
SET GLOBAL tls_version = 'TLSv1.2';

-- Verifica se a configuração foi aplicada
-- SELECT @@GLOBAL.tls_version; -- Deve retornar 'TLSv1.2'


