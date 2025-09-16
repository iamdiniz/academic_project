from .base import db

class Curso(db.Model):
    """Modelo para representar cursos oferecidos pelas instituições."""
    __tablename__ = 'cursos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'), nullable=False)
    
    # Relacionamentos
    instituicao = db.relationship('InstituicaodeEnsino', backref='cursos')
    
    def __repr__(self):
        return f'<Curso {self.nome}>'
