from functools import wraps
from flask import Flask, render_template, url_for, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from unidecode import unidecode
from urllib.parse import unquote
from math import ceil
from dotenv import load_dotenv
import pyotp
import base64
import io
import qrcode
from datetime import datetime, timedelta
from flask_wtf import CSRFProtect
import re
import json
import pytz
import os
import time
from flask_wtf.csrf import generate_csrf
from domain import (
    db,
    Chefe,
    InstituicaodeEnsino,
    Curso,
    Aluno,
    SkillsDoAluno,
    SkillsHistorico,
    Acompanhamento,
    Indicacao,
    TwoFactor,
    LogAcesso,
    CURSOS_PADRAO,
    HARD_SKILLS_POR_CURSO,
    SOFT_SKILLS
)
from services import (
    verificar_rate_limit,
    resetar_rate_limit,
    bloquear_usuario_permanentemente,
    desbloquear_usuario,
    enviar_email,
    gerar_codigo_verificacao,
    _get_or_create_2fa_record,
    _generate_qr_data_uri,
    registrar_log,
    paginate_items,
    validar_email_formato,
    validar_periodo_formato,
    validar_contato_formato,
    validar_skill_valor,
    validar_senha_minima,
    validar_confirmacao_senha,
    validar_campos_obrigatorios_instituicao,
    validar_campos_obrigatorios_chefe,
    validar_campos_obrigatorios_aluno,
    validar_campos_obrigatorios_aluno_edicao,
    validar_skills_por_curso,
    load_user,
    bloquear_chefe,
    bloquear_instituicao,
    processar_alunos_indicados_por_chefe,
    processar_alunos_acompanhados_por_chefe,
    processar_alunos_por_instituicao,
    processar_skills_para_edicao,
    calcular_total_skills_por_habilidades,
    processar_aluno_com_skills,
    criar_instituicao_ensino,
    criar_chefe,
    atualizar_perfil_chefe,
    atualizar_perfil_instituicao,
    verificar_email_duplicado_instituicao,
    verificar_email_duplicado_chefe,
    processar_solicitacao_recuperacao,
    verificar_codigo_digitado,
    processar_nova_senha,
    validar_token_reset,
    # Novos serviços expandidos
    processar_cadastro,
    processar_login,
    processar_perfil,
    processar_two_factor_setup,
    processar_two_factor_verify,
    processar_two_factor_disable,
    processar_esqueceu_senha,
    processar_verificar_codigo,
    processar_verificar_codigo_post,
    processar_nova_senha_page,
    # Serviços existentes
    admin_bloquear_usuario as admin_bloquear_usuario_service,
    admin_desbloquear_usuario as admin_desbloquear_usuario_service,
    cadastrar_curso,
    obter_cursos_instituicao,
    obter_cursos_por_instituicao,
    indicar_aluno as indicar_aluno_service,
    remover_indicacao as remover_indicacao_service,
    acompanhar_aluno as acompanhar_aluno_service,
    remover_acompanhamento as remover_acompanhamento_service,
    obter_alunos_indicados,
    paginar_alunos_indicados,
    obter_historico_aluno,
    criar_snapshot_skills_inicial,
    salvar_historico_skills_atualizacao,
    cadastrar_aluno as cadastrar_aluno_service,
    remover_aluno as remover_aluno_service,
    obter_detalhes_aluno,
    atualizar_aluno,
    obter_alunos_por_curso,
    paginar_alunos_por_curso
)
from services.rate_limit_service import usuarios_bloqueados

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
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

# Rate limiting movido para services/rate_limit_service.py


# Comentado temporariamente para evitar erro de conexão
# with app.app_context():
#     db.create_all()  # Cria tabelas do banco
#     print("Tabelas criadas com sucesso!")


@login_manager.user_loader
def load_user_wrapper(user_id):
    """Carrega usuário para Flask-Login."""
    return load_user(user_id)


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    """Página de cadastro de usuários."""
    return processar_cadastro()


