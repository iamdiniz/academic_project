from flask_login import LoginManager

# Instância global do LoginManager
login_manager = LoginManager()

def init_login(app):
    """Inicializa o Flask-Login com a aplicação Flask"""
    login_manager.init_app(app)
    login_manager.login_view = app.config.get('LOGIN_VIEW', 'auth.login')
