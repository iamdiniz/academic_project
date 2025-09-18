"""
Serviço de Recuperação de Senha
Contém toda a lógica para recuperação de senha de usuários
"""

import secrets
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from flask import session, flash, redirect, url_for, request, render_template
from domain import db, Chefe, InstituicaodeEnsino, ResetarSenha
from .email_service import enviar_email
from .rate_limit_service import desbloquear_usuario


def verificar_email_existe(email):
    """
    Verifica se o email existe no sistema (chefe ou instituição)
    Retorna: (existe, tipo_usuario, user_id, nome_usuario)
    """
    chefe = Chefe.query.filter_by(email=email).first()
    instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

    if chefe:
        return True, 'chefe', chefe.id_chefe, chefe.nome
    elif instituicao:
        return True, 'instituicao', instituicao.id_instituicao, instituicao.nome_instituicao
    else:
        return False, None, None, None


def verificar_codigo_recente(email):
    """
    Verifica se já foi enviado um código recentemente (últimos 2 minutos)
    Retorna: (tem_codigo_recente, codigo_recente)
    """
    codigo_recente = ResetarSenha.query.filter_by(
        email=email,
        used=False
    ).filter(ResetarSenha.created_at > datetime.now() - timedelta(minutes=2)).first()

    return codigo_recente is not None, codigo_recente


def gerar_codigo_verificacao():
    """
    Gera um código de 6 dígitos para verificação
    """
    return ''.join(secrets.choice(string.digits) for _ in range(6))


def criar_solicitacao_reset(email, codigo, user_type, user_id):
    """
    Cria uma nova solicitação de reset de senha no banco
    Retorna: (sucesso, reset_request)
    """
    try:
        reset_request = ResetarSenha(
            email=email,
            codigo=codigo,
            user_type=user_type,
            user_id=user_id,
            created_at=datetime.now()
        )

        db.session.add(reset_request)
        db.session.commit()
        return True, reset_request
    except IntegrityError:
        db.session.rollback()
        return False, None


def enviar_email_recuperacao(email, nome_usuario, codigo):
    """
    Envia email com código de recuperação
    Retorna: (sucesso, mensagem)
    """
    corpo = f"""
    Olá {nome_usuario},

    Você solicitou a recuperação de senha no DashTalent.
    Seu código de verificação é: {codigo}

    Este código expira em 10 minutos.
    Se você não solicitou esta recuperação, ignore este email.

    Atenciosamente,
    Equipe DashTalent
    """

    return enviar_email(email, "Código de Recuperação de Senha - DashTalent", corpo)


def processar_solicitacao_recuperacao(email):
    """
    Processa uma solicitação de recuperação de senha
    Retorna: (sucesso, mensagem, redirect_url)
    """
    # Verificar se email existe
    existe, tipo_usuario, user_id, nome_usuario = verificar_email_existe(email)
    if not existe:
        return False, "Email não cadastrado no sistema.", None

    # Verificar se já foi enviado código recentemente
    tem_codigo_recente, _ = verificar_codigo_recente(email)
    if tem_codigo_recente:
        return False, "Um código já foi enviado recentemente. Aguarde 2 minutos.", None

    # Gerar código
    codigo = gerar_codigo_verificacao()

    # Salvar no banco
    sucesso, reset_request = criar_solicitacao_reset(
        email, codigo, tipo_usuario, user_id)
    if not sucesso:
        return False, "Erro ao processar solicitação. Tente novamente.", None

    # Enviar email
    ok, msg = enviar_email_recuperacao(email, nome_usuario, codigo)
    if ok:
        return True, "Código de verificação enviado para seu email.", "verificar_codigo"
    else:
        return False, msg, None


def buscar_codigos_validos(email):
    """
    Busca todos os códigos válidos para o email (não usados e dentro do prazo)
    Retorna: lista de reset_requests válidos
    """
    return ResetarSenha.query.filter_by(
        email=email,
        used=False
    ).filter(ResetarSenha.created_at > datetime.now() - timedelta(minutes=10)).all()


def verificar_codigo_digitado(email, codigo_digitado):
    """
    Verifica se o código digitado é válido
    Retorna: (sucesso, mensagem, reset_request, redirect_url)
    """
    # Buscar códigos válidos
    reset_requests = buscar_codigos_validos(email)

    if not reset_requests:
        return False, "Código inválido ou expirado.", None, None

    # Procurar o código digitado
    reset_request = None
    for rr in reset_requests:
        if rr.codigo == codigo_digitado:
            reset_request = rr
            break

    # Se não encontrou o código correto, incrementar tentativas
    if not reset_request:
        # Pega o código mais recente para incrementar tentativas
        reset_request = max(reset_requests, key=lambda r: r.created_at)
        reset_request.tentativas += 1
        db.session.commit()

        if reset_request.tentativas >= 3:
            return False, "Muitas tentativas. Solicite um novo código.", None, "esqueceu_senha"
        else:
            return False, "Código incorreto.", None, None

    # Código correto encontrado - verificar tentativas
    if reset_request.tentativas >= 3:
        return False, "Muitas tentativas. Solicite um novo código.", None, "esqueceu_senha"

    # Código correto e tentativas < 3 - sucesso
    return True, "Código verificado com sucesso!", reset_request, "nova_senha"


