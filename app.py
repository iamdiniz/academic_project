from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from unidecode import unidecode
from urllib.parse import unquote
from math import ceil
from dotenv import load_dotenv
import pyotp
import base64
import io
import qrcode
from datetime import datetime, timedelta
from flask_wtf import CSRFProtect
import csv
import re
import json
import pytz
import os
import time
from flask_wtf.csrf import generate_csrf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import string


load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key:
    raise RuntimeError(
        "A variável FLASK_SECRET_KEY não está definida no ambiente!")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "A variável DATABASE_URL não está definida no ambiente!")


if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)


app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

# =============================================================================
# SISTEMA DE RATE LIMITING PARA LOGIN - PROTEÇÃO CONTRA FORÇA BRUTA
# =============================================================================
# Dicionário para armazenar tentativas de login por email
# Estrutura: {email: {'count': número_tentativas, 'last_attempt': timestamp, 'blocked_until': timestamp, 'fase': 1 ou 2}}
rate_limit_attempts = {}

# Lista de emails bloqueados permanentemente (por redefinir senha)
usuarios_bloqueados = set()

# Configurações do rate limiting
MAX_LOGIN_ATTEMPTS = 3  # Máximo de tentativas permitidas por fase
# Duração do bloqueio temporário em segundos (5 minutos)
BLOCK_DURATION = 300
WARNING_THRESHOLD = 3   # Aviso na 3ª tentativa (última antes do bloqueio)


def verificar_rate_limit(email):
    agora = time.time()

    # Se é a primeira tentativa deste email, inicializa o contador na FASE 1
    if email not in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': agora,
            'blocked_until': 0,
            'fase': 1
        }

    dados_email = rate_limit_attempts[email]

    # Verifica se o email ainda está bloqueado temporariamente
    if dados_email['blocked_until'] > agora:
        tempo_restante = int(dados_email['blocked_until'] - agora)
        return False, f"Muitas tentativas de login. Tente novamente em {tempo_restante} segundos.", 0

    # Se passou o tempo de bloqueio temporário, avança para FASE 2
    if dados_email['blocked_until'] > 0 and agora > dados_email['blocked_until']:
        dados_email['count'] = 0
        dados_email['blocked_until'] = 0
        dados_email['fase'] = 2  # Avança para FASE 2

    # Incrementa o contador de tentativas
    dados_email['count'] += 1
    dados_email['last_attempt'] = agora

    # Verifica se excedeu o limite (4ª tentativa = bloqueio)
    if dados_email['count'] > MAX_LOGIN_ATTEMPTS:
        if dados_email['fase'] == 1:
            # FASE 1: Bloqueio temporário
            dados_email['blocked_until'] = agora + BLOCK_DURATION
            return False, f"Muitas tentativas de login. Bloqueado por {BLOCK_DURATION//60} minutos.", 0
        else:
            # FASE 2: Bloqueio permanente
            bloquear_usuario_permanentemente(email)
            return False, "Muitas tentativas de login. Sua conta foi bloqueada permanentemente. Redefina a senha para continuar.", 0

    # Calcula tentativas restantes
    tentativas_restantes = MAX_LOGIN_ATTEMPTS - dados_email['count']

    # Mensagens de aviso baseadas na fase
    if dados_email['count'] == WARNING_THRESHOLD:
        if dados_email['fase'] == 1:
            return True, "Última tentativa antes do bloqueio temporário.", tentativas_restantes
        else:
            return True, "Última tentativa antes do bloqueio permanente.", tentativas_restantes

    # Mensagens padrão para tentativas 1 e 2
    if dados_email['count'] <= 2:
        if dados_email['fase'] == 2:
            return True, "E-mail ou senha inválidos.", tentativas_restantes
        else:
            return True, "E-mail ou senha inválidos.", tentativas_restantes

    return True, "", tentativas_restantes


def resetar_rate_limit(email):
    """
    Reseta o contador de tentativas para um email específico.
    Usado quando o login é bem-sucedido.

    IMPORTANTE: Se o usuário estava na FASE 2, volta para FASE 1 após login bem-sucedido.
    """
    if email in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': time.time(),
            'blocked_until': 0,
            'fase': 1  # Volta para FASE 1 após login bem-sucedido
        }


def bloquear_usuario_permanentemente(email):
    """
    Adiciona um email à lista de bloqueio permanente.
    Usado para bloquear contas comprometidas ou suspeitas.
    """
    usuarios_bloqueados.add(email)


def desbloquear_usuario(email):
    """
    Remove um email da lista de bloqueio permanente.
    Usado para desbloquear contas após verificação de segurança.

    IMPORTANTE: Também reseta o sistema de fases para FASE 1.
    """
    usuarios_bloqueados.discard(email)
    # Reseta o sistema de fases para FASE 1
    if email in rate_limit_attempts:
        rate_limit_attempts[email] = {
            'count': 0,
            'last_attempt': time.time(),
            'blocked_until': 0,
            'fase': 1
        }

# =============================================================================
# FIM DO SISTEMA DE RATE LIMITING
# =============================================================================


CURSOS_PADRAO = [
    "Administração", "Agronomia", "Arquitetura", "Biologia", "Ciência da Computação",
    "Direito", "Educação Física", "Enfermagem", "Engenharia", "Farmácia", "Física",
    "Matemática", "Medicina", "Pedagogia", "Psicologia", "Química", "Sistemas de Informação",
]


HARD_SKILLS_POR_CURSO = {
    "Administração": [
        "Gestão de Pessoas", "Finanças", "Marketing", "Empreendedorismo", "Planejamento Estratégico"
    ],
    "Agronomia": [
        "Manejo de Solo", "Fitotecnia", "Irrigação", "Agroquímica", "Topografia"
    ],
    "Arquitetura": [
        "Desenho Técnico", "AutoCAD", "Maquetes", "Projetos Estruturais", "História da Arquitetura"
    ],
    "Biologia": [
        "Genética", "Microbiologia", "Ecologia", "Botânica", "Zoologia"
    ],
    "Ciência da Computação": [
        "Algoritmos", "Estruturas de Dados", "Programação", "Banco de Dados", "Redes de Computadores"
    ],
    "Direito": [
        "Direito Constitucional", "Direito Civil", "Direito Penal", "Processo Civil", "Processo Penal"
    ],
    "Educação Física": [
        "Fisiologia do Exercício", "Biomecânica", "Treinamento Esportivo", "Avaliação Física", "Primeiros Socorros"
    ],
    "Enfermagem": [
        "Procedimentos de Enfermagem", "Farmacologia", "Saúde Pública", "Cuidados Intensivos", "Primeiros Socorros"
    ],
    "Engenharia": [
        "Cálculo", "Física", "Desenho Técnico", "Materiais de Construção", "Gestão de Projetos"
    ],
    "Farmácia": [
        "Farmacologia", "Análises Clínicas", "Química Farmacêutica", "Microbiologia", "Toxicologia"
    ],
    "Física": [
        "Mecânica", "Eletromagnetismo", "Óptica", "Termodinâmica", "Física Moderna"
    ],
    "Matemática": [
        "Álgebra", "Geometria", "Cálculo", "Estatística", "Matemática Discreta"
    ],
    "Medicina": [
        "Anatomia", "Fisiologia", "Patologia", "Clínica Médica", "Cirurgia"
    ],
    "Pedagogia": [
        "Didática", "Psicologia da Educação", "Planejamento Escolar", "Avaliação Educacional", "Gestão Escolar"
    ],
    "Psicologia": [
        "Psicologia Clínica", "Psicologia Organizacional", "Psicopatologia", "Psicologia do Desenvolvimento", "Psicoterapia"
    ],
    "Química": [
        "Química Orgânica", "Química Inorgânica", "Fisico-Química", "Análises Químicas", "Bioquímica"
    ],
    "Sistemas de Informação": [
        "Java", "Python", "DevOps", "API", "Banco de Dados"
    ]
}


