"""
Serviço de Auditoria - Gerencia logs de acesso e ações do sistema.
Código movido do app.py para organizar responsabilidades.
"""

from datetime import datetime
from domain.models import LogAcesso, db


def registrar_log(acao, usuario_nome, cargo, tipo_usuario):
    log = LogAcesso(
        usuario_nome=usuario_nome,
        cargo=cargo,
        tipo_usuario=tipo_usuario,
        acao=acao,
        data_hora=datetime.now()
    )
    db.session.add(log)
    db.session.commit()
