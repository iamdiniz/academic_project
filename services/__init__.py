"""
Módulo services - Contém os serviços de negócio do sistema.
Código movido do app.py para organizar responsabilidades.
"""

from .rate_limit_service import (
    verificar_rate_limit, resetar_rate_limit,
    bloquear_usuario_permanentemente, desbloquear_usuario
)
from .email_service import (
    enviar_email, gerar_codigo_verificacao
)
from .two_factor_service import (
    _get_or_create_2fa_record, _generate_qr_data_uri
)
from .audit_log_service import (
    registrar_log
)

__all__ = [
    # Rate Limit Service
    'verificar_rate_limit', 'resetar_rate_limit', 'bloquear_usuario_permanentemente', 'desbloquear_usuario',
    # Email Service
    'enviar_email', 'gerar_codigo_verificacao',
    # Two Factor Service
    '_get_or_create_2fa_record', '_generate_qr_data_uri',
    # Audit Log Service
    'registrar_log'
]
