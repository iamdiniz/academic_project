"""
Serviço de Autenticação - Funções de autenticação movidas do app.py.
Código movido para organizar responsabilidades, mantendo a lógica original.
"""

from functools import wraps
from flask import session, flash, redirect, url_for, request, render_template
from flask_login import login_user, current_user
from werkzeug.security import check_password_hash
from domain import Chefe, InstituicaodeEnsino, TwoFactor, CURSOS_PADRAO
from .rate_limit_service import verificar_rate_limit, resetar_rate_limit
from .audit_log_service import registrar_log
from .password_validation_service import (
    validar_senha_minima, validar_confirmacao_senha,
    validar_campos_obrigatorios_instituicao, validar_campos_obrigatorios_chefe,
    PASSWORD_POLICY_MESSAGE
)
from .user_service import (
    verificar_email_duplicado_instituicao, criar_instituicao_ensino, criar_chefe,
    atualizar_perfil_chefe, atualizar_perfil_instituicao
)
from .course_service import obter_cursos_instituicao
from .rate_limit_service import usuarios_bloqueados


def load_user(user_id):
    """
    Carrega usuário - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        return Chefe.query.get(int(user_id))
    elif tipo_usuario == 'instituicao':
        return InstituicaodeEnsino.query.get(int(user_id))
    return None


def bloquear_chefe(f):
    """
    Decorator para bloquear chefes - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'chefe':
            flash("Acesso não permitido para o perfil chefe.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('auth.home'))
        return f(*args, **kwargs)
    return decorated_function


def bloquear_instituicao(f):
    """
    Decorator para bloquear instituições - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('tipo_usuario') == 'instituicao':
            flash("Acesso não permitido para o perfil instituição de ensino.", "danger")
            # Redireciona para a página inicial
            return redirect(url_for('auth.home'))
        return f(*args, **kwargs)
    return decorated_function


def processar_cadastro():
    """
    Processa o cadastro de usuários - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    if request.method == 'POST':
        tipo_usuario = request.form.get('tipo_usuario')
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')

        # Validação: política de senha
        if validar_senha_minima(senha):
            flash(PASSWORD_POLICY_MESSAGE, 'danger')
            return redirect(url_for('auth.cadastro'))

        if validar_confirmacao_senha(senha, confirmar_senha):
            flash('As senhas não coincidem!')
            return redirect(url_for('auth.cadastro'))

        if tipo_usuario == 'instituicao':
            instituicao_nome = request.form.get('instituicao_nome')
            endereco = request.form.get('endereco_instituicao')
            infraestrutura = request.form.get('infraestrutura')
            nota_mec = request.form.get('nota_mec')
            modalidades = request.form.get('modalidades')
            cursos_selecionados = request.form.getlist('cursos_selecionados')

            if validar_campos_obrigatorios_instituicao(nome, email, senha, instituicao_nome, endereco, cursos_selecionados):
                flash(
                    'Todos os campos obrigatórios para Instituição de Ensino devem ser preenchidos!')
                return redirect(url_for('auth.cadastro'))

            # Validação: não permitir e-mail duplicado
            if verificar_email_duplicado_instituicao(email):
                flash('Já existe uma instituição cadastrada com este e-mail.', 'danger')
                return redirect(url_for('auth.cadastro'))

            # Criar instituição usando o serviço
            dados_formulario = {
                'instituicao_nome': instituicao_nome,
                'email': email,
                'senha': senha,
                'infraestrutura': infraestrutura,
                'nota_mec': nota_mec,
                'cursos_selecionados': cursos_selecionados,
                'modalidades': modalidades,
                'nome': nome,
                'endereco': endereco
            }

            sucesso, mensagem, _ = criar_instituicao_ensino(dados_formulario)

            if sucesso:
                flash(mensagem, 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(mensagem, 'error')
                return redirect(url_for('auth.cadastro'))

        elif tipo_usuario == 'chefe':
            empresa_nome = request.form.get('empresa_nome')
            cargo = request.form.get('cargo')

            if validar_campos_obrigatorios_chefe(nome, email, senha, empresa_nome, cargo):
                flash('Todos os campos obrigatórios para Chefe devem ser preenchidos!')
                return redirect(url_for('auth.cadastro'))

            # Validação do cargo
            if cargo not in ['CEO', 'Gerente', 'Coordenador']:
                flash('Selecione um cargo válido!', 'danger')
                return redirect(url_for('auth.cadastro'))

            # Criar chefe usando o serviço
            dados_formulario = {
                'nome': nome,
                'email': email,
                'senha': senha,
                'empresa_nome': empresa_nome,
                'cargo': cargo
            }

            sucesso, mensagem, _ = criar_chefe(dados_formulario)

            if sucesso:
                flash(mensagem, 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(mensagem, 'error')
                return redirect(url_for('auth.cadastro'))

        else:
            flash('Tipo de usuário inválido!')
            return redirect(url_for('auth.cadastro'))

    return render_template('cadastro.html', cursos_padrao=CURSOS_PADRAO)


def processar_login():
    """
    Processa o login de usuários - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    if request.method == 'POST':
        # =============================================================================
        # OBTÉM DADOS DO USUÁRIO
        # =============================================================================
        email = request.form['email']
        senha = request.form['senha']

        # =============================================================================
        # VERIFICAÇÃO DE BLOQUEIO PERMANENTE
        # =============================================================================
        if email in usuarios_bloqueados:
            flash(
                "Sua conta foi bloqueada permanentemente. Redefina a senha para continuar.", "danger")
            return render_template('login.html')

        # =============================================================================
        # VERIFICAÇÃO DE RATE LIMITING ANTES DAS CREDENCIAIS
        # =============================================================================
        # Verifica rate limiting ANTES de verificar credenciais
        permitido, mensagem_rate_limit, _ = verificar_rate_limit(email)

        if not permitido:
            flash(mensagem_rate_limit, "danger")
            return render_template('login.html')

        # =============================================================================
        # VERIFICAÇÃO DE CREDENCIAIS
        # =============================================================================
        chefe = Chefe.query.filter_by(email=email).first()
        instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()

        usuario_valido = None
        tipo_usuario = None

        if chefe and check_password_hash(chefe.senha, senha):
            usuario_valido = chefe
            tipo_usuario = 'chefe'
        elif instituicao and check_password_hash(instituicao.senha, senha):
            usuario_valido = instituicao
            tipo_usuario = 'instituicao'

        # =============================================================================
        # LOGIN BEM-SUCEDIDO - RESETA RATE LIMITING
        # =============================================================================
        if usuario_valido:
            # Reseta histórico de tentativas após login correto
            resetar_rate_limit(email)

            # Verifica 2FA
            tf = TwoFactor.query.filter_by(
                user_type=tipo_usuario,
                user_id=usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao,
                enabled=True
            ).first()

            if tf:
                session['pending_user'] = {
                    'tipo': tipo_usuario,
                    'id': usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao
                }
                return redirect(url_for('two.two_factor_verify'))
            else:
                session['user_id'] = usuario_valido.id_chefe if tipo_usuario == 'chefe' else usuario_valido.id_instituicao
                session['tipo_usuario'] = tipo_usuario
                login_user(usuario_valido)
                registrar_log(
                    'login',
                    usuario_valido.nome if tipo_usuario == 'chefe' else usuario_valido.nome_instituicao,
                    'chefe' if tipo_usuario == 'chefe' else 'reitor',
                    tipo_usuario
                )
                return redirect(url_for('auth.home'))

        # =============================================================================
        # LOGIN FALHADO - EXIBE MENSAGEM
        # =============================================================================
        # Rate limiting já foi verificado antes das credenciais
        if mensagem_rate_limit:
            flash(
                f"E-mail ou senha inválidos. {mensagem_rate_limit}", "warning")
        else:
            flash("E-mail ou senha inválidos.", "danger")

    return render_template('login.html')


def processar_perfil():
    """
    Processa a atualização de perfil - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    tipo_usuario = session.get('tipo_usuario')

    if request.method == 'POST':
        # Atualizar informações do chefe
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get_or_404(current_user.id_chefe)

            # Validação da senha se fornecida
            senha_nova = request.form.get('senha', '')
            if senha_nova and validar_senha_minima(senha_nova):
                flash(PASSWORD_POLICY_MESSAGE, "danger")
                return redirect(url_for('users.perfil'))

            # Preparar dados do formulário
            dados_formulario = {
                'nome': request.form['nome'],
                'email': request.form['email'],
                'cargo': request.form['cargo'],
                'nome_empresa': request.form.get('nome_empresa', ''),
                'senha': senha_nova
            }

            # Atualizar perfil usando o serviço
            sucesso, mensagem = atualizar_perfil_chefe(chefe, dados_formulario)

            if sucesso:
                flash(mensagem, "success")
            else:
                flash(mensagem, "danger")

            return redirect(url_for('users.perfil'))

        # Atualizar informações da instituição
        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get_or_404(
                current_user.id_instituicao)

            # Validação da senha se fornecida
            senha_nova = request.form.get('senha', '')
            if senha_nova and validar_senha_minima(senha_nova):
                flash(PASSWORD_POLICY_MESSAGE, "danger")
                return redirect(url_for('users.perfil'))

            # Preparar dados do formulário
            dados_formulario = {
                'nome_instituicao': request.form['nome_instituicao'],
                'reitor': request.form['reitor'],
                'email': request.form['email'],
                'endereco_instituicao': request.form['endereco_instituicao'],
                'infraestrutura': request.form['infraestrutura'],
                'nota_mec': request.form['nota_mec'],
                'modalidades': request.form['modalidades'],
                'senha': senha_nova
            }

            # Atualizar perfil usando o serviço
            sucesso, mensagem = atualizar_perfil_instituicao(
                instituicao, dados_formulario)

            if sucesso:
                flash(mensagem, "success")
            else:
                flash(mensagem, "danger")

            return redirect(url_for('users.perfil'))

    # Exibir informações do perfil
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = obter_cursos_instituicao(
            current_user.id_instituicao)
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('auth.home'))

    return render_template('perfil.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao)
