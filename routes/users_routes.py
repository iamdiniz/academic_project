from flask import Blueprint, render_template, session, flash, redirect, url_for
from flask_login import login_required, current_user
from services import (
    processar_perfil,
    obter_cursos_instituicao
)
from domain import Chefe, InstituicaodeEnsino, TwoFactor

users_bp = Blueprint('users', __name__)

@users_bp.route('/carousel')
def carousel():
    """Página inicial do carousel."""
    return render_template('carousel.html')


@users_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do usuário."""
    return processar_perfil()


@users_bp.route('/configuracoes', methods=['GET', 'POST'])
@login_required
def configuracoes():
    """Página de configurações do usuário."""
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = obter_cursos_instituicao(
            current_user.id_instituicao)
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('auth.home'))

    # Verificar se 2FA está ativo
    tf_enabled = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id, enabled=True).first() is not None

    return render_template('configuracoes.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao, two_factor_enabled=tf_enabled)
