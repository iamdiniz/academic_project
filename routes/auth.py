from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import logout_user
from services.auth_service import AuthService
from validators.form_validators import validar_nome, validar_email, validar_cargo
from utils.constants import CURSOS_PADRAO
from extensions.database import db
from models.curso import Curso
from models.instituicao import InstituicaodeEnsino

# Blueprint para autenticação
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Rota para cadastro de usuários"""
    if request.method == 'POST':
        tipo_usuario = request.form.get('tipo_usuario')
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Validação básica
        if senha != confirmar_senha:
            flash('As senhas não coincidem!')
            return redirect(url_for('auth.cadastro'))

        if tipo_usuario == 'instituicao':
            return _cadastrar_instituicao(request, nome, email, senha)
        elif tipo_usuario == 'chefe':
            return _cadastrar_chefe(request, nome, email, senha)
        else:
            flash('Tipo de usuário inválido!')
            return redirect(url_for('auth.cadastro'))

    return render_template('cadastro.html', cursos_padrao=CURSOS_PADRAO)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota para login de usuários"""
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Tenta autenticar como chefe
        chefe, erro = AuthService.login_chefe(email, senha)
        if chefe:
            return redirect(url_for('main.home'))

        # Tenta autenticar como instituição
        instituicao, erro = AuthService.login_instituicao(email, senha)
        if instituicao:
            return redirect(url_for('main.home'))

        flash(erro, "danger")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    """Rota para logout"""
    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('auth.login'))


def _cadastrar_instituicao(request, nome, email, senha):
    """Função auxiliar para cadastrar instituição"""
    instituicao_nome = request.form.get('instituicao_nome')
    endereco = request.form.get('endereco_instituicao')
    infraestrutura = request.form.get('infraestrutura')
    nota_mec = request.form.get('nota_mec')
    modalidades = request.form.get('modalidades')
    cursos_selecionados = request.form.getlist('cursos_selecionados')

    # Validações
    if not all([nome, email, senha, instituicao_nome, endereco, cursos_selecionados]):
        flash(
            'Todos os campos obrigatórios para Instituição de Ensino devem ser preenchidos!')
        return redirect(url_for('auth.cadastro'))

    if not validar_nome(instituicao_nome, max_length=50):
        flash('Nome da instituição inválido!')
        return redirect(url_for('auth.cadastro'))

    if not validar_email(email):
        flash('E-mail inválido!')
        return redirect(url_for('auth.cadastro'))

    # Verifica e-mail duplicado
    if InstituicaodeEnsino.query.filter_by(email=email).first():
        flash('Já existe uma instituição cadastrada com este e-mail.', 'danger')
        return redirect(url_for('auth.cadastro'))

    # Cadastra instituição
    instituicao, erro = AuthService.cadastrar_instituicao(
        instituicao_nome, email, senha, endereco, infraestrutura,
        nota_mec, modalidades, cursos_selecionados, nome
    )

    if erro:
        flash(erro, 'error')
        return redirect(url_for('auth.cadastro'))

    # Salva os cursos selecionados
    for nome_curso in cursos_selecionados:
        curso = Curso(nome=nome_curso,
                      id_instituicao=instituicao.id_instituicao)
        db.session.add(curso)
    db.session.commit()

    flash('Cadastro de Instituição realizado com sucesso! Faça login agora.', 'success')
    return redirect(url_for('auth.login'))


def _cadastrar_chefe(request, nome, email, senha):
    """Função auxiliar para cadastrar chefe"""
    empresa_nome = request.form.get('empresa_nome')
    cargo = request.form.get('cargo')

    # Validações
    if not all([nome, email, senha, empresa_nome, cargo]):
        flash('Todos os campos obrigatórios para Chefe devem ser preenchidos!')
        return redirect(url_for('auth.cadastro'))

    if not validar_nome(nome):
        flash('Nome inválido!')
        return redirect(url_for('auth.cadastro'))

    if not validar_email(email):
        flash('E-mail inválido!')
        return redirect(url_for('auth.cadastro'))

    if not validar_cargo(cargo):
        flash('Selecione um cargo válido!', 'danger')
        return redirect(url_for('auth.cadastro'))

    # Cadastra chefe
    chefe, erro = AuthService.cadastrar_chefe(
        nome, email, senha, empresa_nome, cargo)

    if erro:
        flash(erro, 'error')
        return redirect(url_for('auth.cadastro'))

    flash('Cadastro de Chefe realizado com sucesso! Faça login agora.', 'success')
    return redirect(url_for('auth.login'))
