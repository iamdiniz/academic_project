"""
Serviço de Rate Limiting - Gerencia tentativas de login e bloqueios.
Código movido do app.py para organizar responsabilidades.
"""

import time
import os
from datetime import datetime

# Dicionário para armazenar tentativas de login por email
# Estrutura: {email: {'count': número_tentativas, 'last_attempt': timestamp, 'blocked_until': timestamp, 'fase': 1 ou 2}}
rate_limit_attempts = {}

# Lista de emails bloqueados permanentemente (por redefinir senha)
usuarios_bloqueados = set()

# Configurações do rate limiting
MAX_LOGIN_ATTEMPTS = 3  # Máximo de tentativas permitidas por fase
# Duração do bloqueio temporário em segundos (5 minutos)
BLOCK_DURATION = 300
WARNING_THRESHOLD = 3   # Aviso na 3ª tentativa (última antes do bloqueio)

# Arquivo de log para falhas de login
LOG_FILE = 'logs/login_failures.log'


def verificar_rate_limit(email):
    agora = time.time()

    # Se é a primeira tentativa deste email, inicializa o contador na FASE 1
    if email not in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': agora,
            'blocked_until': 0,
            'fase': 1
        }

    dados_email = rate_limit_attempts[email]

    # Verifica se o email ainda está bloqueado temporariamente
    if dados_email['blocked_until'] > agora:
        tempo_restante = int(dados_email['blocked_until'] - agora)
        return False, f"Muitas tentativas de login. Tente novamente em {tempo_restante} segundos.", 0

    # Se passou o tempo de bloqueio temporário, avança para FASE 2
    if dados_email['blocked_until'] > 0 and agora > dados_email['blocked_until']:
        dados_email['count'] = 0
        dados_email['blocked_until'] = 0
        dados_email['fase'] = 2  # Avança para FASE 2

    # Incrementa o contador de tentativas
    dados_email['count'] += 1
    dados_email['last_attempt'] = agora

    # Verifica se excedeu o limite (4ª tentativa = bloqueio)
    if dados_email['count'] > MAX_LOGIN_ATTEMPTS:
        if dados_email['fase'] == 1:
            # FASE 1: Bloqueio temporário
            dados_email['blocked_until'] = agora + BLOCK_DURATION
            return False, f"Muitas tentativas de login. Bloqueado por {BLOCK_DURATION//60} minutos.", 0
        else:
            # FASE 2: Bloqueio permanente
            bloquear_usuario_permanentemente(email)
            return False, "Muitas tentativas de login. Sua conta foi bloqueada permanentemente. Redefina a senha para continuar.", 0

    # Calcula tentativas restantes
    tentativas_restantes = MAX_LOGIN_ATTEMPTS - dados_email['count']

    # Mensagens de aviso baseadas na fase
    if dados_email['count'] == WARNING_THRESHOLD:
        if dados_email['fase'] == 1:
            return True, "Última tentativa antes do bloqueio temporário.", tentativas_restantes
        else:
            return True, "Última tentativa antes do bloqueio permanente.", tentativas_restantes

    # Mensagens padrão para tentativas 1 e 2
    if dados_email['count'] <= 2:
        if dados_email['fase'] == 2:
            return True, "E-mail ou senha inválidos.", tentativas_restantes
        else:
            return True, "E-mail ou senha inválidos.", tentativas_restantes

    return True, "", tentativas_restantes


def resetar_rate_limit(email):
    """
    Reseta o contador de tentativas para um email específico.
    Usado quando o login é bem-sucedido.

    IMPORTANTE: Se o usuário estava na FASE 2, volta para FASE 1 após login bem-sucedido.
    """
    if email in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': time.time(),
            'blocked_until': 0,
            'fase': 1  # Volta para FASE 1 após login bem-sucedido
        }


def bloquear_usuario_permanentemente(email):
    """
    Adiciona um email à lista de bloqueio permanente.
    Usado para bloquear contas comprometidas ou suspeitas.
    """
    usuarios_bloqueados.add(email)


def desbloquear_usuario(email):
    """
    Remove um email da lista de bloqueio permanente.
    Usado para desbloquear contas após verificação de segurança.

    IMPORTANTE: Também reseta o sistema de fases para FASE 1.
    """
    usuarios_bloqueados.discard(email)
    # Reseta o sistema de fases para FASE 1
    if email in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': time.time(),
            'blocked_until': 0,
            'fase': 1
        }


def obter_numero_tentativa_atual(email):
    """
    Obtém o número da tentativa atual para um email específico.
    Retorna 0 se não houver tentativas registradas.
    """
    if email not in rate_limit_attempts:
        return 0
    return rate_limit_attempts[email]['count']


def registrar_falha_login(email, tentativa_numero):
    """
    Registra uma falha de login no arquivo de log.
    Cria o diretório logs/ se não existir.
    
    Args:
        email: Email do usuário que tentou fazer login
        tentativa_numero: Número da tentativa (1-5)
    """
    # Cria o diretório logs/ se não existir
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    # Formata a data e hora atual
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Escreve no arquivo de log
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] FALHA DE LOGIN - Email: {email} - Tentativa: {tentativa_numero}/{MAX_LOGIN_ATTEMPTS}\n")
