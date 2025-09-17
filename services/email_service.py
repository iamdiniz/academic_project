"""
Serviço de Email - Gerencia o envio de emails do sistema.
Código movido do app.py para organizar responsabilidades.
"""

import os
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def gerar_codigo_verificacao():
    """Gera um código de 6 dígitos para verificação"""
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def enviar_email(email_destino, assunto, corpo):
    """Função genérica e segura para envio de emails"""
    try:
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_user = os.getenv('SMTP_USER')
        smtp_password = os.getenv('SMTP_PASSWORD')

        if not smtp_user or not smtp_password:
            raise RuntimeError("Credenciais SMTP não configuradas no .env")

        # Montar mensagem
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email_destino
        msg['Subject'] = assunto
        msg.attach(MIMEText(corpo, 'plain'))

        # Enviar email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)

        return True, "Email enviado com sucesso"

    except Exception as e:
        print(f"[ERRO SMTP] {e}")
        return False, f"Erro ao enviar email: {str(e)}"
