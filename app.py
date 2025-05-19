from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from unidecode import unidecode  # Biblioteca para remover acentos e caracteres especiais
from urllib.parse import unquote

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:educ123@db:3306/educ_invest?charset=utf8mb4'
db = SQLAlchemy(app)

# Configuração do flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redireciona para a página de login se não autenticado

CURSOS_PADRAO = [
    "Administração", "Agronomia", "Arquitetura", "Biologia", "Ciência da Computação",
    "Direito", "Educação Física", "Enfermagem", "Engenharia", "Farmácia", "Física",
    "Matemática", "Medicina", "Pedagogia", "Psicologia", "Química", "Sistemas de Informação",
    # ...adicione outros cursos desejados...
]

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
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'), nullable=False)

    instituicao = db.relationship('InstituicaodeEnsino', backref='cursos')

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_jovem = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    contato_jovem = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    endereco_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'))
    curso = db.Column(db.String(255))
    formacao = db.Column(db.String(255))
    periodo = db.Column(db.Integer)
    indicado_por = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'))  # Relacionamento com Chefe

    chefe = db.relationship('Chefe', backref='alunos_indicados')  # Relacionamento reverso

class Chefe(db.Model, UserMixin):
    __tablename__ = 'chefe'

    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)  # Pode ser nulo, mas deve ser único se fornecido
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

    def get_id(self):
        return str(self.id_chefe)

class SkillsDoAluno(db.Model):
    __tablename__ = 'skills_do_aluno'

    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), primary_key=True)  # Relaciona com a tabela Aluno
    hard_skills = db.Column(db.Integer)
    soft_skills = db.Column(db.Integer)
    avaliacao_geral = db.Column(db.Integer)
    participacao = db.Column(db.Integer)
    comunicacao = db.Column(db.Integer)
    proatividade = db.Column(db.Integer)
    raciocinio = db.Column(db.Integer)
    dominio_tecnico = db.Column(db.Integer)
    criatividade = db.Column(db.Integer)
    trabalho_em_equipe = db.Column(db.Integer)

    # Relacionamento com o modelo Aluno
    aluno = db.relationship('Aluno', backref=db.backref('skills', uselist=False))

class Acompanhamento(db.Model):
    __tablename__ = 'acompanhamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), nullable=False)
    data_acompanhamento = db.Column(db.DateTime, server_default=db.func.now())

    chefe = db.relationship('Chefe', backref='acompanhamentos')
    aluno = db.relationship('Aluno', backref='acompanhamentos')

    __table_args__ = (
        db.UniqueConstraint('id_chefe', 'id_aluno', name='uix_chefe_aluno'),
    )

# Adicione ao seu models.py ou app.py
class SkillsHistorico(db.Model):
    __tablename__ = 'skills_historico'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())
    hard_skills = db.Column(db.Integer)
    soft_skills = db.Column(db.Integer)
    avaliacao_geral = db.Column(db.Integer)
    participacao = db.Column(db.Integer)
    comunicacao = db.Column(db.Integer)
    proatividade = db.Column(db.Integer)
    raciocinio = db.Column(db.Integer)
    dominio_tecnico = db.Column(db.Integer)
    criatividade = db.Column(db.Integer)
    trabalho_em_equipe = db.Column(db.Integer)

    aluno = db.relationship('Aluno', backref='historicos')

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
            return redirect(url_for('home'))  # Redireciona para a página inicial
        return f(*args, **kwargs)
    return decorated_function

