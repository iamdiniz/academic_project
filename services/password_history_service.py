"""
Serviço de histórico de senhas.
Garante que os usuários não reutilizem as últimas senhas.
"""

from werkzeug.security import check_password_hash
from domain import db, PasswordHistory

PASSWORD_REUSE_MESSAGE = "Você não pode reutilizar nenhuma das 3 últimas senhas."


def senha_ja_utilizada_recentemente(user_type: str, user_id: int, senha_plana: str, limite: int = 3) -> bool:
    """
    Verifica se a senha enviada já foi utilizada nas últimas `limite` trocas.
    """
    if not senha_plana or not user_type or not user_id:
        return False

    historicos = (
        PasswordHistory.query
        .filter_by(user_type=user_type, user_id=user_id)
        .order_by(PasswordHistory.created_at.desc(), PasswordHistory.id.desc())
        .limit(limite)
        .all()
    )

    return any(check_password_hash(hist.senha_hash, senha_plana) for hist in historicos)


def registrar_senha_no_historico(user_type: str, user_id: int, senha_hash: str, limite: int = 3) -> None:
    """
    Armazena a nova senha no histórico e mantém apenas as `limite` mais recentes.
    """
    if not senha_hash or not user_type or not user_id:
        return

    novo_registro = PasswordHistory(
        user_type=user_type,
        user_id=user_id,
        senha_hash=senha_hash
    )
    db.session.add(novo_registro)
    db.session.flush()

    historicos = (
        PasswordHistory.query
        .filter_by(user_type=user_type, user_id=user_id)
        .order_by(PasswordHistory.created_at.desc(), PasswordHistory.id.desc())
        .all()
    )

    excedentes = historicos[limite:]
    for registro_antigo in excedentes:
        db.session.delete(registro_antigo)

