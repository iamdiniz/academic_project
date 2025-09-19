"""
Serviço de Autenticação de Dois Fatores - Gerencia 2FA.
Código movido do app.py para organizar responsabilidades.
"""

import pyotp
import base64
import io
import qrcode
from flask import session, flash, redirect, url_for, request, render_template
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
from domain import TwoFactor, Chefe, InstituicaodeEnsino, db
from .audit_log_service import registrar_log
from .rate_limit_service import resetar_rate_limit


def _get_or_create_2fa_record(tipo_usuario, user_id):
    tf = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id).first()
    if not tf:
        tf = TwoFactor(user_type=tipo_usuario, user_id=user_id,
                       otp_secret=pyotp.random_base32(), enabled=False)
        db.session.add(tf)
        db.session.commit()
    return tf


def _generate_qr_data_uri(issuer, account_name, secret):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=issuer)
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    data = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{data}", uri


def processar_two_factor_setup():
    """
    Processa a configuração de 2FA - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        account_name = usuario.email or usuario.nome
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        account_name = usuario.email or usuario.nome_instituicao
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('auth.home'))

    tf = _get_or_create_2fa_record(tipo_usuario, user_id)
    qr_data_uri, otpauth_uri = _generate_qr_data_uri(
        'DashTalent', account_name, tf.otp_secret)

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        totp = pyotp.TOTP(tf.otp_secret)
        if totp.verify(code, valid_window=1):
            tf.enabled = True
            db.session.commit()
            flash('Autenticação de dois fatores ativada com sucesso.', 'success')
            return redirect(url_for('users.configuracoes'))
        else:
            flash('Código inválido. Tente novamente.', 'danger')

    return render_template('2fa_setup.html', qr_data_uri=qr_data_uri, otpauth_uri=otpauth_uri, secret=tf.otp_secret)


def processar_two_factor_verify():
    """
    Processa a verificação de 2FA - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    pending = session.get('pending_user')
    if not pending:
        return redirect(url_for('auth.login'))

    tipo = pending.get('tipo')
    user_id = pending.get('id')
    tf = TwoFactor.query.filter_by(
        user_type=tipo, user_id=user_id, enabled=True).first()
    if not tf:
        # Se não há 2FA ativo, volte ao login
        session.pop('pending_user', None)
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        code = request.form.get('code', '').strip()
        totp = pyotp.TOTP(tf.otp_secret)
        if totp.verify(code, valid_window=1):
            # Completa o login
            if tipo == 'chefe':
                user = Chefe.query.get_or_404(user_id)
                session['user_id'] = user.id_chefe
                session['tipo_usuario'] = 'chefe'
                login_user(user)
                registrar_log('login', user.nome, user.cargo, 'chefe')
            elif tipo == 'instituicao':
                user = InstituicaodeEnsino.query.get_or_404(user_id)
                session['user_id'] = user.id_instituicao
                session['tipo_usuario'] = 'instituicao'
                login_user(user)
                registrar_log('login', user.nome_instituicao,
                              'reitor', 'instituicao')

            # Reseta histórico de tentativas após login bem-sucedido com 2FA
            # Obtém o email do usuário para resetar o rate limiting
            if tipo == 'chefe':
                email_usuario = user.email
            else:
                email_usuario = user.email
            resetar_rate_limit(email_usuario)

            session.pop('pending_user', None)
            return redirect(url_for('auth.home'))
        else:
            flash('Código 2FA inválido.', 'danger')

    return render_template('2fa_verify.html')


def processar_two_factor_disable():
    """
    Processa a desativação de 2FA - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        user_id = usuario.id_chefe
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        user_id = usuario.id_instituicao
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('auth.home'))

    tf = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id, enabled=True).first()
    if not tf:
        flash("2FA não está ativo para esta conta.", "warning")
        return redirect(url_for('users.configuracoes'))

    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '').strip()
        codigo_2fa = request.form.get('codigo_2fa', '').strip()

        # Verificar senha atual
        if not check_password_hash(usuario.senha, senha_atual):
            flash('Senha atual incorreta.', 'danger')
            return render_template('2fa_disable.html')

        # Verificar código 2FA
        totp = pyotp.TOTP(tf.otp_secret)
        if not totp.verify(codigo_2fa, valid_window=1):
            flash('Código 2FA inválido.', 'danger')
            return render_template('2fa_disable.html')

        # Desativar 2FA
        tf.enabled = False
        db.session.commit()

        # Log de auditoria
        if tipo_usuario == 'chefe':
            registrar_log('2fa_disable', usuario.nome, usuario.cargo, 'chefe')
        else:
            registrar_log('2fa_disable', usuario.nome_instituicao,
                          'reitor', 'instituicao')

        flash('2FA desativado com sucesso.', 'success')
        return redirect(url_for('users.configuracoes'))

    return render_template('2fa_disable.html')
