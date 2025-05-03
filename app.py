from flask import Flask, render_template, url_for, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class InstituicaodeEnsino(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    instituicao = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<InstituicaodeEnsino {self.nome}>'

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    score_geral = db.Column(db.Integer, nullable=False)
    evolucao = db.Column(db.Integer, nullable=False)
    soft_skills = db.Column(db.Integer, nullable=False)
    hard_skills = db.Column(db.Integer, nullable=False)
    media_testes = db.Column(db.Integer, nullable=False)
    curso = db.Column(db.String(100), nullable=False)
    area_destaque = db.Column(db.String(100), nullable=False)
    foto_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Aluno {self.nome}>'

with app.app_context():
    db.create_all()
    try:
        if not InstituicaodeEnsino.query.filter_by(email='teste@email.com').first():
            instituicaodeEnsino = InstituicaodeEnsino(
                nome='Fernando',
                email='teste@email.com',
                senha=generate_password_hash('123456'),
                instituicao='Uninassau'
            )
            db.session.add(instituicaodeEnsino)
            db.session.commit()
            print('Instituição de Ensino mockado criado!')
    except IntegrityError:
        db.session.rollback()
        print('Instituição de Ensino já existe.')

    try:
        if not Aluno.query.filter_by(nome='BRUNO BELARMINO').first():
            aluno = Aluno(
                nome='BRUNO BELARMINO',
                idade=25,
                score_geral=78,
                evolucao=47,
                soft_skills=67,
                hard_skills=58,
                media_testes=87,
                curso='Sistemas de Informação',
                area_destaque='Front-End',
                foto_url='/static/foto_bruno.png'
            )
            db.session.add(aluno)
            db.session.commit()
            print('Aluno mockado criado!')
    except IntegrityError:
        db.session.rollback()
        print('Aluno já existe.')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        instituicao = request.form['instituicao']

        try:
            nova_instituicaodeEnsino = InstituicaodeEnsino(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha),
                instituicao=instituicao
            )
            db.session.add(nova_instituicaodeEnsino)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça login agora.')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('Erro: E-mail, nome ou instituicao já cadastrados.')
    
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
            session['instituicaodeEnsino_id'] = instituicaodeEnsino.id
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
    