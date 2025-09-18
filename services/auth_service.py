"""
Serviço de Autenticação - Funções de autenticação movidas do app.py.
Código movido para organizar responsabilidades, mantendo a lógica original.
"""

from functools import wraps
from flask import session, flash, redirect, url_for
from domain import Chefe, InstituicaodeEnsino


def load_user(user_id):
    """
    Carrega usuário - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        return Chefe.query.get(int(user_id))
    elif tipo_usuario == 'instituicao':
        return InstituicaodeEnsino.query.get(int(user_id))
    return None


def bloquear_chefe(f):
    """
    Decorator para bloquear chefes - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'chefe':
            flash("Acesso não permitido para o perfil chefe.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def bloquear_instituicao(f):
    """
    Decorator para bloquear instituições - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'instituicao':
            flash("Acesso não permitido para o perfil instituição de ensino.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function