def bloquear_instituicao(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'instituicao':
            flash("Acesso não permitido para o perfil instituição de ensino.", "danger")
            return redirect(url_for('home'))  # Redireciona para a página inicial
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
                flash('Todos os campos obrigatórios para Instituição de Ensino devem ser preenchidos!')
                return redirect(url_for('cadastro'))

            try:
                nova_instituicaodeEnsino = InstituicaodeEnsino(
                    nome_instituicao=instituicao_nome,
                    email=email,
                    senha=generate_password_hash(senha),
                    infraestrutura=infraestrutura,
                    nota_mec=nota_mec,
                    areas_de_formacao=", ".join(cursos_selecionados),  # Apenas para histórico, não para lógica
                    modalidades=modalidades,
                    quantidade_de_alunos=0,
                    reitor=nome,
                    endereco_instituicao=endereco
                )
                db.session.add(nova_instituicaodeEnsino)
                db.session.commit()

                # Salva os cursos selecionados na tabela cursos
                for nome_curso in cursos_selecionados:
                    curso = Curso(nome=nome_curso, id_instituicao=nova_instituicaodeEnsino.id_instituicao)
                    db.session.add(curso)
                db.session.commit()

                flash('Cadastro de Instituição realizado com sucesso! Faça login agora.')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou instituição já cadastrados.')
                return redirect(url_for('cadastro'))

        elif tipo_usuario == 'chefe':
            empresa_nome = request.form.get('empresa_nome')
            cargo = request.form.get('cargo')

            if not nome or not email or not senha or not empresa_nome or not cargo:
                flash('Todos os campos obrigatórios para Chefe devem ser preenchidos!')
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
                flash('Cadastro de Chefe realizado com sucesso! Faça login agora.')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('Erro: E-mail ou chefe já cadastrados.')
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
        instituicao.quantidade_de_alunos = Aluno.query.filter_by(id_instituicao=instituicao.id_instituicao).count()

    # Novo: monta um dicionário com os cursos de cada instituição
    cursos_por_instituicao = {
        inst.id_instituicao: [curso.nome for curso in Curso.query.filter_by(id_instituicao=inst.id_instituicao).all()]
        for inst in instituicoes
    }

    return render_template(
        'instituicaoEnsino.html',
        instituicoes=instituicoes,
        cursos_por_instituicao=cursos_por_instituicao
    )

@app.route('/detalhes_instituicao/<int:id_instituicao>')
def detalhes_instituicao(id_instituicao):
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    return render_template('detalhes_instituicao.html', instituicao=instituicao)

@app.route('/minhas_selecoes')
@bloquear_instituicao
@login_required
def minhas_selecoes():
    if session.get('tipo_usuario') != 'chefe':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))
    
    chefe_id = current_user.id_chefe
    alunos = Aluno.query.filter_by(indicado_por=chefe_id).all()

    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        skills_dict = {
            "Hard Skills": skills.hard_skills if skills else 0,
            "Soft Skills": skills.soft_skills if skills else 0,
            "Avaliação Geral": skills.avaliacao_geral if skills else 0,
            "Participação": skills.participacao if skills else 0,
            "Comunicação": skills.comunicacao if skills else 0,
            "Proatividade": skills.proatividade if skills else 0,
            "Raciocínio": skills.raciocinio if skills else 0,
            "Domínio Técnico": skills.dominio_tecnico if skills else 0,
            "Criatividade": skills.criatividade if skills else 0,
            "Trabalho em Equipe": skills.trabalho_em_equipe if skills else 0
        } if skills else {}

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome_jovem": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "skills": skills_dict
        })

    return render_template('minhas_selecoes.html', alunos=alunos_com_skills)

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

    return redirect(url_for('alunos'))

@app.route('/ver_alunos_por_curso', methods=['GET'])
@bloquear_instituicao
@login_required
def ver_alunos_por_curso():
    inst_id = request.args.get('inst_id')
    curso = request.args.get('curso')

    # Decodificar o parâmetro 'curso' para evitar problemas com caracteres especiais
    curso = unquote(curso).strip()

    # Normalizar o nome do curso para remover acentos e caracteres especiais
    curso_normalizado = unidecode(curso).lower()

    # Busca os alunos pelo curso e instituição
    alunos = Aluno.query.filter(
        Aluno.id_instituicao == inst_id
    ).all()

    # Filtrar os alunos em Python para aplicar a normalização
    alunos_filtrados = [
        aluno for aluno in alunos
        if unidecode(aluno.curso).lower() == curso_normalizado
    ]

    # Verifica se há alunos encontrados
    if not alunos_filtrados:
        flash(f"Nenhum aluno encontrado para o curso '{curso}'.", "warning")
        return redirect(url_for('instituicao_ensino'))

    # Converte os dados de skills para dicionários completos
    alunos_com_skills = []
    for aluno in alunos_filtrados:
        skills = aluno.skills
        skills_dict = {
            "Hard Skills": skills.hard_skills if skills else 0,
            "Soft Skills": skills.soft_skills if skills else 0,
            "Avaliação Geral": skills.avaliacao_geral if skills else 0,
            "Participação": skills.participacao if skills else 0,
            "Comunicação": skills.comunicacao if skills else 0,
            "Proatividade": skills.proatividade if skills else 0,
            "Raciocínio": skills.raciocinio if skills else 0,
            "Domínio Técnico": skills.dominio_tecnico if skills else 0,
            "Criatividade": skills.criatividade if skills else 0,
            "Trabalho em Equipe": skills.trabalho_em_equipe if skills else 0
        } if skills else {}

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "skills": skills_dict
        })

    return render_template('cardAlunos.html', alunos=alunos_com_skills, curso=curso)

