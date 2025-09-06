from extensions.database import db

class SkillsHistorico(db.Model):
    """Modelo para Histórico de Skills"""
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
