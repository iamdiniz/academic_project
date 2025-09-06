from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user
from sqlalchemy.exc import IntegrityError

# Criar o blueprint de autenticação
auth_bp = Blueprint('auth', __name__)

# Constantes necessárias para o cadastro
CURSOS_PADRAO = [
    "Administração", "Agronomia", "Arquitetura", "Biologia", "Ciência da Computação",
    "Direito", "Educação Física", "Enfermagem", "Engenharia", "Farmácia", "Física",
    "Matemática", "Medicina", "Pedagogia", "Psicologia", "Química", "Sistemas de Informação",
]


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


@auth_bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        from models import db, InstituicaodeEnsino, Chefe, Curso

        tipo_usuario = request.form.get('tipo_usuario')
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        if senha != confirmar_senha:
            flash('As senhas não coincidem!')
            return redirect(url_for('auth.cadastro'))

        if tipo_usuario == 'instituicao':
            instituicao_nome = request.form.get('instituicao_nome')
            endereco = request.form.get('endereco_instituicao')
            infraestrutura = request.form.get('infraestrutura')
            nota_mec = request.form.get('nota_mec')
            modalidades = request.form.get('modalidades')
            cursos_selecionados = request.form.getlist('cursos_selecionados')

            if not nome or not email or not senha or not instituicao_nome or not endereco or not cursos_selecionados:
                flash(
                    'Todos os campos obrigatórios para Instituição de Ensino devem ser preenchidos!')
                return redirect(url_for('auth.cadastro'))

            # Validação: não permitir e-mail duplicado
            if InstituicaodeEnsino.query.filter_by(email=email).first():
                flash('Já existe uma instituição cadastrada com este e-mail.', 'danger')
                return redirect(url_for('auth.cadastro'))

            try:
                nova_instituicaodeEnsino = InstituicaodeEnsino(
                    nome_instituicao=instituicao_nome,
                    email=email,
                    senha=generate_password_hash(senha),
                    infraestrutura=infraestrutura,
                    nota_mec=nota_mec,
                    # Apenas para histórico, não para lógica
                    areas_de_formacao=", ".join(cursos_selecionados),
                    modalidades=modalidades,
                    quantidade_de_alunos=0,
                    reitor=nome,
                    endereco_instituicao=endereco
                )
                db.session.add(nova_instituicaodeEnsino)
                db.session.commit()

                # Salva os cursos selecionados na tabela cursos
                for nome_curso in cursos_selecionados:
                    curso = Curso(
                        nome=nome_curso, id_instituicao=nova_instituicaodeEnsino.id_instituicao)
                    db.session.add(curso)
                db.session.commit()

                flash(
                    'Cadastro de Instituição realizado com sucesso! Faça login agora.', 'success')
                return redirect(url_for('auth.login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou instituição já cadastrados.', 'error')
                return redirect(url_for('auth.cadastro'))

        elif tipo_usuario == 'chefe':
            empresa_nome = request.form.get('empresa_nome')
            cargo = request.form.get('cargo')

            if not nome or not email or not senha or not empresa_nome or not cargo:
                flash('Todos os campos obrigatórios para Chefe devem ser preenchidos!')
                return redirect(url_for('auth.cadastro'))

            # Validação do cargo
            if cargo not in ['CEO', 'Gerente', 'Coordenador']:
                flash('Selecione um cargo válido!', 'danger')
                return redirect(url_for('auth.cadastro'))

            try:
                novo_chefe = Chefe(
                    nome=nome,
                    email=email,
                    senha=generate_password_hash(senha),
                    nome_empresa=empresa_nome,
                    cargo=cargo
                )
                db.session.add(novo_chefe)
                db.session.commit()
                flash(
                    'Cadastro de Chefe realizado com sucesso! Faça login agora.', 'success')
                return redirect(url_for('auth.login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou chefe já cadastrados.', 'error')
                return redirect(url_for('auth.cadastro'))

        else:
            flash('Tipo de usuário inválido!')
            return redirect(url_for('auth.cadastro'))

    return render_template('cadastro.html', cursos_padrao=CURSOS_PADRAO)
