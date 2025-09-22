from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from urllib.parse import unquote
from services import (
    obter_cursos_por_instituicao,
    processar_alunos_indicados_por_chefe,
    processar_alunos_acompanhados_por_chefe,
    obter_historico_aluno,
    obter_cursos_instituicao,
    criar_snapshot_skills_inicial,
    paginate_items,
    bloquear_instituicao,
    obter_detalhes_aluno,
    obter_alunos_por_curso,
    paginar_alunos_por_curso
)
from services.indication_service import (
    indicar_aluno as indicar_aluno_service,
    acompanhar_aluno as acompanhar_aluno_service,
    remover_acompanhamento as remover_acompanhamento_services,
    remover_indicacao as remover_indicacao_services
)
from domain import (
    InstituicaodeEnsino,
    Aluno,
    CURSOS_PADRAO,
    HARD_SKILLS_POR_CURSO,
    SOFT_SKILLS
)

chefe_bp = Blueprint('chefe', __name__)


@chefe_bp.route('/detalhes_instituicao/<int:id_instituicao>')
@login_required
def detalhes_instituicao(id_instituicao):
    """Mostra detalhes de uma instituição."""
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    cursos = obter_cursos_instituicao(id_instituicao)
    return render_template('detalhes_instituicao.html', instituicao=instituicao, cursos=cursos)


@chefe_bp.route('/instituicaoEnsino')
@login_required
@bloquear_instituicao
def instituicao_ensino():
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


@chefe_bp.route('/minhas_selecoes')
@bloquear_instituicao
@login_required
def minhas_selecoes():
    """Mostra alunos indicados pelo chefe."""
    if session.get('tipo_usuario') != 'chefe':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('auth.home'))

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


@chefe_bp.route('/remover_indicacao/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def remover_indicacao(id_aluno):
    """Remove indicação de aluno."""
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = remover_indicacao_services(
        id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@chefe_bp.route('/indicar_aluno/<int:id_aluno>', methods=['POST'])
@bloquear_instituicao
@login_required
def indicar_aluno(id_aluno):
    """Indica um aluno para acompanhamento."""
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido.'}), 403

    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = indicar_aluno_service(id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@chefe_bp.route('/acompanhar_aluno/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def acompanhar_aluno(id_aluno):
    """Inicia acompanhamento de aluno."""
    chefe_id = current_user.id_chefe
    sucesso, mensagem, status_code = acompanhar_aluno_service(
        id_aluno, chefe_id)

    if sucesso:
        criar_snapshot_skills_inicial(id_aluno, chefe_id)

    return jsonify({'message' if sucesso else 'error': mensagem}), status_code


@chefe_bp.route('/acompanhar')
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


@chefe_bp.route('/remover_acompanhamento/<int:id_aluno>', methods=['POST'])
@login_required
@bloquear_instituicao
def remover_acompanhamento(id_aluno):
    """Remove acompanhamento de aluno."""
    chefe_id = current_user.id_chefe
    sucesso, mensagem = remover_acompanhamento_services(id_aluno, chefe_id)

    if sucesso:
        flash(mensagem, "success")
    else:
        flash(mensagem, "danger")

    return redirect(url_for('chefe.acompanhar'))


@chefe_bp.route('/status_aluno/<int:id_aluno>')
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


@chefe_bp.route('/ver_alunos_por_curso', methods=['GET'])
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


@chefe_bp.route('/detalhes_aluno/<int:id_aluno>')
@login_required
@bloquear_instituicao
def detalhes_aluno(id_aluno):
    """Mostra detalhes de um aluno."""
    aluno, hard_labels, hard_values, soft_labels, soft_values = obter_detalhes_aluno(
        id_aluno)

    if not aluno:
        flash('Aluno não encontrado.', 'danger')
        return redirect(url_for('chefe.instituicao_ensino'))

    previous_url = request.args.get(
        'previous', url_for('chefe.instituicao_ensino'))

    return render_template(
        'detalhes_aluno.html',
        aluno=aluno,
        hard_labels=hard_labels,
        hard_values=hard_values,
        soft_labels=soft_labels,
        soft_values=soft_values,
        previous_url=previous_url
    )