SOFT_SKILLS = [
    "Participação", "Comunicação", "Proatividade",
    "Criatividade", "Trabalho em Equipe"
]


class LogAcesso(db.Model):
    __tablename__ = 'log_acesso'
    id = db.Column(db.Integer, primary_key=True)
    usuario_nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    tipo_usuario = db.Column(db.String(30), nullable=False)
    acao = db.Column(db.String(20), nullable=False)  # login ou logout
    data_hora = db.Column(db.DateTime, default=datetime.now)


class InstituicaodeEnsino(db.Model, UserMixin):
    __tablename__ = 'instituicao_de_ensino'

    id_instituicao = db.Column(db.Integer, primary_key=True)
    nome_instituicao = db.Column(db.String(100), nullable=False)
    endereco_instituicao = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    infraestrutura = db.Column(db.Text, nullable=False)
    nota_mec = db.Column(db.Numeric, nullable=False)
    areas_de_formacao = db.Column(db.Text, nullable=False)
    modalidades = db.Column(db.String(255), nullable=False)
    quantidade_de_alunos = db.Column(db.Integer, nullable=False)
    reitor = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id_instituicao)


class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    id_instituicao = db.Column(db.Integer, db.ForeignKey(
        'instituicao_de_ensino.id_instituicao'), nullable=False)

    instituicao = db.relationship('InstituicaodeEnsino', backref='cursos')


class Aluno(db.Model):
    __tablename__ = 'alunos'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_jovem = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    contato_jovem = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    endereco_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey(
        'instituicao_de_ensino.id_instituicao'))
    curso = db.Column(db.String(255))
    formacao = db.Column(db.String(255))
    periodo = db.Column(db.Integer)
    indicado_por = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'))  # Relacionamento com Chefe

    # Relacionamento reverso
    chefe = db.relationship('Chefe', backref='alunos_indicados')


class Chefe(db.Model, UserMixin):
    __tablename__ = 'chefe'

    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    # Pode ser nulo, mas deve ser único se fornecido
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

    def get_id(self):
        return str(self.id_chefe)


class SkillsDoAluno(db.Model):
    __tablename__ = 'skills_do_aluno'

    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), primary_key=True)
    # Hard skills dinâmicas por curso (JSON)
    hard_skills_json = db.Column(db.Text)
    soft_skills_json = db.Column(db.Text)  # Soft skills detalhadas (JSON)
    aluno = db.relationship(
        'Aluno', backref=db.backref('skills', uselist=False))


class Acompanhamento(db.Model):
    __tablename__ = 'acompanhamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    data_acompanhamento = db.Column(db.DateTime, server_default=db.func.now())

    chefe = db.relationship('Chefe', backref='acompanhamentos')
    aluno = db.relationship('Aluno', backref='acompanhamentos')

    __table_args__ = (db.UniqueConstraint(
        'id_chefe', 'id_aluno', name='uix_chefe_aluno'),)


class SkillsHistorico(db.Model):
    __tablename__ = 'skills_historico'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())
    hard_skills_json = db.Column(db.Text)
    soft_skills_json = db.Column(db.Text)

    aluno = db.relationship('Aluno', backref='historicos')
    chefe = db.relationship('Chefe', backref='historicos')


class Indicacao(db.Model):
    __tablename__ = 'indicacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    data_indicacao = db.Column(db.DateTime, server_default=db.func.now())

    chefe = db.relationship('Chefe', backref='indicacoes')
    aluno = db.relationship('Aluno', backref='indicacoes')

    __table_args__ = (db.UniqueConstraint(
        'id_chefe', 'id_aluno', name='uix_chefe_aluno_indicacao'),)


class TwoFactor(db.Model):
    __tablename__ = 'two_factor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 'chefe' ou 'instituicao'
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    otp_secret = db.Column(db.String(64), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint(
        'user_type', 'user_id', name='uix_2fa_user'),)


class ResetarSenha(db.Model):
    __tablename__ = 'resetar_senha'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    codigo = db.Column(db.String(6), nullable=False)
    # 'chefe' ou 'instituicao'
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    tentativas = db.Column(db.Integer, default=0)


with app.app_context():
    db.create_all()  # Recria as tabelas com base nos modelos
    print("Tabelas recriadas com sucesso!")


@login_manager.user_loader
def load_user(user_id):
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        return Chefe.query.get(int(user_id))
    elif tipo_usuario == 'instituicao':
        return InstituicaodeEnsino.query.get(int(user_id))
    return None