@app.route('/detalhes_aluno/<int:id_aluno>')
@bloquear_instituicao
@login_required
def detalhes_aluno(id_aluno):
    aluno = Aluno.query.filter_by(id_aluno=id_aluno).first()
    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('alunos'))

    previous_url = request.args.get('previous', url_for('instituicao_ensino'))  # fallback se não houver parâmetro

    skills = {
        "Hard Skills": aluno.skills.hard_skills,
        "Soft Skills": aluno.skills.soft_skills,
        "Avaliação Geral": aluno.skills.avaliacao_geral,
        "Participação": aluno.skills.participacao,
        "Comunicação": aluno.skills.comunicacao,
        "Proatividade": aluno.skills.proatividade,
        "Raciocínio": aluno.skills.raciocinio,
        "Domínio Técnico": aluno.skills.dominio_tecnico,
        "Criatividade": aluno.skills.criatividade,
        "Trabalho em Equipe": aluno.skills.trabalho_em_equipe
    } if aluno.skills else {}

    return render_template('detalhes_aluno.html', aluno=aluno, skills=skills, previous_url=previous_url)

@app.route('/indicar_aluno/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def indicar_aluno(id_aluno):
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    aluno = Aluno.query.get_or_404(id_aluno)
    chefe_id = current_user.id_chefe

    # Verifica se o aluno já foi indicado
    if aluno.indicado_por is not None:
        return jsonify({'error': 'Este aluno já foi indicado.'}), 400

    # Atualiza o campo indicado_por
    aluno.indicado_por = chefe_id
    db.session.commit()

    return jsonify({'message': 'Aluno indicado com sucesso!'}), 200

@app.route('/cardAlunos')
@bloquear_instituicao
@login_required
def cardAlunos():
    alunos = Aluno.query.all()
    dados_alunos = []

    for aluno in alunos:
        skills = aluno.skills
        skills_dict = {
            "Hard Skills": skills.hard_skills if skills else 0,
            "Soft Skills": skills.soft_skills if skills else 0,
            "Avaliação Geral": skills.avaliacao_geral if skills else 0,
            "Participação": skills.participacao if skills else 0,
            "Comunicação": skills.comunicacao if skills else 0,
            "Proatividade": skills.proatividade if skills else 0,
            "Raciocínio": skills.raciocinio if skills else 0,
            "Domínio Técnico": skills.dominio_tecnico if skills else 0,
            "Criatividade": skills.criatividade if skills else 0,
            "Trabalho em Equipe": skills.trabalho_em_equipe if skills else 0
        } if skills else {}

        dados_alunos.append({
            'id_aluno': aluno.id_aluno,
            'nome': aluno.nome_jovem,
            'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            'curso': aluno.curso,
            'contato_jovem': aluno.contato_jovem,
            'email': aluno.email,
            'skills': skills_dict
        })

    return render_template('cardAlunos.html', alunos=dados_alunos)

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
            novo_curso = Curso(nome=nome_curso, id_instituicao=current_user.id_instituicao)
            db.session.add(novo_curso)
            db.session.commit()
            flash('Curso cadastrado com sucesso!', 'success')
        return redirect(url_for('cursos'))

    cursos = Curso.query.filter_by(id_instituicao=current_user.id_instituicao).all()
    return render_template('cursos.html', cursos=cursos)

@app.route('/alunos')
@login_required
@bloquear_chefe
def alunos():
    return render_template('alunos.html')

@app.route('/cadastrar_aluno', methods=['POST'])
@login_required
@bloquear_chefe
def cadastrar_aluno():
    # Dados do aluno
    nome_jovem = request.form['nome_jovem']
    data_nascimento = request.form['data_nascimento']
    contato_jovem = request.form['contato_jovem']
    email = request.form['email']
    endereco_jovem = request.form['endereco_jovem']
    curso = request.form['curso']
    formacao = request.form['formacao']
    periodo = request.form['periodo']

    # Dados das skills
    hard_skills = request.form['hard_skills']
    soft_skills = request.form['soft_skills']
    avaliacao_geral = request.form['avaliacao_geral']
    participacao = request.form['participacao']
    comunicacao = request.form['comunicacao']
    proatividade = request.form['proatividade']
    raciocinio = request.form['raciocinio']
    dominio_tecnico = request.form['dominio_tecnico']
    criatividade = request.form['criatividade']
    trabalho_em_equipe = request.form['trabalho_em_equipe']

    try:
        # Criar o aluno
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

        # Criar as skills do aluno
        skills = SkillsDoAluno(
            id_aluno=novo_aluno.id_aluno,
            hard_skills=hard_skills,
            soft_skills=soft_skills,
            avaliacao_geral=avaliacao_geral,
            participacao=participacao,
            comunicacao=comunicacao,
            proatividade=proatividade,
            raciocinio=raciocinio,
            dominio_tecnico=dominio_tecnico,
            criatividade=criatividade,
            trabalho_em_equipe=trabalho_em_equipe
        )
        db.session.add(skills)
        db.session.commit()

        # Atualizar a quantidade de alunos na instituição
        instituicao = InstituicaodeEnsino.query.get(current_user.id_instituicao)
        instituicao.quantidade_de_alunos += 1
        db.session.commit()

        flash("Aluno cadastrado com sucesso!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Erro ao cadastrar aluno. Verifique os dados e tente novamente.", "danger")

    return redirect(url_for('alunos_instituicao'))

@app.route('/alunos_instituicao', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def alunos_instituicao():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    instituicao_id = current_user.id_instituicao

    # Pegue os cursos diretamente da tabela cursos
    cursos_disponiveis = [curso.nome for curso in Curso.query.filter_by(id_instituicao=instituicao_id).all()]

    # Para filtro de cursos já cadastrados em alunos (opcional)
    cursos = Aluno.query.with_entities(Aluno.curso).filter_by(id_instituicao=instituicao_id).distinct().all()
    cursos = [curso[0] for curso in cursos if curso[0]]

    filtro_curso = request.form.get('curso') if request.method == 'POST' else None

    if filtro_curso:
        alunos = Aluno.query.filter_by(id_instituicao=instituicao_id, curso=filtro_curso).all()
    else:
        alunos = Aluno.query.filter_by(id_instituicao=instituicao_id).all()

    # Adicionar as skills de cada aluno
    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        skills_dict = {
            "Hard Skills": skills.hard_skills,
            "Soft Skills": skills.soft_skills,
            "Avaliação Geral": skills.avaliacao_geral,
            "Participação": skills.participacao,
            "Comunicação": skills.comunicacao,
            "Proatividade": skills.proatividade,
            "Raciocínio": skills.raciocinio,
            "Domínio Técnico": skills.dominio_tecnico,
            "Criatividade": skills.criatividade,
            "Trabalho em Equipe": skills.trabalho_em_equipe
        } if skills else {}

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "skills": skills_dict
        })

    return render_template(
        'alunos_instituicao.html',
        alunos=alunos_com_skills,
        cursos=cursos,
        filtro_curso=filtro_curso,
        cursos_disponiveis=cursos_disponiveis  # <-- Agora sempre atualizado!
    )

