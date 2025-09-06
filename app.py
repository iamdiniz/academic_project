from flask import Flask
from config.settings import get_config
from validators.decorators import bloquear_instituicao
from extensions.database import init_db
from extensions.login import init_login
from extensions.user_loader import load_user
from routes.auth import auth_bp
from routes.main import main_bp


def create_app(config_name=None):
    """
    Factory function para criar a aplicação Flask

    Args:
        config_name (str): Nome da configuração a ser usada

    Returns:
        Flask: Instância da aplicação Flask configurada
    """
    app = Flask(__name__)

    # Carrega configurações
    app.config.from_object(get_config())

    # Inicializa extensões
    init_db(app)
    init_login(app)

    # Configura o user loader do Flask-Login
    from extensions.login import login_manager
    login_manager.user_loader(load_user)
    login_manager.login_view = 'auth.login'

    # Registra blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # Registra outras rotas (serão movidas para blueprints separados)
    _register_remaining_routes(app)

    return app


def _register_remaining_routes(app):
    """
    Registra rotas que ainda não foram movidas para blueprints
    Esta função será removida conforme as rotas são organizadas
    """
    # Importa as rotas restantes organizadas
    from routes.remaining_routes import register_remaining_routes
    register_remaining_routes(app)


def _import_routes_from_original_app(app):
    """Obsoleto: rotas legadas migradas para blueprint."""
    return


# Criação da aplicação
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0') # host para expor o servidor para fora do container