def bloquear_chefe(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'chefe':
            flash("Acesso não permitido para o perfil chefe.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def bloquear_instituicao(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'instituicao':
            flash("Acesso não permitido para o perfil instituição de ensino.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        tipo_usuario = request.form.get('tipo_usuario')
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Validação: senha mínima de 8 caracteres
        if not senha or len(senha) < 8:
            flash('A senha deve ter no mínimo 8 caracteres.', 'danger')
            return redirect(url_for('cadastro'))

        if senha != confirmar_senha:
            flash('As senhas não coincidem!')
            return redirect(url_for('cadastro'))

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
                return redirect(url_for('cadastro'))

            # Validação: não permitir e-mail duplicado
            if InstituicaodeEnsino.query.filter_by(email=email).first():
                flash('Já existe uma instituição cadastrada com este e-mail.', 'danger')
                return redirect(url_for('cadastro'))

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
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou instituição já cadastrados.', 'error')
                return redirect(url_for('cadastro'))

        elif tipo_usuario == 'chefe':
            empresa_nome = request.form.get('empresa_nome')
            cargo = request.form.get('cargo')

            if not nome or not email or not senha or not empresa_nome or not cargo:
                flash('Todos os campos obrigatórios para Chefe devem ser preenchidos!')
                return redirect(url_for('cadastro'))

            # Validação do cargo
            if cargo not in ['CEO', 'Gerente', 'Coordenador']:
                flash('Selecione um cargo válido!', 'danger')
                return redirect(url_for('cadastro'))

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
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou chefe já cadastrados.', 'error')
                return redirect(url_for('cadastro'))

        else:
            flash('Tipo de usuário inválido!')
            return redirect(url_for('cadastro'))

    return render_template('cadastro.html', cursos_padrao=CURSOS_PADRAO)


@app.route('/')
def index():
    return redirect(url_for('carousel'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # =============================================================================
        # OBTÉM DADOS DO USUÁRIO
        # =============================================================================
        email = request.form['email']
        senha = request.form['senha']

        # =============================================================================
        # VERIFICAÇÃO DE BLOQUEIO PERMANENTE
        # =============================================================================
        if email in usuarios_bloqueados:
            flash(
                "Sua conta foi bloqueada permanentemente. Redefina a senha para continuar.", "danger")
            return render_template('login.html')

        # =============================================================================
        # VERIFICAÇÃO DE CREDENCIAIS PRIMEIRO
        # =============================================================================
        chefe = Chefe.query.filter_by(email=email).first()
        instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

        usuario_valido = None
        tipo_usuario = None

        if chefe and check_password_hash(chefe.senha, senha):
            usuario_valido = chefe
            tipo_usuario = 'chefe'
        elif instituicao and check_password_hash(instituicao.senha, senha):
            usuario_valido = instituicao
            tipo_usuario = 'instituicao'

        # =============================================================================
        # LOGIN BEM-SUCEDIDO - RESETA RATE LIMITING
        # =============================================================================
        if usuario_valido:
            # Reseta histórico de tentativas após login correto
            resetar_rate_limit(email)

            # Verifica 2FA
            tf = TwoFactor.query.filter_by(
                user_type=tipo_usuario,
                user_id=usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao,
                enabled=True
            ).first()

            if tf:
                session['pending_user'] = {
                    'tipo': tipo_usuario,
                    'id': usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao
                }
                return redirect(url_for('two_factor_verify'))
            else:
                session['user_id'] = usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao
                session['tipo_usuario'] = tipo_usuario
                login_user(usuario_valido)
                registrar_log(
                    'login',
                    usuario_valido.nome if tipo_usuario == 'chefe' else usuario_valido.nome_instituicao,
                    'chefe' if tipo_usuario == 'chefe' else 'reitor',
                    tipo_usuario
                )
                return redirect(url_for('home'))

        # =============================================================================
        # LOGIN FALHADO - VERIFICA RATE LIMITING E EXIBE MENSAGEM
        # =============================================================================
        # Só verifica rate limiting quando o login falha
        permitido, mensagem_rate_limit, _ = verificar_rate_limit(email)

        if not permitido:
            flash(mensagem_rate_limit, "danger")
        elif mensagem_rate_limit:
            flash(
                f"E-mail ou senha inválidos. {mensagem_rate_limit}", "warning")
        else:
            flash("E-mail ou senha inválidos.", "danger")

    return render_template('login.html')


@app.route('/home')
@login_required
def home():
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        # Renderiza a tela inicial para chefes
        return render_template('home_chefe.html')
    elif tipo_usuario == 'instituicao':
        # Renderiza a tela inicial para instituições de ensino
        return render_template('home_instituicao.html')
    else:
        # Caso o tipo de usuário não seja reconhecido, redireciona para o login
        flash("Tipo de usuário inválido. Faça login novamente.", "danger")
        return redirect(url_for('login'))


@app.route('/instituicaoEnsino')
@bloquear_instituicao
@login_required
def instituicao_ensino():
    # Busca todas as instituições no banco de dados
    instituicoes = InstituicaodeEnsino.query.all()

    # Calcula a quantidade de alunos para cada instituição
    for instituicao in instituicoes:
        instituicao.quantidade_de_alunos = Aluno.query.filter_by(
            id_instituicao=instituicao.id_instituicao).count()

    # Novo: monta um dicionário com os cursos de cada instituição
    cursos_por_instituicao = {
        inst.id_instituicao: [curso.nome for curso in Curso.query.filter_by(
            id_instituicao=inst.id_instituicao).all()]
        for inst in instituicoes
    }

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(instituicoes)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    instituicoes_paginadas = instituicoes[start:end]

    return render_template(
        'instituicaoEnsino.html',
        instituicoes=instituicoes_paginadas,
        cursos_por_instituicao=cursos_por_instituicao,
        page=page,
        total_pages=total_pages
    )


@app.route('/detalhes_instituicao/<int:id_instituicao>')
@login_required
def detalhes_instituicao(id_instituicao):
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    cursos = Curso.query.filter_by(id_instituicao=id_instituicao).all()
    return render_template('detalhes_instituicao.html', instituicao=instituicao, cursos=cursos)


@app.route('/minhas_selecoes')
@bloquear_instituicao
@login_required
def minhas_selecoes():
    if session.get('tipo_usuario') != 'chefe':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    chefe_id = current_user.id_chefe

    # Busca todos os alunos indicados por este chefe usando a tabela Indicacao
    indicacoes = Indicacao.query.filter_by(id_chefe=chefe_id).all()
    alunos = [indicacao.aluno for indicacao in indicacoes]

    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []
        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}

            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "periodo": aluno.periodo,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    return render_template(
        'minhas_selecoes.html',
        alunos=alunos_paginados,
        page=page,
        total_pages=total_pages
    )


@app.route('/remover_indicacao/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def remover_indicacao(id_aluno):
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    aluno = Aluno.query.get_or_404(id_aluno)
    chefe_id = current_user.id_chefe

    # Verifica se o aluno foi indicado pelo chefe logado
    if aluno.indicado_por != chefe_id:
        return jsonify({'error': 'Você não indicou este aluno.'}), 400

    # Remove a indicação
    aluno.indicado_por = None
    db.session.commit()

    return jsonify({'message': 'Indicação removida com sucesso!'}), 200


@app.route('/remover_aluno/<int:id_aluno>', methods=['POST'])
@login_required
def remover_aluno(id_aluno):
    aluno = Aluno.query.get_or_404(id_aluno)

    try:
        # Decrementar a quantidade de alunos na instituição
        instituicao = InstituicaodeEnsino.query.get(aluno.id_instituicao)
        instituicao.quantidade_de_alunos -= 1

        # Remover o aluno
        db.session.delete(aluno)
        db.session.commit()

        flash("Aluno removido com sucesso!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Erro ao remover aluno.", "danger")

    return redirect(url_for('alunos_instituicao'))


@app.route('/ver_alunos_por_curso', methods=['GET'])
@bloquear_instituicao
@login_required
def ver_alunos_por_curso():
    inst_id = request.args.get('inst_id')
    curso = request.args.get('curso')
    filtro_tipo = request.args.get('filtro_tipo')
    periodo = request.args.get('periodo')
    habilidade = request.args.getlist('habilidade')  # <-- sempre retorna lista

    # Decodificar o parâmetro 'curso' para evitar problemas com caracteres especiais
    curso = unquote(curso).strip()
    curso_normalizado = unidecode(curso).lower()

    alunos = Aluno.query.filter(
        Aluno.id_instituicao == inst_id
    ).all()

    alunos_filtrados = [
        aluno for aluno in alunos
        if unidecode(aluno.curso).lower() == curso_normalizado
    ]

    # Filtro por período
    if periodo and periodo.isdigit():
        alunos_filtrados = [
            aluno for aluno in alunos_filtrados if str(aluno.periodo) == periodo]

    # Ordenação por múltiplas habilidades (hard e soft)
    if habilidade:
        def get_total_skills(aluno):
            skills = aluno.skills
            total = 0
            if skills:
                hard_dict = json.loads(
                    skills.hard_skills_json) if skills.hard_skills_json else {}
                soft_dict = json.loads(
                    skills.soft_skills_json) if skills.soft_skills_json else {}
                for hab in habilidade:
                    if ':' in hab:
                        tipo, nome = hab.split(':', 1)
                        if tipo == 'hard':
                            total += hard_dict.get(nome, 0)
                        elif tipo == 'soft':
                            total += soft_dict.get(nome, 0)
            return total
        alunos_filtrados = sorted(
            alunos_filtrados, key=get_total_skills, reverse=True)

    alunos_com_skills = []
    for aluno in alunos_filtrados:
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []
        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}

            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "periodo": aluno.periodo,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })

    mensagem = None
    if not alunos_filtrados:
        if periodo and periodo.isdigit():
            mensagem = f"Nenhum aluno encontrado para o período '{periodo}' no curso '{curso}'."
        else:
            mensagem = f"Nenhum aluno encontrado para o curso '{curso}'."

    # PAGINAÇÃO
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    return render_template(
        'cardAlunos.html',
        alunos=alunos_paginados,
        curso=curso,
        mensagem=mensagem,
        page=page,
        total_pages=total_pages,
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS
    )


@app.route('/detalhes_aluno/<int:id_aluno>')
@bloquear_instituicao
@login_required
def detalhes_aluno(id_aluno):
    aluno = Aluno.query.filter_by(id_aluno=id_aluno).first()
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('alunos'))

    previous_url = request.args.get('previous', url_for('instituicao_ensino'))

    hard_labels, hard_values = [], []
    soft_labels, soft_values = [], []
    if aluno.skills:
        import json
        hard_dict = json.loads(
            aluno.skills.hard_skills_json) if aluno.skills.hard_skills_json else {}
        soft_dict = json.loads(
            aluno.skills.soft_skills_json) if aluno.skills.soft_skills_json else {}
        hard_labels = list(hard_dict.keys())
        hard_values = list(hard_dict.values())
        soft_labels = list(soft_dict.keys())
        soft_values = list(soft_dict.values())

    return render_template(
        'detalhes_aluno.html',
        aluno=aluno,
        hard_labels=hard_labels,
        hard_values=hard_values,
        soft_labels=soft_labels,
        soft_values=soft_values,
        previous_url=previous_url
    )


@app.route('/indicar_aluno/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def indicar_aluno(id_aluno):
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    chefe_id = current_user.id_chefe

    # Verifica se já existe indicação deste chefe para este aluno
    ja_indicado = Indicacao.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno).first()
    if ja_indicado:
        return jsonify({'error': 'Você já indicou este aluno.'}), 400

    nova_indicacao = Indicacao(id_chefe=chefe_id, id_aluno=id_aluno)
    db.session.add(nova_indicacao)
    db.session.commit()

    return jsonify({'message': 'Aluno indicado com sucesso!'}), 200


@app.route('/carousel')
def carousel():
    return render_template('carousel.html')


@app.route('/cursos', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def cursos():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        nome_curso = request.form.get('curso')
        if nome_curso:
            # Verifica se já existe para esta instituição
            ja_existe = Curso.query.filter_by(
                nome=nome_curso,
                id_instituicao=current_user.id_instituicao
            ).first()
            if ja_existe:
                flash('Este curso já foi cadastrado!', 'warning')
            else:
                novo_curso = Curso(
                    nome=nome_curso, id_instituicao=current_user.id_instituicao)
                db.session.add(novo_curso)
                db.session.commit()
                flash('Curso cadastrado com sucesso!', 'success')
        return redirect(url_for('cursos'))

    cursos = Curso.query.filter_by(
        id_instituicao=current_user.id_instituicao).all()
    return render_template('cursos.html', cursos=cursos, CURSOS_PADRAO=CURSOS_PADRAO)


def validar_skills_por_curso(curso, hard_skills_dict, soft_skills_dict):
    # Curso deve ser válido
    if curso not in HARD_SKILLS_POR_CURSO:
        return False, f"Curso '{curso}' não é permitido."
    # Hard skills: 5, nomes exatos, valores entre 0 e 10
    hard_labels = HARD_SKILLS_POR_CURSO[curso]
    if set(hard_skills_dict.keys()) != set(hard_labels):
        return False, f"As hard skills devem ser exatamente: {', '.join(hard_labels)}."
    for valor in hard_skills_dict.values():
        if not isinstance(valor, int) or valor < 0 or valor > 10:
            return False, "Todas as hard skills devem ser números inteiros de 0 a 10."
    # Soft skills: 5, nomes exatos, valores entre 0 e 10
    if set(soft_skills_dict.keys()) != set(SOFT_SKILLS):
        return False, f"As soft skills devem ser exatamente: {', '.join(SOFT_SKILLS)}."
    for valor in soft_skills_dict.values():
        if not isinstance(valor, int) or valor < 0 or valor > 10:
            return False, "Todas as soft skills devem ser números inteiros de 0 a 10."
    return True, ""


@app.route('/cadastrar_aluno', methods=['POST'])
@login_required
@bloquear_chefe
def cadastrar_aluno():
    nome_jovem = request.form.get('nome_jovem', '').strip()
    data_nascimento = request.form.get('data_nascimento', '').strip()
    contato_jovem = request.form.get('contato_jovem', '').strip()
    email = request.form.get('email', '').strip()
    endereco_jovem = request.form.get('endereco_jovem', '').strip()
    curso = request.form.get('curso', '').strip()
    formacao = request.form.get('formacao', '').strip()
    periodo = request.form.get('periodo', '').strip()

    # Validação do e-mail duplicado
    if Aluno.query.filter_by(email=email).first():
        flash("Já existe um aluno cadastrado com este e-mail.", "danger")
        return redirect(url_for('alunos_instituicao'))

    # Validação dos campos obrigatórios
    if not nome_jovem or not data_nascimento or not endereco_jovem or not contato_jovem or not email or not curso or not formacao or not periodo:
        flash("Preencha todos os campos obrigatórios!", "error")
        return redirect(url_for('alunos_instituicao'))

    # Validação do e-mail
    if '@' not in email or '.' not in email:
        flash("E-mail inválido!", "danger")
        return redirect(url_for('alunos_instituicao'))

    # Validação do período (agora obrigatório)
    if not periodo.isdigit() or int(periodo) < 1 or int(periodo) > 20:
        flash("Período deve ser um número entre 1 e 20.", "danger")
        return redirect(url_for('alunos_instituicao'))

    # Validação do contato (exemplo simples, pode ser melhorado)
    if not contato_jovem.isdigit() or len(contato_jovem) < 8:
        flash("Contato deve conter apenas números e ter pelo menos 11 dígitos.", "danger")
        return redirect(url_for('alunos_instituicao'))

    # Validação das hard skills
    hard_skills_dict = {}
    for label in HARD_SKILLS_POR_CURSO.get(curso, []):
        field_name = f"hard_{label.lower().replace(' ', '_')}"
        valor = request.form.get(field_name)
        if valor is None or not valor.isdigit() or int(valor) < 0 or int(valor) > 10:
            flash(
                f"Preencha corretamente a hard skill '{label}' (0 a 10).", "danger")
            return redirect(url_for('alunos_instituicao'))
        hard_skills_dict[label] = int(valor)

    # Validação das soft skills
    soft_skills_dict = {}
    for label in SOFT_SKILLS:
        field_name = label.lower().replace(' ', '_')
        valor = request.form.get(field_name)
        if valor is None or not valor.isdigit() or int(valor) < 0 or int(valor) > 10:
            flash(
                f"Preencha corretamente a soft skill '{label}' (0 a 10).", "danger")
            return redirect(url_for('alunos_instituicao'))
        soft_skills_dict[label] = int(valor)

    try:
        novo_aluno = Aluno(
            nome_jovem=nome_jovem,
            data_nascimento=data_nascimento,
            contato_jovem=contato_jovem,
            email=email,
            endereco_jovem=endereco_jovem,
            id_instituicao=current_user.id_instituicao,
            curso=curso,
            formacao=formacao,
            periodo=periodo
        )
        db.session.add(novo_aluno)
        db.session.commit()

        skills = SkillsDoAluno(
            id_aluno=novo_aluno.id_aluno,
            hard_skills_json=json.dumps(hard_skills_dict),
            soft_skills_json=json.dumps(soft_skills_dict),
        )
        db.session.add(skills)
        db.session.commit()

        instituicao = InstituicaodeEnsino.query.get(
            current_user.id_instituicao)
        instituicao.quantidade_de_alunos += 1
        db.session.commit()

        flash("Aluno cadastrado com sucesso!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Erro inesperado ao cadastrar aluno. Tente novamente.", "danger")

    return redirect(url_for('alunos_instituicao'))


@app.route('/alunos_instituicao', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def alunos_instituicao():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    instituicao_id = current_user.id_instituicao

    cursos_disponiveis = [curso.nome for curso in Curso.query.filter_by(
        id_instituicao=instituicao_id).all()]
    # Usa os cursos disponíveis da instituição em vez de apenas os que têm alunos
    cursos = cursos_disponiveis

    filtro_curso = request.form.get(
        'curso') if request.method == 'POST' else None

    if filtro_curso:
        alunos = Aluno.query.filter_by(
            id_instituicao=instituicao_id, curso=filtro_curso).all()
    else:
        alunos = Aluno.query.filter_by(id_instituicao=instituicao_id).all()

    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        # Parse JSONs
        hard_skills = []
        hard_labels = []
        soft_skills = []
        soft_labels = []
        if skills:
            import json
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}

            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "periodo": aluno.periodo,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })

    # PAGINAÇÃO
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    return render_template(
        'alunos_instituicao.html',
        alunos=alunos_paginados,
        cursos=cursos,
        filtro_curso=filtro_curso,
        cursos_disponiveis=cursos_disponiveis,
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS,
        page=page,
        total_pages=total_pages
    )