@app.route('/detalhes_aluno_instituicao/<int:id_aluno>', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def detalhes_aluno_instituicao(id_aluno):
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    aluno = Aluno.query.get_or_404(id_aluno)

    if request.method == 'POST':
        # Atualizar informações do aluno
        aluno.nome_jovem = request.form['nome_jovem']
        aluno.data_nascimento = request.form['data_nascimento']
        aluno.contato_jovem = request.form['contato_jovem']
        aluno.email = request.form['email']
        aluno.endereco_jovem = request.form['endereco_jovem']
        aluno.curso = request.form['curso']
        aluno.formacao = request.form['formacao']
        aluno.periodo = request.form['periodo']

        # Atualizar informações de skills
        skills = aluno.skills or SkillsDoAluno(id_aluno=aluno.id_aluno)
        skills.hard_skills = request.form['hard_skills']
        skills.soft_skills = request.form['soft_skills']
        skills.avaliacao_geral = request.form['avaliacao_geral']
        skills.participacao = request.form['participacao']
        skills.comunicacao = request.form['comunicacao']
        skills.proatividade = request.form['proatividade']
        skills.raciocinio = request.form['raciocinio']
        skills.dominio_tecnico = request.form['dominio_tecnico']
        skills.criatividade = request.form['criatividade']
        skills.trabalho_em_equipe = request.form['trabalho_em_equipe']

        db.session.add(skills)
        db.session.commit()

        # --- NOVO: Salvar snapshot no histórico ---
        historico = SkillsHistorico(
            id_aluno=aluno.id_aluno,
            hard_skills=skills.hard_skills,
            soft_skills=skills.soft_skills,
            avaliacao_geral=skills.avaliacao_geral,
            participacao=skills.participacao,
            comunicacao=skills.comunicacao,
            proatividade=skills.proatividade,
            raciocinio=skills.raciocinio,
            dominio_tecnico=skills.dominio_tecnico,
            criatividade=skills.criatividade,
            trabalho_em_equipe=skills.trabalho_em_equipe
        )
        db.session.add(historico)
        db.session.commit()
        # --- FIM DO NOVO ---

        flash("Informações do aluno atualizadas com sucesso!", "success")
        return redirect(url_for('alunos_instituicao'))

    return render_template('detalhes_aluno_instituicao.html', aluno=aluno)

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    tipo_usuario = session.get('tipo_usuario')

    if request.method == 'POST':
        # Atualizar informações do chefe
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get_or_404(current_user.id_chefe)
            chefe.nome = request.form['nome']
            chefe.cargo = request.form['cargo']
            chefe.nome_empresa = request.form.get('nome_empresa')
            chefe.email = request.form['email']
            if request.form['senha']:
                chefe.senha = generate_password_hash(request.form['senha'])
            db.session.commit()
            flash("Perfil atualizado com sucesso!", "success")
        # Atualizar informações da instituição
        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get_or_404(current_user.id_instituicao)
            instituicao.nome_instituicao = request.form['nome_instituicao']
            instituicao.endereco_instituicao = request.form['endereco_instituicao']
            instituicao.reitor = request.form['reitor']
            instituicao.infraestrutura = request.form['infraestrutura']
            instituicao.nota_mec = request.form['nota_mec']
            # NÃO atualize areas_de_formacao manualmente!
            instituicao.modalidades = request.form['modalidades']
            instituicao.email = request.form['email']
            if request.form['senha']:
                instituicao.senha = generate_password_hash(request.form['senha'])
            db.session.commit()
            flash("Perfil atualizado com sucesso!", "success")
        return redirect(url_for('perfil'))

    # Exibir informações do perfil
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(current_user.id_instituicao)
        # Pegue os cursos reais da tabela cursos
        cursos_da_instituicao = Curso.query.filter_by(id_instituicao=current_user.id_instituicao).all()
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
    acompanhamento = Acompanhamento.query.filter_by(id_chefe=chefe_id, id_aluno=id_aluno).first()
    if acompanhamento:
        return jsonify({'error': 'Você já está acompanhando este aluno.'}), 400

    novo_acompanhamento = Acompanhamento(id_chefe=chefe_id, id_aluno=id_aluno)
    db.session.add(novo_acompanhamento)
    db.session.commit()
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
        skills_dict = {
            "Hard Skills": skills.hard_skills,
            "Soft Skills": skills.soft_skills,
            "Avaliação Geral": skills.avaliacao_geral,
            "Participação": skills.participacao,
            "Comunicação": skills.comunicacao,
            "Proatividade": skills.proatividade,
            "Raciocínio": skills.raciocinio,
            "Domínio Técnico": skills.dominio_tecnico,
            "Criatividade": skills.criatividade,
            "Trabalho em Equipe": skills.trabalho_em_equipe
        } if skills else {}
        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome_jovem": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "skills": skills_dict
        })
    return render_template('acompanhar.html', alunos=alunos_com_skills)

