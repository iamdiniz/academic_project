from .base import db

class Aluno(db.Model):
    """Modelo para representar um aluno no sistema."""
    __tablename__ = 'alunos'
    
    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_jovem = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    contato_jovem = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    endereco_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey('instituicao_de_ensino.id_instituicao'))
    curso = db.Column(db.String(255))
    formacao = db.Column(db.String(255))
    periodo = db.Column(db.Integer)
    indicado_por = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'))
    
    # Relacionamentos
    chefe = db.relationship('Chefe', backref='alunos_indicados')
    instituicao = db.relationship('InstituicaodeEnsino', backref='alunos')
    
    def __repr__(self):
        return f'<Aluno {self.nome_jovem}>'
