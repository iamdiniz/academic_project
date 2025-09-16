from flask_login import UserMixin
from .base import db

class InstituicaodeEnsino(db.Model, UserMixin):
    """Modelo para representar uma instituição de ensino."""
    __tablename__ = 'instituicao_de_ensino'
    
    id_instituicao = db.Column(db.Integer, primary_key=True)
    nome_instituicao = db.Column(db.String(100), nullable=False)
    endereco_instituicao = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    senha = db.Column(db.String(255), nullable=False)
    infraestrutura = db.Column(db.Text, nullable=False)
    nota_mec = db.Column(db.Numeric, nullable=False)
    areas_de_formacao = db.Column(db.Text, nullable=False)
    modalidades = db.Column(db.String(255), nullable=False)
    quantidade_de_alunos = db.Column(db.Integer, nullable=False)
    reitor = db.Column(db.String(255), nullable=False)

    def get_id(self):
        """Retorna o ID do usuário para Flask-Login."""
        return str(self.id_instituicao)
    
    def __repr__(self):
        return f'<InstituicaodeEnsino {self.nome_instituicao}>'
