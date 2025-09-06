from extensions.database import db

class Indicacao(db.Model):
    """Modelo para Indicação"""
    __tablename__ = 'indicacoes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), nullable=False)
    data_indicacao = db.Column(db.DateTime, server_default=db.func.now())

    # Relacionamentos
    chefe = db.relationship('Chefe', backref='indicacoes')
    aluno = db.relationship('Aluno', backref='indicacoes')

    __table_args__ = (
        db.UniqueConstraint('id_chefe', 'id_aluno', name='uix_chefe_aluno_indicacao'),
    )
