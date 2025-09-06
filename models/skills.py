from extensions.database import db

class SkillsDoAluno(db.Model):
    """Modelo para Skills do Aluno"""
    __tablename__ = 'skills_do_aluno'

    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), primary_key=True)
    hard_skills_json = db.Column(db.Text)  # Hard skills dinâmicas por curso (JSON)
    soft_skills_json = db.Column(db.Text)  # Soft skills detalhadas (JSON)
    
    # Relacionamento
    aluno = db.relationship('Aluno', backref=db.backref('skills', uselist=False))
