from flask import Blueprint

def register_blueprints(app):
    """Registra todos os blueprints no app Flask."""
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .chefes_routes import chefe_bp
    from .ie_routes import instituicao_bp
    from .esqueceu_senha_routes import esquece_bp
    from .two_factor_routes import two_bp
    from .users_routes import users_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chefe_bp)
    app.register_blueprint(instituicao_bp)
    app.register_blueprint(esquece_bp)
    app.register_blueprint(two_bp, url_prefix='/2fa')
    app.register_blueprint(users_bp)
