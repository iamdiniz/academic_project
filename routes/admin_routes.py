from flask import Blueprint, request, flash, redirect, url_for
from flask_login import login_required
from services import (
    admin_bloquear_usuario as admin_bloquear_usuario_service,
    admin_desbloquear_usuario as admin_desbloquear_usuario_service
)

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/bloquear-usuario', methods=['POST'])
@login_required
def admin_bloquear_usuario():
    """Bloqueia usuário permanentemente"""
    email = request.form.get('email', '').strip().lower()

    sucesso, mensagem, redirect_url = admin_bloquear_usuario_service(email)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for(redirect_url))


@admin_bp.route('/admin/desbloquear-usuario', methods=['POST'])
@login_required
def admin_desbloquear_usuario():
    """Desbloqueia usuário"""
    email = request.form.get('email', '').strip().lower()

    sucesso, mensagem, redirect_url = admin_desbloquear_usuario_service(email)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for(redirect_url))