@app.route('/detalhes_aluno_instituicao/<int:id_aluno>', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def detalhes_aluno_instituicao(id_aluno):
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    aluno = Aluno.query.get_or_404(id_aluno)
    cursos_disponiveis = [curso.nome for curso in Curso.query.filter_by(
        id_instituicao=aluno.id_instituicao).all()]

    # Pegue as listas para o formulário
    hard_labels = HARD_SKILLS_POR_CURSO.get(aluno.curso, [])
    soft_labels = SOFT_SKILLS

    # Carregue os valores atuais
    skills = aluno.skills
    hard_dict = {}
    soft_dict = {}
    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}

    if request.method == 'POST':
        # Validação do curso
        curso = request.form['curso']
        if curso not in cursos_disponiveis:
            flash("Curso inválido para esta instituição!", "danger")
            return redirect(request.url)

        # Validação dos campos obrigatórios
        nome_jovem = request.form.get('nome_jovem', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        contato_jovem = request.form.get('contato_jovem', '').strip()
        email = request.form.get('email', '').strip()
        endereco_jovem = request.form.get('endereco_jovem', '').strip()
        formacao = request.form.get('formacao', '').strip()
        periodo = request.form.get('periodo', '').strip()

        # Verifica se já existe outro aluno com este e-mail
        email_existente = Aluno.query.filter(
            Aluno.email == email, Aluno.id_aluno != aluno.id_aluno).first()
        if email_existente:
            flash("Já existe um aluno cadastrado com este e-mail.", "danger")

        if not nome_jovem or not data_nascimento or not contato_jovem or not email or not endereco_jovem or not formacao or not periodo:
            flash("Preencha todos os campos obrigatórios!", "danger")
            return redirect(request.url)

        # Validação do e-mail
        if '@' not in email or '.' not in email:
            flash("E-mail inválido!", "danger")
            return redirect(request.url)

        # Validação do contato
        if not contato_jovem.isdigit() or len(contato_jovem) < 8:
            flash(
                "Contato deve conter apenas números e ter pelo menos 11 dígitos.", "danger")
            return redirect(request.url)

        # Validação do período
        if not periodo.isdigit() or int(periodo) < 1 or int(periodo) > 20:
            flash("Período deve ser um número inteiro entre 1 e 20.", "danger")
            return redirect(request.url)

        # Atualizar informações do aluno
        aluno.nome_jovem = nome_jovem
        aluno.data_nascimento = data_nascimento
        aluno.contato_jovem = contato_jovem
        aluno.email = email
        aluno.endereco_jovem = endereco_jovem
        aluno.curso = curso
        aluno.formacao = formacao
        aluno.periodo = periodo

        # Atualizar hard skills (dinâmico conforme curso)
        hard_labels = HARD_SKILLS_POR_CURSO.get(curso, [])
        new_hard_dict = {}
        for label in hard_labels:
            field_name = f"hard_{label.lower().replace(' ', '_')}"
            valor = request.form.get(field_name)
            if valor is None or valor == '':
                flash(f"Preencha a pontuação de '{label}'!", "danger")
                return redirect(request.url)
            try:
                new_hard_dict[label] = int(valor)
            except ValueError:
                flash(f"Valor inválido para '{label}'.", "danger")
                return redirect(request.url)

        # Atualizar soft skills (fixo)
        new_soft_dict = {}
        for label in SOFT_SKILLS:
            field_name = label.lower().replace(' ', '_')
            valor = request.form.get(field_name)
            if valor is None or valor == '':
                flash(f"Preencha a pontuação de '{label}'!", "danger")
                return redirect(request.url)
            try:
                new_soft_dict[label] = int(valor)
            except ValueError:
                flash(f"Valor inválido para '{label}'.", "danger")
                return redirect(request.url)

        # Atualiza ou cria o registro de skills
        if not skills:
            skills = SkillsDoAluno(id_aluno=aluno.id_aluno)
            db.session.add(skills)
        skills.hard_skills_json = json.dumps(new_hard_dict)
        skills.soft_skills_json = json.dumps(new_soft_dict)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Já existe um aluno cadastrado com este e-mail.", "danger")
            return redirect(request.url)

        # Salvar histórico das skills após atualizar para todos os chefes que acompanham este aluno
        try:
            acompanhamentos = Acompanhamento.query.filter_by(
                id_aluno=aluno.id_aluno).all()
            fuso_brasil = pytz.timezone('America/Recife')
            data_atualizacao = datetime.now(fuso_brasil)
            for ac in acompanhamentos:
                novo_historico = SkillsHistorico(
                    id_aluno=aluno.id_aluno,
                    id_chefe=ac.id_chefe,
                    hard_skills_json=json.dumps(new_hard_dict),
                    soft_skills_json=json.dumps(new_soft_dict),
                    data=data_atualizacao
                )
                db.session.add(novo_historico)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Erro ao salvar histórico das skills.", "danger")

        flash("Informações do aluno atualizadas com sucesso!", "success")
        return redirect(url_for('detalhes_aluno_instituicao', id_aluno=id_aluno))

    return render_template(
        'detalhes_aluno_instituicao.html',
        aluno=aluno,
        cursos_disponiveis=cursos_disponiveis,
        hard_labels=hard_labels,
        soft_labels=soft_labels,
        hard_dict=hard_dict,
        soft_dict=soft_dict,
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS
    )


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    tipo_usuario = session.get('tipo_usuario')

    if request.method == 'POST':
        # Atualizar informações do chefe
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get_or_404(current_user.id_chefe)
            nome = request.form['nome'].strip()
            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', nome):
                flash(
                    "O nome deve ter entre 2 e 30 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))

            novo_email = request.form['email']
            email_existente = Chefe.query.filter(
                Chefe.email == novo_email, Chefe.id_chefe != chefe.id_chefe).first()
            if email_existente:
                flash("Já existe um chefe cadastrado com este e-mail.", "danger")
                return redirect(url_for('perfil'))
            chefe.nome = request.form['nome']
            cargo = request.form['cargo']
            if cargo not in ['CEO', 'Gerente', 'Coordenador']:
                flash("Selecione um cargo válido.", "danger")
                return redirect(url_for('perfil'))
            chefe.cargo = cargo
            chefe.nome_empresa = request.form.get('nome_empresa')
            chefe.email = novo_email
            senha_nova = request.form.get('senha', '')
            if senha_nova:
                if len(senha_nova) < 8:
                    flash("A senha deve ter no mínimo 8 caracteres.", "danger")
                    return redirect(url_for('perfil'))
                chefe.senha = generate_password_hash(senha_nova)
            try:
                db.session.commit()
                flash("Perfil atualizado com sucesso!", "success")
                return redirect(url_for('perfil'))
            except IntegrityError:
                db.session.rollback()
                flash("Já existe um chefe cadastrado com este e-mail.", "danger")
                return redirect(url_for('perfil'))

        # Atualizar informações da instituição
        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get_or_404(
                current_user.id_instituicao)
            nome_instituicao = request.form['nome_instituicao'].strip()
            reitor = request.form['reitor'].strip()

            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,50}$', nome_instituicao):
                flash(
                    "O nome da instituição deve ter entre 2 e 50 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))
            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', reitor):
                flash(
                    "O nome do reitor deve ter entre 2 e 30 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))

            novo_email = request.form['email']
            email_existente = InstituicaodeEnsino.query.filter(
                InstituicaodeEnsino.email == novo_email,
                InstituicaodeEnsino.id_instituicao != instituicao.id_instituicao
            ).first()
            if email_existente:
                flash("Já existe uma instituição cadastrada com este e-mail.", "danger")
                return redirect(url_for('perfil'))
            instituicao.nome_instituicao = request.form['nome_instituicao']
            instituicao.endereco_instituicao = request.form['endereco_instituicao']
            instituicao.reitor = request.form['reitor']
            instituicao.infraestrutura = request.form['infraestrutura']

            nota_mec = request.form['nota_mec']
            if nota_mec not in ['1', '2', '3', '4', '5']:
                flash("Nota MEC deve ser um valor entre 1 e 5.", "danger")
                return redirect(url_for('perfil'))
            instituicao.nota_mec = int(nota_mec)

            modalidades = request.form['modalidades']
            if modalidades not in ['Presencial', 'Hibrido', 'EAD']:
                flash("Selecione uma modalidade válida.", "danger")
                return redirect(url_for('perfil'))
            instituicao.modalidades = modalidades

            instituicao.email = novo_email
            senha_nova = request.form.get('senha', '')
            if senha_nova:
                if len(senha_nova) < 8:
                    flash("A senha deve ter no mínimo 8 caracteres.", "danger")
                    return redirect(url_for('perfil'))
                instituicao.senha = generate_password_hash(senha_nova)
            try:
                db.session.commit()
                flash("Perfil atualizado com sucesso!", "success")
                return redirect(url_for('perfil'))
            except IntegrityError:
                db.session.rollback()
                flash("Já existe uma instituição cadastrada com este e-mail.", "danger")
                return redirect(url_for('perfil'))

    # Exibir informações do perfil
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = Curso.query.filter_by(
            id_instituicao=current_user.id_instituicao).all()
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('home'))

    return render_template('perfil.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao)


@app.route('/acompanhar_aluno/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def acompanhar_aluno(id_aluno):
    chefe_id = current_user.id_chefe

    # Verifica se já está acompanhando
    acompanhamento = Acompanhamento.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno).first()
    if acompanhamento:
        return jsonify({'error': 'Você já está acompanhando este aluno.'}), 400

    novo_acompanhamento = Acompanhamento(id_chefe=chefe_id, id_aluno=id_aluno)
    db.session.add(novo_acompanhamento)
    db.session.commit()

    # Cria snapshot das skills no momento do acompanhamento, se não existir para este chefe
    historico_existente = SkillsHistorico.query.filter_by(
        id_aluno=id_aluno, id_chefe=chefe_id).count()
    aluno = Aluno.query.get(id_aluno)
    if aluno and aluno.skills and historico_existente == 0:
        novo_historico = SkillsHistorico(
            id_aluno=aluno.id_aluno,
            id_chefe=chefe_id,  # Salva o chefe responsável pelo snapshot
            hard_skills_json=aluno.skills.hard_skills_json,
            soft_skills_json=aluno.skills.soft_skills_json
        )
        db.session.add(novo_historico)
        db.session.commit()
    # -------------------------------------------------------------------------------

    return jsonify({'message': 'Aluno adicionado à sua lista de acompanhamento!'})


@app.route('/acompanhar')
@login_required
@bloquear_instituicao
def acompanhar():
    chefe_id = current_user.id_chefe
    acompanhamentos = Acompanhamento.query.filter_by(id_chefe=chefe_id).all()
    alunos_com_skills = []
    for ac in acompanhamentos:
        aluno = ac.aluno
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []
        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}

            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome_jovem": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    return render_template(
        'acompanhar.html',
        alunos=alunos_paginados,
        page=page,
        total_pages=total_pages
    )


@app.route('/remover_acompanhamento/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def remover_acompanhamento(id_aluno):
    print(f"DEBUG: Removendo acompanhamento do aluno {id_aluno}")  # Debug log
    chefe_id = current_user.id_chefe
    ac = Acompanhamento.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno).first()
    if ac:
        db.session.delete(ac)
        db.session.commit()
        print("DEBUG: Aluno removido com sucesso")  # Debug log
        flash("Aluno removido do acompanhamento.", "success")
    else:
        print("DEBUG: Acompanhamento não encontrado")  # Debug log
        flash("Acompanhamento não encontrado.", "danger")
    return redirect(url_for('acompanhar'))


@app.route('/status_aluno/<int:id_aluno>')
@login_required
@bloquear_instituicao
def status_aluno(id_aluno):
    chefe_id = current_user.id_chefe
    historicos = SkillsHistorico.query.filter_by(
        id_aluno=id_aluno, id_chefe=chefe_id).order_by(SkillsHistorico.data.desc()).all()
    aluno = Aluno.query.get_or_404(id_aluno)
    historicos_dict = []
    fuso_brasil = pytz.timezone('America/Recife')
    for hist in historicos:
        # Converte para o fuso de Recife se não tiver tzinfo
        data_brasil = hist.data
        if data_brasil and data_brasil.tzinfo is None:
            data_brasil = pytz.utc.localize(
                data_brasil).astimezone(fuso_brasil)
        elif data_brasil:
            data_brasil = data_brasil.astimezone(fuso_brasil)
        hard = json.loads(
            hist.hard_skills_json) if hist.hard_skills_json else {}
        soft = json.loads(
            hist.soft_skills_json) if hist.soft_skills_json else {}
        historicos_dict.append({
            'data': data_brasil,
            'hard_skills': hard,
            'soft_skills': soft
        })
    # Gera pares para comparação de evolução
    historico_pares = []
    if len(historicos_dict) > 1:
        for i in range(len(historicos_dict) - 1):
            atual = historicos_dict[i]
            anterior = historicos_dict[i + 1]
            historico_pares.append({
                'data': atual['data'],
                'atual': atual,
                'anterior': anterior
            })
    elif len(historicos_dict) == 1:
        historico_pares.append({
            'data': historicos_dict[0]['data'],
            'atual': historicos_dict[0],
            'anterior': None
        })
    return render_template('status_aluno.html', historicos=historicos_dict, historico_pares=historico_pares, aluno=aluno)


@app.route('/alunos_indicados')
@bloquear_chefe
@login_required
def alunos_indicados():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    instituicao_id = current_user.id_instituicao

    # Busca todos os alunos da instituição que possuem pelo menos uma indicação
    alunos = Aluno.query.filter_by(id_instituicao=instituicao_id).all()
    dados_alunos = []
    for aluno in alunos:
        for indicacao in aluno.indicacoes:
            chefe = indicacao.chefe
            dados_alunos.append({
                "id_aluno": aluno.id_aluno,
                "nome": aluno.nome_jovem,
                "curso": aluno.curso,
                "periodo": aluno.periodo,
                "chefe_nome": chefe.nome if chefe else 'Não informado',
                "chefe_empresa": chefe.nome_empresa if chefe else 'Não informado',
                "data_indicacao": indicacao.data_indicacao.strftime('%d/%m/%Y') if indicacao.data_indicacao else 'Sem data'
            })

    # Paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(dados_alunos)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = dados_alunos[start:end]

    return render_template(
        'alunos_indicados.html',
        alunos=alunos_paginados,
        page=page,
        total_pages=total_pages
    )


@app.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = Curso.query.filter_by(
            id_instituicao=current_user.id_instituicao).all()
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('home'))

    # Verificar se 2FA está ativo
    tf_enabled = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id, enabled=True).first() is not None

    return render_template('configuracoes.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao, two_factor_enabled=tf_enabled)


def _get_or_create_2fa_record(tipo_usuario, user_id):
    tf = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id).first()
    if not tf:
        tf = TwoFactor(user_type=tipo_usuario, user_id=user_id,
                       otp_secret=pyotp.random_base32(), enabled=False)
        db.session.add(tf)
        db.session.commit()
    return tf


