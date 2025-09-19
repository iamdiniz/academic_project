from flask import Blueprint, render_template, url_for, request, redirect, session, flash
from flask_login import login_required, logout_user, current_user
from services import (
    processar_cadastro,
    processar_login,
    registrar_log
)
from domain import Chefe, InstituicaodeEnsino

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro de usuários."""
    return processar_cadastro()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    return processar_login()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Faz logout do usuário."""

    if 'tipo_usuario' in session:
        tipo_usuario = session['tipo_usuario']
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get(session.get('user_id'))
            if chefe:
                registrar_log('logout', chefe.nome, chefe.cargo, 'chefe')
        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get(session.get('user_id'))
            if instituicao:
                registrar_log('logout', instituicao.nome_instituicao,
                              'reitor', 'instituicao')

    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
def index():
    """Redireciona para carousel."""
    return redirect(url_for('users.carousel'))


@auth_bp.route('/home')
@login_required
def home():
    """Página inicial baseada no tipo de usuário."""
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        return render_template('home_chefe.html')
    elif tipo_usuario == 'instituicao':
        return render_template('home_instituicao.html')
    else:
        flash("Tipo de usuário inválido. Faça login novamente.", "danger")
        return redirect(url_for('auth.login'))
