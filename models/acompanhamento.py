from extensions.database import db

class Acompanhamento(db.Model):
    """Modelo para Acompanhamento"""
    __tablename__ = 'acompanhamento'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey('chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id_aluno'), nullable=False)
    data_acompanhamento = db.Column(db.DateTime, server_default=db.func.now())

    # Relacionamentos
    chefe = db.relationship('Chefe', backref='acompanhamentos')
    aluno = db.relationship('Aluno', backref='acompanhamentos')

    __table_args__ = (
        db.UniqueConstraint('id_chefe', 'id_aluno', name='uix_chefe_aluno'),
    )
