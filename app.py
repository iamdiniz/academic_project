from flask import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import os
from flask_wtf.csrf import generate_csrf
from domain import db
from services import load_user
# usuarios_bloqueados removido - não usado diretamente no app.py

from routes import register_blueprints

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key:
    raise RuntimeError(
        "A variável FLASK_SECRET_KEY não está definida no ambiente!")

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "A variável DATABASE_URL não está definida no ambiente!")


if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)


app.config['SQLALCHEMY_DATABASE_URI'] = database_url
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # Atualizado para usar blueprint


csrf = CSRFProtect(app)


# Comentado temporariamente para evitar erro de conexão
with app.app_context():
    db.create_all()  # Cria tabelas do banco
    print("Tabelas criadas com sucesso!")


@login_manager.user_loader
def load_user_wrapper(user_id):
    """Carrega usuário para Flask-Login."""
    return load_user(user_id)


register_blueprints(app)


# Configuração CSRF e cookies baseada no ambiente
# Verifica se está em produção para aplicar configurações seguras
is_production = os.getenv('FLASK_ENV') == 'production'

if is_production:
    # Configurações seguras para produção
    app.config.update(
        SESSION_COOKIE_SAMESITE="Strict",
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        WTF_CSRF_TIME_LIMIT=3600
    )
else:
    # Configurações para desenvolvimento
    app.config.update(
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True
    )


@app.context_processor
def inject_csrf_token():
    """Injeta token CSRF nos templates."""
    return dict(csrf_token=generate_csrf)


@app.after_request
def set_csrf_cookie(response):
    """Define cookie CSRF com configurações baseadas no ambiente."""
    try:
        csrf_token_value = generate_csrf()
        response.set_cookie(
            "csrf_token",
            csrf_token_value,
            secure=is_production,  # True em produção, False em desenvolvimento
            httponly=True,  # Previne acesso via JavaScript
            samesite="Strict" if is_production else "Lax",
            path="/"
        )
    except (ValueError, TypeError):
        # Falha silenciosa se não conseguir gerar token CSRF
        pass
    return response


@app.after_request
def set_security_headers(response):
    """Define headers de segurança para proteger contra ataques comuns."""
    # Previne MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Previne clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # Ativa proteção XSS do navegador
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # Força HTTPS em produção
    if is_production:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Content Security Policy básico
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'"
        )

    return response


if __name__ == "__main__":
    # Configuração de debug baseada no ambiente
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Host para acesso externo
    app.run(debug=debug_mode, host='0.0.0.0')