def _generate_qr_data_uri(issuer, account_name, secret):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=issuer)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{data}", uri


@app.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        account_name = usuario.email or usuario.nome
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        account_name = usuario.email or usuario.nome_instituicao
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('home'))

    tf = _get_or_create_2fa_record(tipo_usuario, user_id)
    qr_data_uri, otpauth_uri = _generate_qr_data_uri(
        'DashTalent', account_name, tf.otp_secret)

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        totp = pyotp.TOTP(tf.otp_secret)
        if totp.verify(code, valid_window=1):
            tf.enabled = True
            db.session.commit()
            flash('Autenticação de dois fatores ativada com sucesso.', 'success')
            return redirect(url_for('configuracoes'))
        else:
            flash('Código inválido. Tente novamente.', 'danger')

    return render_template('2fa_setup.html', qr_data_uri=qr_data_uri, otpauth_uri=otpauth_uri, secret=tf.otp_secret)


@app.route('/2fa/verify', methods=['GET', 'POST'])
def two_factor_verify():
    pending = session.get('pending_user')
    if not pending:
        return redirect(url_for('login'))

    tipo = pending.get('tipo')
    user_id = pending.get('id')
    tf = TwoFactor.query.filter_by(
        user_type=tipo, user_id=user_id, enabled=True).first()
    if not tf:
        # Se não há 2FA ativo, volte ao login
        session.pop('pending_user', None)
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        totp = pyotp.TOTP(tf.otp_secret)
        if totp.verify(code, valid_window=1):
            # Completa o login
            if tipo == 'chefe':
                user = Chefe.query.get_or_404(user_id)
                session['user_id'] = user.id_chefe
                session['tipo_usuario'] = 'chefe'
                login_user(user)
                registrar_log('login', user.nome, user.cargo, 'chefe')
            elif tipo == 'instituicao':
                user = InstituicaodeEnsino.query.get_or_404(user_id)
                session['user_id'] = user.id_instituicao
                session['tipo_usuario'] = 'instituicao'
                login_user(user)
                registrar_log('login', user.nome_instituicao,
                              'reitor', 'instituicao')

            # Reseta histórico de tentativas após login bem-sucedido com 2FA
            # Obtém o email do usuário para resetar o rate limiting
            if tipo == 'chefe':
                email_usuario = user.email
            else:
                email_usuario = user.email
            resetar_rate_limit(email_usuario)

            session.pop('pending_user', None)
            return redirect(url_for('home'))
        else:
            flash('Código 2FA inválido.', 'danger')

    return render_template('2fa_verify.html')


