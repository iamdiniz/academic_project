#!/usr/bin/env python3
"""
Script simples para criar as tabelas no banco de dados
"""

import os
import sys

# Adiciona o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from dotenv import load_dotenv

    # Carrega variáveis de ambiente
    load_dotenv()

    # Cria uma aplicação Flask simples
    app = Flask(__name__)

    # Configuração do banco de dados - tenta diferentes configurações
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Tenta configuração padrão para Docker
        DATABASE_URL = "mysql+pymysql://root:jonas1385@localhost:3307/educ_invest?charset=utf8mb4"
        print(f"Usando configuração padrão: {DATABASE_URL}")
    else:
        print(f"Usando DATABASE_URL do .env: {DATABASE_URL}")

    # Adapta para SQLAlchemy se necessário
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializa SQLAlchemy
    db = SQLAlchemy(app)

    # Define os modelos aqui para evitar dependências
    class InstituicaodeEnsino(db.Model):
        __tablename__ = 'instituicao_ensino'
        id_instituicao = db.Column(
            db.Integer, primary_key=True, autoincrement=True)
        nome_instituicao = db.Column(db.String(100), nullable=False)
        endereco_instituicao = db.Column(db.String(200))
        reitor = db.Column(db.String(100))
        infraestrutura = db.Column(db.Text)
        nota_mec = db.Column(db.Integer)
        modalidades = db.Column(db.String(50))
        email = db.Column(db.String(100), unique=True, nullable=False)
        senha = db.Column(db.String(255), nullable=False)

    class Chefe(db.Model):
        __tablename__ = 'chefe'
        id_chefe = db.Column(db.Integer, primary_key=True, autoincrement=True)
        nome = db.Column(db.String(100), nullable=False)
        cargo = db.Column(db.String(50))
        nome_empresa = db.Column(db.String(100))
        email = db.Column(db.String(100), unique=True, nullable=False)
        senha = db.Column(db.String(255), nullable=False)

    class Aluno(db.Model):
        __tablename__ = 'alunos'
        id_aluno = db.Column(db.Integer, primary_key=True, autoincrement=True)
        nome_jovem = db.Column(db.String(100), nullable=False)
        data_nascimento = db.Column(db.Date)
        curso = db.Column(db.String(100))
        periodo = db.Column(db.String(20))
        contato_jovem = db.Column(db.String(20))
        email = db.Column(db.String(100), unique=True, nullable=False)
        id_instituicao = db.Column(db.Integer, db.ForeignKey(
            'instituicao_ensino.id_instituicao'))

    class Curso(db.Model):
        __tablename__ = 'curso'
        id_curso = db.Column(db.Integer, primary_key=True, autoincrement=True)
        nome = db.Column(db.String(100), nullable=False)
        id_instituicao = db.Column(db.Integer, db.ForeignKey(
            'instituicao_ensino.id_instituicao'))

    class SkillsDoAluno(db.Model):
        __tablename__ = 'skills_do_aluno'
        id_skills = db.Column(db.Integer, primary_key=True, autoincrement=True)
        id_aluno = db.Column(db.Integer, db.ForeignKey(
            'alunos.id_aluno'), unique=True)
        hard_skills_json = db.Column(db.Text)
        soft_skills_json = db.Column(db.Text)

    class Acompanhamento(db.Model):
        __tablename__ = 'acompanhamento'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        id_chefe = db.Column(db.Integer, db.ForeignKey(
            'chefe.id_chefe'), nullable=False)
        id_aluno = db.Column(db.Integer, db.ForeignKey(
            'alunos.id_aluno'), nullable=False)
        data_acompanhamento = db.Column(
            db.DateTime, server_default=db.func.now())

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

    class Indicacao(db.Model):
        __tablename__ = 'indicacoes'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        id_chefe = db.Column(db.Integer, db.ForeignKey(
            'chefe.id_chefe'), nullable=False)
        id_aluno = db.Column(db.Integer, db.ForeignKey(
            'alunos.id_aluno'), nullable=False)
        data_indicacao = db.Column(db.DateTime, server_default=db.func.now())

    def create_tables():
        """Cria todas as tabelas no banco de dados"""
        with app.app_context():
            print("Criando tabelas no banco de dados...")
            print(f"URL do banco: {DATABASE_URL}")

            try:
                # Testa a conexão primeiro
                print("Testando conexão com o banco...")
                db.engine.connect()
                print("✅ Conexão com banco estabelecida!")

                # Cria todas as tabelas
                db.create_all()
                print("✅ Tabelas criadas com sucesso!")

                # Lista todas as tabelas criadas
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()

                print("\n📋 Tabelas criadas:")
                for table in tables:
                    print(f"  - {table}")

                print(f"\n📊 Total de tabelas: {len(tables)}")

                # Verifica se as tabelas problemáticas foram criadas
                if 'indicacoes' in tables:
                    print("✅ Tabela 'indicacoes' criada com sucesso!")
                else:
                    print("❌ Tabela 'indicacoes' NÃO foi criada!")

                if 'acompanhamento' in tables:
                    print("✅ Tabela 'acompanhamento' criada com sucesso!")
                else:
                    print("❌ Tabela 'acompanhamento' NÃO foi criada!")

            except Exception as e:
                print(f"❌ Erro ao criar tabelas: {str(e)}")
                print("\n💡 Dicas para resolver:")
                print("1. Certifique-se de que o Docker está rodando")
                print("2. Execute: docker-compose up -d")
                print("3. Aguarde o banco de dados inicializar")
                print("4. Tente novamente")
                return False

            return True

    if __name__ == "__main__":
        success = create_tables()
        if success:
            print("\n🎉 Script executado com sucesso!")
            print("Agora as rotas 'minhas_selecoes' e 'acompanhar' devem funcionar!")
        else:
            print("\n💥 Script falhou!")

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Certifique-se de que todas as dependências estão instaladas:")
    print("pip install flask flask-sqlalchemy python-dotenv pymysql")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
