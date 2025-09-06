#!/usr/bin/env python3
"""
Script para inicializar o banco de dados e criar todas as tabelas
"""

from app import create_app
from extensions.database import db
from models.instituicao import InstituicaodeEnsino
from models.chefe import Chefe
from models.aluno import Aluno
from models.curso import Curso
from models.skills import SkillsDoAluno
from models.acompanhamento import Acompanhamento
from models.historico import SkillsHistorico
from models.indicacao import Indicacao


def init_database():
    """Inicializa o banco de dados e cria todas as tabelas"""
    app = create_app()

    with app.app_context():
        print("Criando todas as tabelas...")

        # Importa todos os modelos para garantir que sejam registrados
        print("Registrando modelos...")

        # Cria todas as tabelas
        db.create_all()

        print("Tabelas criadas com sucesso!")
        print("\nTabelas criadas:")

        # Lista todas as tabelas criadas
        inspector = db.inspect(db.engine)
        for table_name in inspector.get_table_names():
            print(f"  - {table_name}")

        print(f"\nTotal de tabelas: {len(inspector.get_table_names())}")


if __name__ == "__main__":
    init_database()