@app.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def two_factor_disable():
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('home'))

    tf = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id, enabled=True).first()
    if not tf:
        flash("2FA não está ativo para esta conta.", "warning")
        return redirect(url_for('configuracoes'))

    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '').strip()
        codigo_2fa = request.form.get('codigo_2fa', '').strip()

        # Verificar senha atual
        if not check_password_hash(usuario.senha, senha_atual):
            flash('Senha atual incorreta.', 'danger')
            return render_template('2fa_disable.html')

        # Verificar código 2FA
        totp = pyotp.TOTP(tf.otp_secret)
        if not totp.verify(codigo_2fa, valid_window=1):
            flash('Código 2FA inválido.', 'danger')
            return render_template('2fa_disable.html')

        # Desativar 2FA
        tf.enabled = False
        db.session.commit()

        # Log de auditoria
        if tipo_usuario == 'chefe':
            registrar_log('2fa_disable', usuario.nome, usuario.cargo, 'chefe')
        else:
            registrar_log('2fa_disable', usuario.nome_instituicao,
                          'reitor', 'instituicao')

        flash('2FA desativado com sucesso.', 'success')
        return redirect(url_for('configuracoes'))

    return render_template('2fa_disable.html')


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


@app.route('/logout', methods=['POST'])
def logout():

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
    return redirect(url_for('login'))


