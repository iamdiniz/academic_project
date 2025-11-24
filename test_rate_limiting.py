#!/usr/bin/env python3
"""
Script de teste para verificar o rate limiting e logging.
Este script testa as funções sem precisar do Docker.
"""

import sys
import os
import time
from datetime import datetime

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importa as funções do rate_limit_service
from services.rate_limit_service import (
    verificar_rate_limit,
    resetar_rate_limit,
    registrar_falha_login,
    obter_numero_tentativa_atual,
    MAX_LOGIN_ATTEMPTS,
    BLOCK_DURATION,
    LOG_FILE
)

def test_configuracao():
    """Testa se as configurações estão corretas."""
    print("=" * 60)
    print("TESTE 1: Verificando Configurações")
    print("=" * 60)
    
    assert MAX_LOGIN_ATTEMPTS == 5, f"MAX_LOGIN_ATTEMPTS deve ser 5, mas é {MAX_LOGIN_ATTEMPTS}"
    assert BLOCK_DURATION == 600, f"BLOCK_DURATION deve ser 600 (10 min), mas é {BLOCK_DURATION}"
    
    print(f"[OK] MAX_LOGIN_ATTEMPTS: {MAX_LOGIN_ATTEMPTS}")
    print(f"[OK] BLOCK_DURATION: {BLOCK_DURATION} segundos ({BLOCK_DURATION // 60} minutos)")
    print(f"[OK] LOG_FILE: {LOG_FILE}")
    print()

def test_registro_falha():
    """Testa o registro de falhas de login."""
    print("=" * 60)
    print("TESTE 2: Registro de Falhas de Login")
    print("=" * 60)
    
    email_teste = "teste@exemplo.com"
    
    # Limpa o log anterior se existir
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    
    # Testa registro de 5 tentativas
    for i in range(1, 6):
        registrar_falha_login(email_teste, i)
        print(f"[OK] Tentativa {i} registrada")
    
    # Verifica se o arquivo foi criado
    assert os.path.exists(LOG_FILE), f"Arquivo de log {LOG_FILE} não foi criado!"
    
    # Lê o conteúdo do log
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    
    assert len(linhas) == 5, f"Esperado 5 linhas no log, mas encontrado {len(linhas)}"
    
    # Verifica se todas as tentativas foram registradas
    for i, linha in enumerate(linhas, 1):
        assert f"Tentativa: {i}/5" in linha, f"Tentativa {i} não encontrada no log"
        assert email_teste in linha, f"Email não encontrado na linha {i}"
    
    print(f"[OK] Arquivo de log criado: {LOG_FILE}")
    print(f"[OK] {len(linhas)} tentativas registradas corretamente")
    print()

def test_rate_limit():
    """Testa o sistema de rate limiting."""
    print("=" * 60)
    print("TESTE 3: Sistema de Rate Limiting")
    print("=" * 60)
    
    email_teste = "ratelimit@exemplo.com"
    
    # Reseta o rate limit
    resetar_rate_limit(email_teste)
    
    # Testa as primeiras 5 tentativas (devem ser permitidas)
    for i in range(1, 6):
        permitido, mensagem, tentativas_restantes = verificar_rate_limit(email_teste)
        tentativa_atual = obter_numero_tentativa_atual(email_teste)
        
        print(f"Tentativa {i}:")
        print(f"  - Permitido: {permitido}")
        print(f"  - Tentativa atual: {tentativa_atual}")
        print(f"  - Tentativas restantes: {tentativas_restantes}")
        print(f"  - Mensagem: {mensagem[:50]}..." if len(mensagem) > 50 else f"  - Mensagem: {mensagem}")
        
        if i == 5:
            assert "Última tentativa" in mensagem, "Deveria mostrar aviso na 5ª tentativa"
            print(f"  [OK] Aviso na 5ª tentativa: OK")
        
        assert permitido == True, f"Tentativa {i} deveria ser permitida"
        print()
    
    # A 6ª tentativa deve bloquear
    permitido, mensagem, _ = verificar_rate_limit(email_teste)
    tentativa_atual = obter_numero_tentativa_atual(email_teste)
    
    print(f"Tentativa 6 (deve bloquear):")
    print(f"  - Permitido: {permitido}")
    print(f"  - Tentativa atual: {tentativa_atual}")
    print(f"  - Mensagem: {mensagem}")
    
    assert permitido == False, "6ª tentativa deveria ser bloqueada"
    assert "Bloqueado por" in mensagem or "10" in mensagem, "Deveria mencionar bloqueio de 10 minutos"
    print(f"  [OK] Bloqueio funcionando corretamente")
    print()

def test_obter_numero_tentativa():
    """Testa a função obter_numero_tentativa_atual."""
    print("=" * 60)
    print("TESTE 4: Obter Número da Tentativa Atual")
    print("=" * 60)
    
    email_teste = "contador@exemplo.com"
    
    # Reseta
    resetar_rate_limit(email_teste)
    
    # Verifica antes de qualquer tentativa
    tentativa = obter_numero_tentativa_atual(email_teste)
    assert tentativa == 0, f"Tentativa inicial deveria ser 0, mas é {tentativa}"
    print(f"[OK] Tentativa inicial: {tentativa}")
    
    # Faz algumas tentativas
    for i in range(1, 4):
        verificar_rate_limit(email_teste)
        tentativa = obter_numero_tentativa_atual(email_teste)
        assert tentativa == i, f"Tentativa deveria ser {i}, mas é {tentativa}"
        print(f"[OK] Após {i} tentativa(s): {tentativa}")
    
    print()

def main():
    """Executa todos os testes."""
    print("\n" + "=" * 60)
    print("INICIANDO TESTES DO RATE LIMITING E LOGGING")
    print("=" * 60 + "\n")
    
    try:
        test_configuracao()
        test_registro_falha()
        test_rate_limit()
        test_obter_numero_tentativa()
        
        print("=" * 60)
        print("[OK] TODOS OS TESTES PASSARAM!")
        print("=" * 60)
        print("\nResumo:")
        print(f"  - Rate limiting: 5 tentativas configurado [OK]")
        print(f"  - Bloqueio: 10 minutos configurado [OK]")
        print(f"  - Logging: Funcionando [OK]")
        print(f"  - Funções: Todas funcionando [OK]")
        print("\nO sistema está pronto para uso com Docker!")
        
        return 0
        
    except AssertionError as e:
        print("\n" + "=" * 60)
        print("[ERRO] TESTE FALHOU!")
        print("=" * 60)
        print(f"Erro: {e}")
        return 1
    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERRO] ERRO INESPERADO!")
        print("=" * 60)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

