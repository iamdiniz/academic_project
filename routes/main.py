from flask import Blueprint, render_template, session, redirect, url_for
from flask_login import login_required

# Blueprint para rotas principais
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Rota raiz - redireciona para carousel"""
    return redirect(url_for('main.carousel'))


@main_bp.route('/carousel')
def carousel():
    """Rota para página de carousel"""
    return render_template('carousel.html')


@main_bp.route('/home')
@login_required
def home():
    """Rota para página inicial após login"""
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        return render_template('home_chefe.html')
    elif tipo_usuario == 'instituicao':
        return render_template('home_instituicao.html')
    else:
        from flask import flash, redirect, url_for
        flash("Tipo de usuário inválido. Faça login novamente.", "danger")
        return redirect(url_for('auth.login'))


# Rotas de redirecionamento removidas para evitar loops infinitos
# As rotas funcionais estão definidas em remaining_routes.py