@app.route('/remover_acompanhamento/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def remover_acompanhamento(id_aluno):
    chefe_id = current_user.id_chefe
    acompanhamento = Acompanhamento.query.filter_by(id_chefe=chefe_id, id_aluno=id_aluno).first()
    if acompanhamento:
        db.session.delete(acompanhamento)
        db.session.commit()
        return jsonify({'message': 'Acompanhamento removido com sucesso!'})
    return jsonify({'error': 'Acompanhamento não encontrado.'}), 404

@app.route('/status_aluno/<int:id_aluno>')
@login_required
@bloquear_instituicao
def status_aluno(id_aluno):
    historicos = SkillsHistorico.query.filter_by(id_aluno=id_aluno).order_by(SkillsHistorico.data.desc()).all()
    aluno = Aluno.query.get_or_404(id_aluno)
    campos = [
        'hard_skills','soft_skills','avaliacao_geral','participacao','comunicacao',
        'proatividade','raciocinio','dominio_tecnico','criatividade','trabalho_em_equipe'
    ]
    historico_pares = []
    for i in range(len(historicos) - 1):
        atual = {campo: getattr(historicos[i], campo) for campo in campos}
        anterior = {campo: getattr(historicos[i+1], campo) for campo in campos}
        data_atual = historicos[i].data
        historico_pares.append({'atual': atual, 'anterior': anterior, 'data': data_atual})
    return render_template('status_aluno.html', historico_pares=historico_pares, aluno=aluno)

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # host para expor o servidor para fora do container