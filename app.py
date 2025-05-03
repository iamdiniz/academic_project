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
    endereço_instituicao = db.Column(db.String(255), nullable=False)
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
    endereço_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'))
    Curso = db.Column(db.String(255))
    formação = db.Column(db.String(255))
    periodo = db.Column(db.Integer)

with app.app_context():
    db.create_all()  # mantido caso quiser criar outras tabelas

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        instituicao_nome = request.form.get('instituicao_nome')  # Corrigido para o nome correto do campo
        endereco = request.form.get('endereco_instituicao')

        if not nome or not email or not senha or not instituicao_nome:
            flash('Todos os campos obrigatórios devem ser preenchidos!')
            return redirect(url_for('cadastro'))

        try:
            nova_instituicaodeEnsino = InstituicaodeEnsino(
                nome_instituicao=instituicao_nome,  # Atualizado para o campo correto
                email=email,
                senha=generate_password_hash(senha),
                infraestrutura="Infraestrutura padrão",  # Adicione valores padrão para campos obrigatórios
                nota_mec=0,
                areas_de_formacao="Áreas padrão",
                modalidades="Modalidades padrão",
                quantidade_de_alunos=0,
                reitor=nome,
                endereço_instituicao=endereco
            )
            db.session.add(nova_instituicaodeEnsino)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login agora.')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Erro: E-mail ou instituição já cadastrados.')
    
    return render_template('cadastro.html')

@app.route('/')
def index():
    return redirect(url_for('cadastro'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        instituicaodeEnsino = InstituicaodeEnsino.query.filter_by(email=email).first()
        if instituicaodeEnsino and check_password_hash(instituicaodeEnsino.senha, senha):
            session['instituicaodeEnsino_id'] = instituicaodeEnsino.id_instituicao
            return redirect(url_for('home'))  # Redireciona o navegador para acessar a rota /home
        else:
            return 'Credenciais inválidas!', 401
    return render_template('login.html')

@app.route('/home')
def home():
    instituicaodeEnsino = db.session.get(InstituicaodeEnsino, session.get('instituicaodeEnsino_id'))
    if not instituicaodeEnsino:
        return redirect(url_for('login'))
    return render_template('home.html', instituicaodeEnsino=instituicaodeEnsino)  # Renderiza o HTML com o chefe

@app.route("/instituicaoEnsino")
def instituicaoEnsino():
    instituicaos = InstituicaodeEnsino.query.all()
    return render_template("instituicaoEnsino.html", instituicaos=instituicaos)

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