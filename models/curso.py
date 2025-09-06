from extensions.database import db

class Curso(db.Model):
    """Modelo para Curso"""
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'), nullable=False)

    # Relacionamento
    instituicao = db.relationship('InstituicaodeEnsino', backref='cursos')
