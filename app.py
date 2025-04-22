from flask import Flask, render_template, url_for, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = 'minha-chave-teste'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Chefe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(120), nullable=False)
    empresa = db.Column(db.String(80), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<Chefe {self.nome}>'

with app.app_context():
    db.create_all()
    try:
        if not Chefe.query.filter_by(email='teste@email.com').first():
            chefe = Chefe(
                nome='Chefe Teste',
                email='teste@email.com',
                senha=generate_password_hash('123456'),
                empresa='Empresa Teste'
            )
            db.session.add(chefe)
            db.session.commit()
            print('Chefe mockado criado!')
    except IntegrityError:
        db.session.rollback()
        print('Chefe já existe.')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        chefe = Chefe.query.filter_by(email=email).first()
        if chefe and check_password_hash(chefe.senha, senha):
            session['chefe_id'] = chefe.id
            return redirect(url_for('home'))  # Redireciona o navegador para acessar a rota /home
        else:
            return 'Credenciais inválidas!', 401
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/home')
def home():
    chefe = db.session.get(Chefe, session.get('chefe_id'))
    if not chefe:
        return redirect(url_for('login'))
    return render_template('home.html', chefe=chefe)  # Renderiza o HTML com o chefe

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')  # host para expor o servidor para fora do container
