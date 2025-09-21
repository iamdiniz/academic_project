from flask import Blueprint
from services import (
    processar_esqueceu_senha,
    processar_verificar_codigo,
    processar_verificar_codigo_post,
    processar_nova_senha_page
)

esquece_bp = Blueprint('esquece', __name__)


@esquece_bp.route('/esqueceu-senha', methods=['GET', 'POST'])
def esqueceu_senha():
    """Página de recuperação de senha."""
    return processar_esqueceu_senha()


@esquece_bp.route('/verificar-codigo')
def verificar_codigo():
    """Página de verificação de código."""
    return processar_verificar_codigo()


@esquece_bp.route('/verificar-codigo', methods=['POST'])
def verificar_codigo_post():
    """Processa verificação de código."""
    return processar_verificar_codigo_post()


@esquece_bp.route('/nova-senha', methods=['GET', 'POST'])
def nova_senha():
    """Página de nova senha."""
    return processar_nova_senha_page()