def validar_token_reset(reset_token):
    """
    Valida se o token de reset é válido
    Retorna: (valido, reset_request, mensagem)
    """
    if not reset_token:
        return False, None, "Sessão inválida. Inicie o processo novamente."

    reset_request = ResetarSenha.query.get(reset_token)
    if not reset_request or reset_request.used:
        return False, None, "Token inválido ou já utilizado."

    return True, reset_request, None


def validar_nova_senha(nova_senha, confirmar_senha):
    """
    Valida a nova senha
    Retorna: (valida, mensagem)
    """
    if not nova_senha or not confirmar_senha:
        return False, "Todos os campos são obrigatórios."

    if len(nova_senha) < 6:
        return False, "A senha deve ter pelo menos 6 caracteres."

    if nova_senha != confirmar_senha:
        return False, "As senhas não coincidem."

    return True, None


def atualizar_senha_usuario(reset_request, nova_senha):
    """
    Atualiza a senha do usuário
    Retorna: (sucesso, mensagem)
    """
    try:
        senha_hash = generate_password_hash(nova_senha)

        if reset_request.user_type == 'chefe':
            user = Chefe.query.get(reset_request.user_id)
            user.senha = senha_hash
        else:
            user = InstituicaodeEnsino.query.get(reset_request.user_id)
            user.senha = senha_hash

        # Marcar código como usado
        reset_request.used = True

        db.session.commit()

        # Liberar usuário do bloqueio permanente
        desbloquear_usuario(reset_request.email)

        return True, "Senha alterada com sucesso! Faça login com sua nova senha."

    except Exception:
        db.session.rollback()
        return False, "Erro ao alterar senha. Tente novamente."


def processar_nova_senha(reset_token, nova_senha, confirmar_senha):
    """
    Processa a definição de nova senha
    Retorna: (sucesso, mensagem, redirect_url)
    """
    # Validar token
    valido, reset_request, mensagem = validar_token_reset(reset_token)
    if not valido:
        return False, mensagem, "esqueceu_senha"

    # Validar senha
    valida, mensagem = validar_nova_senha(nova_senha, confirmar_senha)
    if not valida:
        return False, mensagem, None

    # Atualizar senha
    sucesso, mensagem = atualizar_senha_usuario(reset_request, nova_senha)
    if sucesso:
        return True, "Senha alterada com sucesso! Faça login com sua nova senha.", "login"
    else:
        return False, mensagem, None


def processar_esqueceu_senha():
    """
    Processa a solicitação de recuperação de senha - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if not email:
            flash("Por favor, informe seu email.", "danger")
            return render_template('esqueceu_senha.html')

        # Processar solicitação usando o serviço
        sucesso, mensagem, redirect_url = processar_solicitacao_recuperacao(
            email)

        if sucesso:
            flash(mensagem, "success")
            return redirect(url_for(redirect_url, email=email))
        else:
            flash(mensagem, "danger" if "não cadastrado" in mensagem else "warning")
            return render_template('esqueceu_senha.html')

    return render_template('esqueceu_senha.html')


def processar_verificar_codigo():
    """
    Processa a exibição da página de verificação de código - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    email = request.args.get('email')
    if not email:
        return redirect(url_for('esqueceu_senha'))
    return render_template('verificar_codigo.html', email=email)


def processar_verificar_codigo_post():
    """
    Processa a verificação do código digitado - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    email = request.form['email']
    codigo = request.form['codigo']

    if not email or not codigo:
        flash("Email e código são obrigatórios.", "danger")
        return render_template('verificar_codigo.html', email=email)

    # Verificar código usando o serviço
    sucesso, mensagem, reset_request, redirect_url = verificar_codigo_digitado(
        email, codigo)

    if sucesso:
        session['reset_token'] = reset_request.id
        flash(mensagem, "success")
        return redirect(url_for(redirect_url))
    else:
        if redirect_url:
            return redirect(url_for(redirect_url))
        else:
            flash(mensagem, "danger")
            return render_template('verificar_codigo.html', email=email)


def processar_nova_senha_page():
    """
    Processa a página de nova senha - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    # Validar token usando o serviço
    valido, reset_request, mensagem = validar_token_reset(
        session.get('reset_token'))
    if not valido:
        flash(mensagem, "danger")
        session.pop('reset_token', None)
        return redirect(url_for('esqueceu_senha'))

    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']

        # Processar nova senha usando o serviço
        sucesso, mensagem, redirect_url = processar_nova_senha(
            session.get('reset_token'), nova_senha, confirmar_senha)

        if sucesso:
            session.pop('reset_token', None)
            flash(mensagem, "success")
            return redirect(url_for(redirect_url))
        else:
            flash(mensagem, "danger")

    return render_template('nova_senha.html')
