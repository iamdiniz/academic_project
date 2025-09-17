"""
Serviço de Autenticação de Dois Fatores - Gerencia 2FA.
Código movido do app.py para organizar responsabilidades.
"""

import pyotp
import base64
import io
import qrcode
from domain.models import TwoFactor, db


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
