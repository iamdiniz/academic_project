from functools import wraps
from flask import session, redirect, url_for, flash


def bloquear_chefe(f):
    """
    Decorador para bloquear acesso de chefes a determinadas rotas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'chefe':
            flash("Acesso não permitido para o perfil chefe.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def bloquear_instituicao(f):
    """
    Decorador para bloquear acesso de instituições a determinadas rotas
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'instituicao':
            flash("Acesso não permitido para o perfil instituição de ensino.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def requer_chefe(f):
    """
    Decorador para exigir que o usuário seja um chefe
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') != 'chefe':
            flash("Acesso restrito a chefes.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function


def requer_instituicao(f):
    """
    Decorador para exigir que o usuário seja uma instituição
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') != 'instituicao':
            flash("Acesso restrito a instituições de ensino.", "danger")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return decorated_function
