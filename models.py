from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class InstituicaodeEnsino(db.Model, UserMixin):
    __tablename__ = 'instituicao_de_ensino'

    id_instituicao = db.Column(db.Integer, primary_key=True)
    nome_instituicao = db.Column(db.String(100), nullable=False)
    endereco_instituicao = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    infraestrutura = db.Column(db.Text, nullable=False)
    nota_mec = db.Column(db.Numeric, nullable=False)
    areas_de_formacao = db.Column(db.Text, nullable=False)
    modalidades = db.Column(db.String(255), nullable=False)
    quantidade_de_alunos = db.Column(db.Integer, nullable=False)
    reitor = db.Column(db.String(255), nullable=False)

    def get_id(self):
        return str(self.id_instituicao)


class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(255), nullable=False)
    id_instituicao = db.Column(db.Integer, db.ForeignKey(
        'instituicao_de_ensino.id_instituicao'), nullable=False)

    instituicao = db.relationship('InstituicaodeEnsino', backref='cursos')


class Aluno(db.Model):
    __tablename__ = 'alunos'

    id_aluno = db.Column(db.Integer, primary_key=True)
    nome_jovem = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    contato_jovem = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True)
    endereco_jovem = db.Column(db.String(255))
    id_instituicao = db.Column(db.Integer, db.ForeignKey(
        'instituicao_de_ensino.id_instituicao'))
    curso = db.Column(db.String(255))
    formacao = db.Column(db.String(255))
    periodo = db.Column(db.Integer)
    indicado_por = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'))  # Relacionamento com Chefe

    # Relacionamento reverso
    chefe = db.relationship('Chefe', backref='alunos_indicados')


class Chefe(db.Model, UserMixin):
    __tablename__ = 'chefe'

    id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cargo = db.Column(db.String(50), nullable=False)
    # Pode ser nulo, mas deve ser único se fornecido
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(255), nullable=False)
    nome_empresa = db.Column(db.String(100))

    def get_id(self):
        return str(self.id_chefe)


class SkillsDoAluno(db.Model):
    __tablename__ = 'skills_do_aluno'

    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), primary_key=True)
    # Hard skills dinâmicas por curso (JSON)
    hard_skills_json = db.Column(db.Text)
    soft_skills_json = db.Column(db.Text)  # Soft skills detalhadas (JSON)
    aluno = db.relationship(
        'Aluno', backref=db.backref('skills', uselist=False))


class Acompanhamento(db.Model):
    __tablename__ = 'acompanhamento'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    data_acompanhamento = db.Column(db.DateTime, server_default=db.func.now())

    chefe = db.relationship('Chefe', backref='acompanhamentos')
    aluno = db.relationship('Aluno', backref='acompanhamentos')

    __table_args__ = (
        db.UniqueConstraint('id_chefe', 'id_aluno', name='uix_chefe_aluno'),
    )


class SkillsHistorico(db.Model):
    __tablename__ = 'skills_historico'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    data = db.Column(db.DateTime, server_default=db.func.now())
    hard_skills_json = db.Column(db.Text)
    soft_skills_json = db.Column(db.Text)

    aluno = db.relationship('Aluno', backref='historicos')
    chefe = db.relationship('Chefe', backref='historicos')


class Indicacao(db.Model):
    __tablename__ = 'indicacoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_chefe = db.Column(db.Integer, db.ForeignKey(
        'chefe.id_chefe'), nullable=False)
    id_aluno = db.Column(db.Integer, db.ForeignKey(
        'alunos.id_aluno'), nullable=False)
    data_indicacao = db.Column(db.DateTime, server_default=db.func.now())

    chefe = db.relationship('Chefe', backref='indicacoes')
    aluno = db.relationship('Aluno', backref='indicacoes')

    __table_args__ = (
        db.UniqueConstraint('id_chefe', 'id_aluno',
                            name='uix_chefe_aluno_indicacao'),
    )
