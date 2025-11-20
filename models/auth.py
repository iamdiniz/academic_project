from datetime import datetime
from .base import db

class TwoFactor(db.Model):
    """Modelo para gerenciar autenticação de dois fatores."""
    __tablename__ = 'two_factor'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 'chefe' ou 'instituicao'
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    otp_secret = db.Column(db.String(64), nullable=False)
    enabled = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    __table_args__ = (db.UniqueConstraint('user_type', 'user_id', name='uix_2fa_user'),)
    
    def __repr__(self):
        return f'<TwoFactor {self.user_type}:{self.user_id}>'

class ResetarSenha(db.Model):
    """Modelo para gerenciar tokens de redefinição de senha."""
    __tablename__ = 'resetar_senha'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False)
    codigo = db.Column(db.String(6), nullable=False)
    # 'chefe' ou 'instituicao'
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used = db.Column(db.Boolean, default=False)
    tentativas = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<ResetarSenha {self.email}>'

class PasswordHistory(db.Model):
    """Modelo para armazenar histórico de senhas e bloquear reutilização."""
    __tablename__ = 'password_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 'chefe' ou 'instituicao'
    user_type = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<PasswordHistory {self.user_type}:{self.user_id} at {self.created_at}>'
