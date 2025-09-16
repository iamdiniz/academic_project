from datetime import datetime
from .base import db

class LogAcesso(db.Model):
    """Modelo para registrar logs de acesso ao sistema."""
    __tablename__ = 'log_acesso'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    tipo_usuario = db.Column(db.String(30), nullable=False)
    acao = db.Column(db.String(20), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<LogAcesso {self.usuario_nome} - {self.acao}>'
