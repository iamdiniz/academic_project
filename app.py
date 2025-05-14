from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:educ123@db:3306/educ_invest'
db = SQLAlchemy(app)

# Configuração do flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Redireciona para a página de login se não autenticado

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

with app.app_context():
    db.create_all()  # Recria as tabelas com base nos modelos
    print("Tabelas recriadas com sucesso!")

@login_manager.user_loader
def load_user(user_id):
    # Tenta carregar o usuário como Chefe ou Instituição de Ensino
    chefe = Chefe.query.get(int(user_id))
    if chefe:
        return chefe
    return InstituicaodeEnsino.query.get(int(user_id))

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
        tipo_usuario = request.form.get('tipo_usuario')  # Verifica o tipo de usuário
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')

        # Validação de senha
        confirmar_senha = request.form.get('confirmar_senha')
        if senha != confirmar_senha:
            flash('As senhas não coincidem!')
            return redirect(url_for('cadastro'))

        if tipo_usuario == 'instituicao':
            instituicao_nome = request.form.get('instituicao_nome')
            endereco = request.form.get('endereco_instituicao')

            if not nome or not email or not senha or not instituicao_nome or not endereco:
                flash('Todos os campos obrigatórios para Instituição de Ensino devem ser preenchidos!')
                return redirect(url_for('cadastro'))

            try:
                nova_instituicaodeEnsino = InstituicaodeEnsino(
                    nome_instituicao=instituicao_nome,
                    email=email,
                    senha=generate_password_hash(senha),
                    infraestrutura="Infraestrutura padrão",
                    nota_mec=0,
                    areas_de_formacao="Áreas padrão",
                    modalidades="Modalidades padrão",
                    quantidade_de_alunos=0,
                    reitor=nome,
                    endereco_instituicao=endereco
                )
                db.session.add(nova_instituicaodeEnsino)
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

    return render_template('cadastro.html')

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

    # Log para verificar os valores de areas_de_formacao
    for inst in instituicoes:
        print(f"Instituição: {inst.nome_instituicao}, Cursos: {inst.areas_de_formacao}")

    return render_template('instituicaoEnsino.html', instituicoes=instituicoes)

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
    
    # Obtenha os alunos indicados pelo chefe logado
    chefe_id = current_user.id_chefe
    alunos = Aluno.query.filter_by(indicado_por=chefe_id).all()
    return render_template('minhas_selecoes.html', alunos=alunos)

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

@app.route('/ver_alunos_por_curso', methods=['GET'])
@bloquear_instituicao
@login_required
def ver_alunos_por_curso():
    inst_id = request.args.get('inst_id')
    curso = request.args.get('curso')

    # Busca os alunos pelo curso e instituição
    alunos = Aluno.query.filter_by(id_instituicao=inst_id, curso=curso).all()

    # Converte os dados de skills para dicionários
    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        skills_dict = {
            "Hard Skills": skills.hard_skills,
            "Soft Skills": skills.soft_skills,
            "Avaliação Geral": skills.avaliacao_geral,
            "Comunicação": skills.comunicacao,
            "Criatividade": skills.criatividade,
            "Trabalho em Equipe": skills.trabalho_em_equipe
        } if skills else {}

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,  # Corrigido para usar id_aluno
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
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
        dados_alunos.append({
            'id': aluno.id_aluno,
            'nome': aluno.nome_jovem,
            'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            'curso': aluno.curso,
            'skills': {
                'Hard Skills': skills.hard_skills,
                'Soft Skills': skills.soft_skills,
                'Avaliação Geral': skills.avaliacao_geral,
            } if skills else {}
        })

    return render_template('cardAlunos.html', alunos=dados_alunos)

@app.route('/carousel')
def carousel():
    return render_template('carousel.html')

@app.route('/cursos')
@login_required
@bloquear_chefe
def cursos():
    return render_template('cursos.html')

@app.route('/alunos')
@login_required
@bloquear_chefe
def alunos():
    return render_template('alunos.html')

@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # host para expor o servidor para fora do container