from flask_login import UserMixin
from extensions.database import db

class Chefe(db.Model, UserMixin):
    """Modelo para Chefe"""
    __tablename__ = 'chefe'

    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

    def get_id(self):
        return str(self.id_chefe)