@app.route('/')
def index():
    """Redireciona para carousel."""
    return redirect(url_for('carousel'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    return processar_login()


@app.route('/home')
@login_required
def home():
    """Página inicial baseada no tipo de usuário."""
    tipo_usuario = session.get('tipo_usuario')

    if tipo_usuario == 'chefe':
        # Chefe
        return render_template('home_chefe.html')
    elif tipo_usuario == 'instituicao':
        # Instituição
        return render_template('home_instituicao.html')
    else:
        # Inválido
        flash("Tipo de usuário inválido. Faça login novamente.", "danger")
        return redirect(url_for('login'))


@app.route('/instituicaoEnsino')
@bloquear_instituicao
@login_required
def instituicao_ensino():
    """Lista instituições de ensino."""
    # Query
    instituicoes = InstituicaodeEnsino.query.all()

    # Count
    for instituicao in instituicoes:
        instituicao.quantidade_de_alunos = Aluno.query.filter_by(
            id_instituicao=instituicao.id_instituicao).count()

    # Build
    cursos_por_instituicao = obter_cursos_por_instituicao(instituicoes)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginate_items(instituicoes, page)

    return render_template(
        'instituicaoEnsino.html',
        instituicoes=pagination_result['items'],
        cursos_por_instituicao=cursos_por_instituicao,
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages']
    )


@app.route('/detalhes_instituicao/<int:id_instituicao>')
@login_required
def detalhes_instituicao(id_instituicao):
    """Mostra detalhes de uma instituição."""
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    cursos = obter_cursos_instituicao(id_instituicao)
    return render_template('detalhes_instituicao.html', instituicao=instituicao, cursos=cursos)


@app.route('/minhas_selecoes')
@bloquear_instituicao
@login_required
def minhas_selecoes():
    """Mostra alunos indicados pelo chefe."""
    if session.get('tipo_usuario') != 'chefe':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    chefe_id = current_user.id_chefe

    # Get
    alunos_com_skills = processar_alunos_indicados_por_chefe(chefe_id)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginate_items(alunos_com_skills, page)

    return render_template(
        'minhas_selecoes.html',
        alunos=pagination_result['items'],
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages']
    )


@app.route('/remover_indicacao/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def remover_indicacao(id_aluno):
    """Remove indicação de aluno."""
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = remover_indicacao_service(
        id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@app.route('/remover_aluno/<int:id_aluno>', methods=['POST'])
@login_required
def remover_aluno(id_aluno):
    """Remove um aluno do sistema."""
    sucesso, mensagem = remover_aluno_service(id_aluno)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for('alunos_instituicao'))


@app.route('/ver_alunos_por_curso', methods=['GET'])
@bloquear_instituicao
@login_required
def ver_alunos_por_curso():
    """Mostra alunos filtrados por curso."""
    inst_id = request.args.get('inst_id')
    curso = request.args.get('curso')
    filtro_tipo = request.args.get('filtro_tipo')
    periodo = request.args.get('periodo')
    habilidade = request.args.getlist('habilidade')  # Lista

    # Decode
    curso = unquote(curso).strip()

    alunos_com_skills, mensagem = obter_alunos_por_curso(
        inst_id, curso, periodo, habilidade)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginar_alunos_por_curso(alunos_com_skills, page)

    return render_template(
        'cardAlunos.html',
        alunos=pagination_result['items'],
        curso=curso,
        mensagem=mensagem,
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages'],
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS
    )


@app.route('/detalhes_aluno/<int:id_aluno>')
@bloquear_instituicao
@login_required
def detalhes_aluno(id_aluno):
    """Mostra detalhes de um aluno."""
    aluno, hard_labels, hard_values, soft_labels, soft_values = obter_detalhes_aluno(
        id_aluno)

    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('instituicao_ensino'))

    previous_url = request.args.get('previous', url_for('instituicao_ensino'))

    return render_template(
        'detalhes_aluno.html',
        aluno=aluno,
        hard_labels=hard_labels,
        hard_values=hard_values,
        soft_labels=soft_labels,
        soft_values=soft_values,
        previous_url=previous_url
    )


@app.route('/indicar_aluno/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def indicar_aluno(id_aluno):
    """Indica um aluno para acompanhamento."""
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = indicar_aluno_service(id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@app.route('/carousel')
def carousel():
    """Página inicial do carousel."""
    return render_template('carousel.html')


@app.route('/cursos', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def cursos():
    """Gerencia cursos da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        nome_curso = request.form.get('curso')
        if nome_curso:
            sucesso, mensagem = cadastrar_curso(
                nome_curso, current_user.id_instituicao)
            if sucesso:
                flash(mensagem, 'success')
            else:
                flash(mensagem, 'warning')
        return redirect(url_for('cursos'))

    cursos = obter_cursos_instituicao(current_user.id_instituicao)
    return render_template('cursos.html', cursos=cursos, CURSOS_PADRAO=CURSOS_PADRAO)


@app.route('/cadastrar_aluno', methods=['POST'])
@login_required
@bloquear_chefe
def cadastrar_aluno():
    """Cadastra novo aluno."""
    dados_formulario = request.form.to_dict()
    sucesso, mensagem = cadastrar_aluno_service(
        dados_formulario, current_user.id_instituicao)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for('alunos_instituicao'))


@app.route('/alunos_instituicao', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def alunos_instituicao():
    """Lista alunos da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    instituicao_id = current_user.id_instituicao

    cursos_disponiveis = [
        curso.nome for curso in obter_cursos_instituicao(instituicao_id)]
    # Usa cursos da instituição
    cursos = cursos_disponiveis

    filtro_curso = request.form.get(
        'curso') if request.method == 'POST' else None

    # Get
    alunos_com_skills = processar_alunos_por_instituicao(
        instituicao_id, filtro_curso)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginate_items(alunos_com_skills, page)

    return render_template(
        'alunos_instituicao.html',
        alunos=pagination_result['items'],
        cursos=cursos,
        filtro_curso=filtro_curso,
        cursos_disponiveis=cursos_disponiveis,
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS,
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages']
    )


@app.route('/detalhes_aluno_instituicao/<int:id_aluno>', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def detalhes_aluno_instituicao(id_aluno):
    """Detalhes e edição de aluno para instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    aluno = Aluno.query.get_or_404(id_aluno)
    cursos_disponiveis = [
        curso.nome for curso in obter_cursos_instituicao(aluno.id_instituicao)]

    # Form
    hard_labels = HARD_SKILLS_POR_CURSO.get(aluno.curso, [])
    soft_labels = SOFT_SKILLS

    # Data
    hard_dict, soft_dict = processar_skills_para_edicao(aluno)

    if request.method == 'POST':
        dados_formulario = request.form.to_dict()
        sucesso, mensagem = atualizar_aluno(
            id_aluno, dados_formulario, cursos_disponiveis)

        if sucesso:
            flash(mensagem, "success")
        else:
            flash(mensagem, "danger")

        return redirect(url_for('detalhes_aluno_instituicao', id_aluno=id_aluno))

    return render_template(
        'detalhes_aluno_instituicao.html',
        aluno=aluno,
        cursos_disponiveis=cursos_disponiveis,
        hard_labels=hard_labels,
        soft_labels=soft_labels,
        hard_dict=hard_dict,
        soft_dict=soft_dict,
        HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
        SOFT_SKILLS=SOFT_SKILLS
    )


@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do usuário."""
    return processar_perfil()


@app.route('/acompanhar_aluno/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def acompanhar_aluno(id_aluno):
    """Inicia acompanhamento de aluno."""
    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = acompanhar_aluno_service(
        id_aluno, chefe_id)

    if sucesso:
        # Save
        criar_snapshot_skills_inicial(id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@app.route('/acompanhar')
@login_required
@bloquear_instituicao
def acompanhar():
    """Lista alunos em acompanhamento."""
    chefe_id = current_user.id_chefe

    # Get
    alunos_com_skills = processar_alunos_acompanhados_por_chefe(chefe_id)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginate_items(alunos_com_skills, page)

    return render_template(
        'acompanhar.html',
        alunos=pagination_result['items'],
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages']
    )


@app.route('/remover_acompanhamento/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def remover_acompanhamento(id_aluno):
    """Remove acompanhamento de aluno."""
    chefe_id = current_user.id_chefe
    sucesso, mensagem = remover_acompanhamento_service(id_aluno, chefe_id)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for('acompanhar'))


@app.route('/status_aluno/<int:id_aluno>')
@login_required
@bloquear_instituicao
def status_aluno(id_aluno):
    """Mostra status e histórico do aluno."""
    chefe_id = current_user.id_chefe
    historicos_dict, historico_pares, aluno = obter_historico_aluno(
        id_aluno, chefe_id)

    return render_template('status_aluno.html',
                           historicos=historicos_dict,
                           historico_pares=historico_pares,
                           aluno=aluno)


@app.route('/alunos_indicados')
@bloquear_chefe
@login_required
def alunos_indicados():
    """Lista alunos indicados da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('home'))

    instituicao_id = current_user.id_instituicao
    dados_alunos = obter_alunos_indicados(instituicao_id)

    # Paginação
    page = request.args.get('page', 1, type=int)
    pagination_result = paginar_alunos_indicados(dados_alunos, page)

    return render_template(
        'alunos_indicados.html',
        alunos=pagination_result['items'],
        page=pagination_result['page'],
        total_pages=pagination_result['total_pages']
    )


@app.route('/configuracoes', methods=['GET', 'POST'])
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
        return redirect(url_for('home'))

    # Verificar se 2FA está ativo
    tf_enabled = TwoFactor.query.filter_by(
        user_type=tipo_usuario, user_id=user_id, enabled=True).first() is not None

    return render_template('configuracoes.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao, two_factor_enabled=tf_enabled)


@app.route('/2fa/setup', methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    """Configura autenticação de dois fatores."""
    return processar_two_factor_setup()


@app.route('/2fa/verify', methods=['GET', 'POST'])
def two_factor_verify():
    """Verifica código 2FA."""
    return processar_two_factor_verify()


@app.route('/2fa/disable', methods=['GET', 'POST'])
@login_required
def two_factor_disable():
    """Desabilita autenticação de dois fatores."""
    return processar_two_factor_disable()


@app.route('/logout', methods=['POST'])
def logout():
    """Faz logout do usuário."""

    if 'tipo_usuario' in session:
        tipo_usuario = session['tipo_usuario']
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get(session.get('user_id'))
            if chefe:
                registrar_log('logout', chefe.nome, chefe.cargo, 'chefe')
        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get(session.get('user_id'))
            if instituicao:
                registrar_log('logout', instituicao.nome_instituicao,
                              'reitor', 'instituicao')

    logout_user()
    session.clear()
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))


# Configuração CSRF e cookies (ajustar secure=True em produção)
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # True em produção
)


@app.context_processor
def inject_csrf_token():
    """Injeta token CSRF nos templates."""
    return dict(csrf_token=generate_csrf)


@app.after_request
def set_csrf_cookie(response):
    """Define cookie CSRF."""
    try:
        csrf_token_value = generate_csrf()
        response.set_cookie(
            "csrf_token",
            csrf_token_value,
            secure=False,  # True em produção
            samesite="Lax",
            path="/"
        )
    except Exception:
        pass
    return response


@app.route('/esqueceu-senha', methods=['GET', 'POST'])
def esqueceu_senha():
    """Página de recuperação de senha."""
    return processar_esqueceu_senha()


@app.route('/verificar-codigo')
def verificar_codigo():
    """Página de verificação de código."""
    return processar_verificar_codigo()


@app.route('/verificar-codigo', methods=['POST'])
def verificar_codigo_post():
    """Processa verificação de código."""
    return processar_verificar_codigo_post()


@app.route('/nova-senha', methods=['GET', 'POST'])
def nova_senha():
    """Página de nova senha."""
    return processar_nova_senha_page()


# Rotas administrativas (proteger em produção)

@app.route('/admin/bloquear-usuario', methods=['POST'])
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


@app.route('/admin/desbloquear-usuario', methods=['POST'])
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


if __name__ == "__main__":
    # Host para acesso externo
    app.run(debug=True, host='0.0.0.0')
