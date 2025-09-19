from flask import Blueprint
from flask_login import login_required
from services import (
    processar_two_factor_setup,
    processar_two_factor_verify,
    processar_two_factor_disable
)

two_bp = Blueprint('two', __name__)

@two_bp.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    """Configura autenticação de dois fatores."""
    return processar_two_factor_setup()


@two_bp.route('/2fa/verify', methods=['GET', 'POST'])
def two_factor_verify():
    """Verifica código 2FA."""
    return processar_two_factor_verify()


@two_bp.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def two_factor_disable():
    """Desabilita autenticação de dois fatores."""
    return processar_two_factor_disable()
