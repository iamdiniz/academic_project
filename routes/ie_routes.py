from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from services import (
    obter_cursos_instituicao,
    paginate_items,
    bloquear_chefe,
    processar_alunos_por_instituicao,
    processar_skills_para_edicao,
    cadastrar_curso,
    obter_alunos_indicados,
    paginar_alunos_indicados,
    atualizar_aluno,
)
from services.student_service import cadastrar_aluno as cadastrar_aluno_service, remover_aluno as remover_aluno_service
from domain import (
    InstituicaodeEnsino,
    Aluno,
    CURSOS_PADRAO,
    HARD_SKILLS_POR_CURSO,
    SOFT_SKILLS
)

instituicao_bp = Blueprint('instituicao', __name__)


@instituicao_bp.route('/detalhes_instituicao/<int:id_instituicao>')
@login_required
def detalhes_instituicao(id_instituicao):
    """Mostra detalhes de uma instituição."""
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    cursos = obter_cursos_instituicao(id_instituicao)
    return render_template('detalhes_instituicao.html', instituicao=instituicao, cursos=cursos)


@instituicao_bp.route('/cursos', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def cursos():
    """Gerencia cursos da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('auth.home'))

    if request.method == 'POST':
        nome_curso = request.form.get('curso')
        if nome_curso:
            sucesso, mensagem = cadastrar_curso(
                nome_curso, current_user.id_instituicao)
            if sucesso:
                flash(mensagem, 'success')
            else:
                flash(mensagem, 'warning')
        return redirect(url_for('instituicao.cursos'))

    cursos = obter_cursos_instituicao(current_user.id_instituicao)
    return render_template('cursos.html', cursos=cursos, CURSOS_PADRAO=CURSOS_PADRAO)


@instituicao_bp.route('/cadastrar_aluno', methods=['POST'])
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

    return redirect(url_for('instituicao.alunos_instituicao'))


@instituicao_bp.route('/remover_aluno/<int:id_aluno>', methods=['POST'])
@login_required
def remover_aluno(id_aluno):
    """Remove um aluno do sistema."""
    sucesso, mensagem = remover_aluno_service(id_aluno)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for('instituicao.alunos_instituicao'))


@instituicao_bp.route('/alunos_instituicao', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def alunos_instituicao():
    """Lista alunos da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('auth.home'))

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


@instituicao_bp.route('/detalhes_aluno_instituicao/<int:id_aluno>', methods=['GET', 'POST'])
@login_required
@bloquear_chefe
def detalhes_aluno_instituicao(id_aluno):
    """Detalhes e edição de aluno para instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('auth.home'))

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

        return redirect(url_for('instituicao.detalhes_aluno_instituicao', id_aluno=id_aluno))

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


@instituicao_bp.route('/alunos_indicados')
@login_required
@bloquear_chefe
def alunos_indicados():
    """Lista alunos indicados da instituição."""
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('auth.home'))

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
