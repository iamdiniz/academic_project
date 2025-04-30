from flask import Flask, render_template, url_for, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Faculdade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    instituicao = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return f'<Faculdade {self.nome}>'

with app.app_context():
    db.create_all()
    try:
        if not Faculdade.query.filter_by(email='teste@email.com').first():
            faculdade = Faculdade(
                nome='Fernando',
                email='teste@email.com',
                senha=generate_password_hash('123456'),
                instituicao='Uninassau'
            )
            db.session.add(faculdade)
            db.session.commit()
            print('Faculdade mockado criado!')
    except IntegrityError:
        db.session.rollback()
        print('Faculdade já existe.')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        instituicao = request.form['instituicao']

        try:
            nova_faculdade = Faculdade(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha),
                instituicao=instituicao
            )
            db.session.add(nova_faculdade)
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

        faculdade = Faculdade.query.filter_by(email=email).first()
        if faculdade and check_password_hash(faculdade.senha, senha):
            session['faculdade_id'] = faculdade.id
            return redirect(url_for('home'))  # Redireciona o navegador para acessar a rota /home
        else:
            return 'Credenciais inválidas!', 401
    return render_template('login.html')

@app.route('/home')
def home():
    faculdade = db.session.get(Faculdade, session.get('faculdade_id'))
    if not faculdade:
        return redirect(url_for('login'))
    return render_template('home.html', faculdade=faculdade)  # Renderiza o HTML com o chefe

@app.route("/instituicaoEnsino")
def instituicaoEnsino():
    instituicaos = [
        {
            "instituicao": "UNINASSAU",
            "logo": "/static/uninassau.png",  # Salve a logo aqui
            "matriculados": 20.000,
            "modalidade": "EAD, Presencial e Semi-Presencial",
            "cursos": "Ciencia da computação, ADM, etc..."
        },
        {
            "instituicao": "UNICAP",
            "logo": "/static/unicap.png",  # Salve a logo aqui
            "matriculados": 10.000,
            "modalidade": "EAD e Presencial",
            "cursos": "Direito, ADM, etc..."
        },
        {
            "instituicao": "UNIBRA",
            "logo": "/static/unibra.png",  # Salve a logo aqui
            "matriculados": 15.000,
            "modalidade": "EAD e Presencial",
            "cursos": "Educação Fisíca, Design, etc..."
        }
    ]
    return render_template("instituicaoEnsino.html", instituicaos=instituicaos)

@app.route('/logout')
def logout():
    session.pop('faculdade_id', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # host para expor o servidor para fora do container
    