# ================================
# Implementação da mudança solicitada:
# Proteção CSRF + endurecimento de cookies de sessão
# Observação: Ajuste as flags `secure=True` em produção com HTTPS
# ================================
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # Ajuste para True em produção com HTTPS
)


@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)


@app.after_request
def set_csrf_cookie(response):
    try:
        csrf_token_value = generate_csrf()
        response.set_cookie(
            "csrf_token",
            csrf_token_value,
            secure=False,  # Ajuste para True em produção com HTTPS
            samesite="Lax",
            path="/"
        )
    except Exception:
        pass
    return response


def gerar_codigo_verificacao():
    """Gera um código de 6 dígitos para verificação"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def enviar_email(email_destino, assunto, corpo):
    """Função genérica e segura para envio de emails"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not smtp_user or not smtp_password:
            raise RuntimeError("Credenciais SMTP não configuradas no .env")

        # Montar mensagem
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email_destino
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return True, "Email enviado com sucesso"

    except Exception as e:
        print(f"[ERRO SMTP] {e}")
        return False, f"Erro ao enviar email: {str(e)}"


@app.route('/esqueceu-senha', methods=['GET', 'POST'])
def esqueceu_senha():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if not email:
            flash("Por favor, informe seu email.", "danger")
            return render_template('esqueceu_senha.html')

        # Verificar se o email existe (chefe ou instituição)
        chefe = Chefe.query.filter_by(email=email).first()
        instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

        if not chefe and not instituicao:
            flash("Email não cadastrado no sistema.", "danger")
            return render_template('esqueceu_senha.html')

        # Rate limiting - verificar se já foi enviado código recentemente
        codigo_recente = ResetarSenha.query.filter_by(
            email=email,
            used=False
        ).filter(ResetarSenha.created_at > datetime.now() - timedelta(minutes=2)).first()

        if codigo_recente:
            flash("Um código já foi enviado recentemente. Aguarde 2 minutos.", "warning")
            return render_template('esqueceu_senha.html')

        # Gerar código de 6 dígitos
        codigo = ''.join(secrets.choice(string.digits) for _ in range(6))

        # Determinar tipo de usuário e ID
        if chefe:
            user_type = 'chefe'
            user_id = chefe.id_chefe
            nome_usuario = chefe.nome
        else:
            user_type = 'instituicao'
            user_id = instituicao.id_instituicao
            nome_usuario = instituicao.nome_instituicao

        # Salvar no banco
        reset_request = ResetarSenha(
            email=email,
            codigo=codigo,
            user_type=user_type,
            user_id=user_id,
            created_at=datetime.now()
        )

        db.session.add(reset_request)
        db.session.commit()

        # Enviar email real
        corpo = f"""
        Olá {nome_usuario},

        Você solicitou a recuperação de senha no DashTalent.
        Seu código de verificação é: {codigo}

        Este código expira em 10 minutos.
        Se você não solicitou esta recuperação, ignore este email.

        Atenciosamente,
        Equipe DashTalent
        """

        ok, msg = enviar_email(
            email, "Código de Recuperação de Senha - DashTalent", corpo)

        if ok:
            flash("Código de verificação enviado para seu email.", "success")
            return redirect(url_for('verificar_codigo', email=email))
        else:
            flash(msg, "danger")
            return render_template('esqueceu_senha.html')

    return render_template('esqueceu_senha.html')


