from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user

# Criar o blueprint de autenticação
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        from models import Chefe, InstituicaodeEnsino

        email = request.form['email']
        senha = request.form['senha']

        # Verifica se o usuário é um chefe
        chefe = Chefe.query.filter_by(email=email).first()
        if chefe and check_password_hash(chefe.senha, senha):
            session['user_id'] = chefe.id_chefe
            session['tipo_usuario'] = 'chefe'
            login_user(chefe)
            return redirect(url_for('home'))

        # Verifica se o usuário é uma instituição de ensino
        instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()
        if instituicao and check_password_hash(instituicao.senha, senha):
            session['user_id'] = instituicao.id_instituicao
            session['tipo_usuario'] = 'instituicao'
            login_user(instituicao)
            return redirect(url_for('home'))

        flash("E-mail ou senha inválidos.", "danger")
    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('auth.login'))
