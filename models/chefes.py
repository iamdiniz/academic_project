from flask_login import UserMixin
from .base import db

class Chefe(db.Model, UserMixin):
    """Modelo para representar um chefe/gestor no sistema."""
    __tablename__ = 'chefe'
    
    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    # Pode ser nulo, mas deve ser único se fornecido
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

    def get_id(self):
        """Retorna o ID do usuário para Flask-Login."""
        return str(self.id_chefe)
    
    def __repr__(self):
        return f'<Chefe {self.nome}>'