@app.route('/verificar-codigo')
def verificar_codigo():
    email = request.args.get('email')
    if not email:
        return redirect(url_for('esqueceu_senha'))
    return render_template('verificar_codigo.html', email=email)


@app.route('/verificar-codigo', methods=['POST'])
def verificar_codigo_post():
    email = request.form['email']
    codigo = request.form['codigo']

    if not email or not codigo:
        flash("Email e código são obrigatórios.", "danger")
        return render_template('verificar_codigo.html', email=email)

    # Buscar todos os códigos válidos para o email (não usados e dentro do prazo)
    reset_requests = ResetarSenha.query.filter_by(
        email=email,
        used=False
    ).filter(ResetarSenha.created_at > datetime.now() - timedelta(minutes=10)).all()

    if not reset_requests:
        flash("Código inválido ou expirado.", "danger")
        return render_template('verificar_codigo.html', email=email)

    # Procurar o código digitado entre os códigos válidos
    reset_request = None
    for rr in reset_requests:
        if rr.codigo == codigo:
            reset_request = rr
            break

    # Se não encontrou o código correto, incrementar tentativas no código mais recente
    if not reset_request:
        # Pega o código mais recente para incrementar tentativas
        reset_request = max(reset_requests, key=lambda r: r.created_at)
        reset_request.tentativas += 1
        db.session.commit()

        if reset_request.tentativas >= 3:
            flash("Muitas tentativas. Solicite um novo código.", "danger")
            return redirect(url_for('esqueceu_senha'))
        else:
            flash("Código incorreto.", "danger")
            return render_template('verificar_codigo.html', email=email)

    # Código correto encontrado - verificar tentativas
    if reset_request.tentativas >= 3:
        flash("Muitas tentativas. Solicite um novo código.", "danger")
        return redirect(url_for('esqueceu_senha'))

    # Código correto e tentativas < 3 - sucesso
    session['reset_token'] = reset_request.id
    flash("Código verificado com sucesso!", "success")
    return redirect(url_for('nova_senha'))


@app.route('/nova-senha', methods=['GET', 'POST'])
def nova_senha():
    if 'reset_token' not in session:
        flash("Sessão inválida. Inicie o processo novamente.", "danger")
        return redirect(url_for('esqueceu_senha'))

    reset_request = ResetarSenha.query.get(session['reset_token'])
    if not reset_request or reset_request.used:
        flash("Token inválido ou já utilizado.", "danger")
        session.pop('reset_token', None)
        return redirect(url_for('esqueceu_senha'))

    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        # Validações
        if not nova_senha or not confirmar_senha:
            flash("Todos os campos são obrigatórios.", "danger")
            return render_template('nova_senha.html')

        if len(nova_senha) < 6:
            flash("A senha deve ter pelo menos 6 caracteres.", "danger")
            return render_template('nova_senha.html')

        if nova_senha != confirmar_senha:
            flash("As senhas não coincidem.", "danger")
            return render_template('nova_senha.html')

        # Atualizar senha do usuário
        senha_hash = generate_password_hash(nova_senha)

        try:
            if reset_request.user_type == 'chefe':
                user = Chefe.query.get(reset_request.user_id)
                user.senha = senha_hash
            else:
                user = InstituicaodeEnsino.query.get(reset_request.user_id)
                user.senha = senha_hash

            # Marcar código como usado
            reset_request.used = True

            db.session.commit()
            session.pop('reset_token', None)

            # Liberar usuário do bloqueio permanente e resetar para FASE 1
            desbloquear_usuario(reset_request.email)

            flash("Senha alterada com sucesso! Faça login com sua nova senha.", "success")
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash("Erro ao alterar senha. Tente novamente.", "danger")

    return render_template('nova_senha.html')


# =============================================================================
# ROTAS ADMINISTRATIVAS PARA GERENCIAMENTO DE BLOQUEIOS
# =============================================================================
# Estas rotas são apenas para demonstração e devem ser protegidas adequadamente
# em um ambiente de produção

@app.route('/admin/bloquear-usuario', methods=['POST'])
@login_required
def admin_bloquear_usuario():
    """
    Rota administrativa para bloquear um usuário permanentemente.
    ATENÇÃO: Esta rota deve ser protegida adequadamente em produção!
    """
    email = request.form.get('email', '').strip().lower()

    if not email:
        flash("Email é obrigatório.", "danger")
        return redirect(url_for('configuracoes'))

    # Verificar se o email existe no sistema
    chefe = Chefe.query.filter_by(email=email).first()
    instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

    if not chefe and not instituicao:
        flash("Email não encontrado no sistema.", "danger")
        return redirect(url_for('configuracoes'))

    # Bloquear o usuário
    bloquear_usuario_permanentemente(email)

    flash(f"Usuário {email} bloqueado permanentemente.", "success")
    return redirect(url_for('configuracoes'))


@app.route('/admin/desbloquear-usuario', methods=['POST'])
@login_required
def admin_desbloquear_usuario():
    """
    Rota administrativa para desbloquear um usuário.
    ATENÇÃO: Esta rota deve ser protegida adequadamente em produção!
    """
    email = request.form.get('email', '').strip().lower()

    if not email:
        flash("Email é obrigatório.", "danger")
        return redirect(url_for('configuracoes'))

    # Desbloquear o usuário
    desbloquear_usuario(email)

    flash(f"Usuário {email} desbloqueado.", "success")
    return redirect(url_for('configuracoes'))


if __name__ == "__main__":
    # host para expor o servidor para fora do container
    app.run(debug=True, host='0.0.0.0')
