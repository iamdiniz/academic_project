from flask_sqlalchemy import SQLAlchemy

# Instância global do SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print("Tabelas criadas/atualizadas com sucesso!")
