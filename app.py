from flask import Flask, render_template, url_for, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:educ123@db:3306/educ_invest'
db = SQLAlchemy(app)

class InstituicaodeEnsino(db.Model):
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

class Aluno(db.Model):
    __tablename__ = 'alunos'

    id_jovem = db.Column(db.Integer, primary_key=True)
    nome_jovem = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    contato_jovem = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    endereco_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'))
    curso = db.Column(db.String(255))
    formacao = db.Column(db.String(255))
    periodo = db.Column(db.Integer)

class Chefe(db.Model):
    __tablename__ = 'chefe'

    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)  # Pode ser nulo, mas deve ser único se fornecido
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

with app.app_context():
    db.drop_all()  # Remove todas as tabelas
    db.create_all()  # Recria as tabelas com base nos modelos
    print("Tabelas recriadas com sucesso!")

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
    return redirect(url_for('cadastro'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        # Verifica se o login é de uma Instituição de Ensino
        instituicaodeEnsino = InstituicaodeEnsino.query.filter_by(email=email).first()
        if instituicaodeEnsino and check_password_hash(instituicaodeEnsino.senha, senha):
            session['instituicaodeEnsino_id'] = instituicaodeEnsino.id_instituicao
            return redirect(url_for('home'))  # Redireciona para a página inicial

        # Verifica se o login é de um Chefe
        chefe = Chefe.query.filter_by(email=email).first()
        if chefe and check_password_hash(chefe.senha, senha):
            session['chefe_id'] = chefe.id_chefe
            return redirect(url_for('home'))  # Redireciona para a página inicial

        # Se nenhum dos dois for válido
        flash('Credenciais inválidas!')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/home')
def home():
    # Verifica se é uma Instituição de Ensino logada
    instituicaodeEnsino = db.session.get(InstituicaodeEnsino, session.get('instituicaodeEnsino_id'))
    if instituicaodeEnsino:
        return render_template('home.html', usuario=instituicaodeEnsino, tipo_usuario='instituicao')

    # Verifica se é um Chefe logado
    chefe = db.session.get(Chefe, session.get('chefe_id'))
    if chefe:
        return render_template('home.html', usuario=chefe, tipo_usuario='chefe')

    # Se nenhum usuário estiver logado, redireciona para o login
    return redirect(url_for('login'))

@app.route('/instituicaoEnsino')
def instituicao_ensino():
    # Busca todas as instituições no banco de dados
    instituicoes = InstituicaodeEnsino.query.all()
    return render_template('instituicaoEnsino.html', instituicaos=instituicoes)

@app.route('/cardAlunos')
def cardAlunos():
    alunos = Aluno.query.all()
    return render_template('cardAlunos.html', alunos=alunos)
    
@app.route('/logout')
def logout():
    session.pop('instituicaodeEnsino_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # host para expor o servidor para fora do container