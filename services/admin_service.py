"""
Serviço para operações administrativas do sistema.
Inclui funcionalidades de bloqueio/desbloqueio de usuários.
"""

# Imports removidos - não utilizados neste serviço
from domain import Chefe, InstituicaodeEnsino
from services.rate_limit_service import bloquear_usuario_permanentemente, desbloquear_usuario


def admin_bloquear_usuario(email):
    """
    Bloqueia um usuário permanentemente no sistema.

    Args:
        email (str): Email do usuário a ser bloqueado

    Returns:
        tuple: (sucesso, mensagem, redirect_url)
    """
    email = email.strip().lower()

    if not email:
        return False, "Email é obrigatório.", 'configuracoes'

    # Verificar se o email existe no sistema
    chefe = Chefe.query.filter_by(email=email).first()
    instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

    if not chefe and not instituicao:
        return False, "Email não encontrado no sistema.", 'configuracoes'

    # Bloquear o usuário
    bloquear_usuario_permanentemente(email)

    return True, f"Usuário {email} bloqueado permanentemente.", 'configuracoes'


def admin_desbloquear_usuario(email):
    """
    Desbloqueia um usuário no sistema.

    Args:
        email (str): Email do usuário a ser desbloqueado

    Returns:
        tuple: (sucesso, mensagem, redirect_url)
    """
    email = email.strip().lower()

    if not email:
        return False, "Email é obrigatório.", 'configuracoes'

    # Desbloquear o usuário
    desbloquear_usuario(email)

    return True, f"Usuário {email} desbloqueado.", 'configuracoes'
