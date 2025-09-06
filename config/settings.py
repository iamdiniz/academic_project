import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


class Config:
    """Configurações base da aplicação"""

    # Chave secreta do Flask
    SECRET_KEY = os.getenv(
        'FLASK_SECRET_KEY', 'sua-chave-secreta-super-segura-aqui-123456789')

    # Configuração do banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///instance/test.db")

    # Adapta para SQLAlchemy se necessário
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações do Flask-Login
    LOGIN_VIEW = 'auth.login'

    # Configurações de paginação
    ITEMS_PER_PAGE = 12


class DevelopmentConfig(Config):
    """Configurações para desenvolvimento"""
    DEBUG = True


class ProductionConfig(Config):
    """Configurações para produção"""
    DEBUG = False


class TestingConfig(Config):
    """Configurações para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Configuração atual baseada na variável de ambiente


def get_config():
    """Retorna a configuração baseada na variável de ambiente FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'default')
    return config.get(env, config['default'])
