from datetime import datetime
from .base import db

class SkillsDoAluno(db.Model):
    """Modelo para armazenar as habilidades atuais de um aluno."""
    __tablename__ = 'skills_do_aluno'
    
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), primary_key=True)
    # Hard skills dinâmicas por curso (JSON)
    hard_skills_json = db.Column(db.Text)
    # Soft skills detalhadas (JSON)
    soft_skills_json = db.Column(db.Text)
    
    # Relacionamentos
    aluno = db.relationship('Aluno', backref=db.backref('skills', uselist=False))
    
    def __repr__(self):
        return f'<SkillsDoAluno aluno_id={self.id_aluno}>'

class SkillsHistorico(db.Model):
    """Modelo para armazenar o histórico de avaliações de habilidades."""
    __tablename__ = 'skills_historico'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'), nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())
    hard_skills_json = db.Column(db.Text)
    soft_skills_json = db.Column(db.Text)

    # Relacionamentos
    aluno = db.relationship('Aluno', backref='historicos')
    chefe = db.relationship('Chefe', backref='historicos')
    
    def __repr__(self):
        return f'<SkillsHistorico aluno_id={self.id_aluno} chefe_id={self.id_chefe}>'
