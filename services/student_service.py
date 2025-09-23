"""
Serviço para operações relacionadas a alunos.
Inclui funcionalidades de cadastro, edição, remoção e consulta de alunos.
"""

import json
# Imports removidos - não utilizados neste serviço
from sqlalchemy.exc import IntegrityError
from unidecode import unidecode
from urllib.parse import unquote
from math import ceil
from domain import (
    Aluno, SkillsDoAluno, InstituicaodeEnsino, db,
    HARD_SKILLS_POR_CURSO, SOFT_SKILLS
)
from services.validation_service import (
    validar_email_formato,
    validar_periodo_formato,
    validar_contato_formato,
    validar_skill_valor
)
from services.password_validation_service import (
    validar_campos_obrigatorios_aluno,
    validar_campos_obrigatorios_aluno_edicao
)
from services.data_processing_service import (
    processar_aluno_com_skills,
    calcular_total_skills_por_habilidades
)
from services.skills_history_service import salvar_historico_skills_atualizacao


def cadastrar_aluno(dados_formulario, id_instituicao):
    """
    Cadastra um novo aluno.

    Args:
        dados_formulario (dict): Dados do formulário
        id_instituicao (int): ID da instituição

    Returns:
        tuple: (sucesso, mensagem)
    """
    # Aceita nomes neutros vindos do front
    nome_jovem = (dados_formulario.get('a_nj')
                  or dados_formulario.get('nome_jovem') or '').strip()
    data_nascimento = (dados_formulario.get(
        'a_dn') or dados_formulario.get('data_nascimento') or '').strip()
    contato_jovem = (dados_formulario.get('a_ct')
                     or dados_formulario.get('contato_jovem') or '').strip()
    email = (dados_formulario.get('a_e')
             or dados_formulario.get('email') or '').strip()
    endereco_jovem = (dados_formulario.get('a_addr')
                      or dados_formulario.get('endereco_jovem') or '').strip()
    curso = (dados_formulario.get('a_c')
             or dados_formulario.get('curso') or '').strip()
    formacao = (dados_formulario.get('a_f')
                or dados_formulario.get('formacao') or '').strip()
    periodo = (dados_formulario.get('a_p')
               or dados_formulario.get('periodo') or '').strip()

    # Validação do e-mail duplicado
    if Aluno.query.filter_by(email=email).first():
        return False, "Já existe um aluno cadastrado com este e-mail."

    # Validação dos campos obrigatórios
    if validar_campos_obrigatorios_aluno(nome_jovem, data_nascimento, endereco_jovem, contato_jovem, email, curso, formacao, periodo):
        return False, "Preencha todos os campos obrigatórios!"

    # Validação do e-mail
    if validar_email_formato(email):
        return False, "E-mail inválido!"

    # Validação do período
    if validar_periodo_formato(periodo):
        return False, "Período deve ser um número entre 1 e 20."

    # Validação do contato
    if validar_contato_formato(contato_jovem):
        return False, "Contato deve conter apenas números e ter pelo menos 11 dígitos."

    # Validação das hard skills
    hard_skills_dict = {}
    for label in HARD_SKILLS_POR_CURSO.get(curso, []):
        field_name = f"hard_{label.lower().replace(' ', '_')}"
        valor = dados_formulario.get(
            f"h_{label.lower().replace(' ', '_')}") or dados_formulario.get(field_name)
        if validar_skill_valor(valor):
            return False, f"Preencha corretamente a hard skill '{label}' (0 a 10)."
        hard_skills_dict[label] = int(valor)

    # Validação das soft skills
    soft_skills_dict = {}
    for label in SOFT_SKILLS:
        field_name = label.lower().replace(' ', '_')
        valor = dados_formulario.get(
            f"s_{field_name}") or dados_formulario.get(field_name)
        if valor is None or not valor.isdigit() or int(valor) < 0 or int(valor) > 10:
            return False, f"Preencha corretamente a soft skill '{label}' (0 a 10)."
        soft_skills_dict[label] = int(valor)

    try:
        novo_aluno = Aluno(
            nome_jovem=nome_jovem,
            data_nascimento=data_nascimento,
            contato_jovem=contato_jovem,
            email=email,
            endereco_jovem=endereco_jovem,
            id_instituicao=id_instituicao,
            curso=curso,
            formacao=formacao,
            periodo=periodo
        )
        db.session.add(novo_aluno)
        db.session.commit()

        skills = SkillsDoAluno(
            id_aluno=novo_aluno.id_aluno,
            hard_skills_json=json.dumps(hard_skills_dict),
            soft_skills_json=json.dumps(soft_skills_dict),
        )
        db.session.add(skills)
        db.session.commit()

        # Incrementa a quantidade de alunos na instituição
        instituicao = InstituicaodeEnsino.query.get(id_instituicao)
        instituicao.quantidade_de_alunos += 1
        db.session.commit()

        return True, "Aluno cadastrado com sucesso!"
    except IntegrityError:
        db.session.rollback()
        return False, "Erro inesperado ao cadastrar aluno. Tente novamente."


def remover_aluno(id_aluno):
    """
    Remove um aluno do sistema.

    Args:
        id_aluno (int): ID do aluno

    Returns:
        tuple: (sucesso, mensagem)
    """
    try:
        aluno = Aluno.query.get_or_404(id_aluno)

        # Decrementar a quantidade de alunos na instituição
        instituicao = InstituicaodeEnsino.query.get(aluno.id_instituicao)
        instituicao.quantidade_de_alunos -= 1

        # Remover o aluno
        db.session.delete(aluno)
        db.session.commit()

        return True, "Aluno removido com sucesso!"
    except Exception:
        db.session.rollback()
        return False, "Erro ao remover aluno."


def obter_detalhes_aluno(id_aluno):
    """
    Obtém os detalhes de um aluno.

    Args:
        id_aluno (int): ID do aluno

    Returns:
        tuple: (aluno, hard_labels, hard_values, soft_labels, soft_values)
    """
    aluno = Aluno.query.filter_by(id_aluno=id_aluno).first()
    if not aluno:
        return None, [], [], [], []

    hard_labels, hard_values = [], []
    soft_labels, soft_values = [], []

    if aluno.skills:
        hard_dict = json.loads(
            aluno.skills.hard_skills_json) if aluno.skills.hard_skills_json else {}
        soft_dict = json.loads(
            aluno.skills.soft_skills_json) if aluno.skills.soft_skills_json else {}
        hard_labels = list(hard_dict.keys())
        hard_values = list(hard_dict.values())
        soft_labels = list(soft_dict.keys())
        soft_values = list(soft_dict.values())

    return aluno, hard_labels, hard_values, soft_labels, soft_values


def atualizar_aluno(id_aluno, dados_formulario, cursos_disponiveis):
    """
    Atualiza as informações de um aluno.

    Args:
        id_aluno (int): ID do aluno
        dados_formulario (dict): Dados do formulário
        cursos_disponiveis (list): Lista de cursos disponíveis

    Returns:
        tuple: (sucesso, mensagem)
    """
    aluno = Aluno.query.get_or_404(id_aluno)

    # Validação do curso
    curso = dados_formulario.get('curso')
    if curso not in cursos_disponiveis:
        return False, "Curso inválido para esta instituição!"

    # Validação dos campos obrigatórios
    nome_jovem = dados_formulario.get('nome_jovem', '').strip()
    data_nascimento = dados_formulario.get('data_nascimento', '').strip()
    contato_jovem = dados_formulario.get('contato_jovem', '').strip()
    email = dados_formulario.get('email', '').strip()
    endereco_jovem = dados_formulario.get('endereco_jovem', '').strip()
    formacao = dados_formulario.get('formacao', '').strip()
    periodo = dados_formulario.get('periodo', '').strip()

    # Verifica se já existe outro aluno com este e-mail
    email_existente = Aluno.query.filter(
        Aluno.email == email, Aluno.id_aluno != aluno.id_aluno
    ).first()
    if email_existente:
        return False, "Já existe um aluno cadastrado com este e-mail."

    if validar_campos_obrigatorios_aluno_edicao(nome_jovem, data_nascimento, contato_jovem, email, endereco_jovem, formacao, periodo):
        return False, "Preencha todos os campos obrigatórios!"

    # Validação do e-mail
    if validar_email_formato(email):
        return False, "E-mail inválido!"

    # Validação do contato
    if validar_contato_formato(contato_jovem):
        return False, "Contato deve conter apenas números e ter pelo menos 11 dígitos."

    # Validação do período
    if validar_periodo_formato(periodo):
        return False, "Período deve ser um número inteiro entre 1 e 20."

    # Atualizar informações do aluno
    aluno.nome_jovem = nome_jovem
    aluno.data_nascimento = data_nascimento
    aluno.contato_jovem = contato_jovem
    aluno.email = email
    aluno.endereco_jovem = endereco_jovem
    aluno.curso = curso
    aluno.formacao = formacao
    aluno.periodo = periodo

    # Atualizar hard skills (dinâmico conforme curso)
    hard_labels = HARD_SKILLS_POR_CURSO.get(curso, [])
    new_hard_dict = {}
    for label in hard_labels:
        field_name = f"hard_{label.lower().replace(' ', '_')}"
        valor = dados_formulario.get(field_name)
        if valor is None or valor == '':
            return False, f"Preencha a pontuação de '{label}'!"
        try:
            new_hard_dict[label] = int(valor)
        except ValueError:
            return False, f"Valor inválido para '{label}'."

    # Atualizar soft skills (fixo)
    new_soft_dict = {}
    for label in SOFT_SKILLS:
        field_name = label.lower().replace(' ', '_')
        valor = dados_formulario.get(field_name)
        if valor is None or valor == '':
            return False, f"Preencha a pontuação de '{label}'!"
        try:
            new_soft_dict[label] = int(valor)
        except ValueError:
            return False, f"Valor inválido para '{label}'."

    try:
        # Atualiza ou cria o registro de skills
        skills = aluno.skills
        if not skills:
            skills = SkillsDoAluno(id_aluno=aluno.id_aluno)
            db.session.add(skills)
        skills.hard_skills_json = json.dumps(new_hard_dict)
        skills.soft_skills_json = json.dumps(new_soft_dict)

        db.session.commit()

        # Salvar histórico das skills após atualizar
        salvar_historico_skills_atualizacao(
            aluno.id_aluno, new_hard_dict, new_soft_dict)

        return True, "Informações do aluno atualizadas com sucesso!"
    except IntegrityError:
        db.session.rollback()
        return False, "Já existe um aluno cadastrado com este e-mail."


def obter_alunos_por_curso(inst_id, curso, periodo=None, habilidade=None):
    """
    Obtém alunos filtrados por curso com opções de filtro.

    Args:
        inst_id (int): ID da instituição
        curso (str): Nome do curso
        periodo (str): Período para filtrar
        habilidade (list): Lista de habilidades para ordenar

    Returns:
        tuple: (alunos_com_skills, mensagem)
    """
    # Decodificar o parâmetro 'curso' para evitar problemas com caracteres especiais
    curso = unquote(curso).strip()
    curso_normalizado = unidecode(curso).lower()

    alunos = Aluno.query.filter(Aluno.id_instituicao == inst_id).all()

    alunos_filtrados = [
        aluno for aluno in alunos
        if unidecode(aluno.curso).lower() == curso_normalizado
    ]

    # Filtro por período
    if periodo and periodo.isdigit():
        alunos_filtrados = [
            aluno for aluno in alunos_filtrados if str(aluno.periodo) == periodo
        ]

    # Ordenação por múltiplas habilidades (hard e soft)
    if habilidade:
        def get_total_skills(aluno):
            return calcular_total_skills_por_habilidades(aluno, habilidade)
        alunos_filtrados = sorted(
            alunos_filtrados, key=get_total_skills, reverse=True)

    alunos_com_skills = []
    for aluno in alunos_filtrados:
        alunos_com_skills.append(processar_aluno_com_skills(aluno))

    mensagem = None
    if not alunos_filtrados:
        if periodo and periodo.isdigit():
            mensagem = f"Nenhum aluno encontrado para o período '{periodo}' no curso '{curso}'."
        else:
            mensagem = f"Nenhum aluno encontrado para o curso '{curso}'."

    return alunos_com_skills, mensagem


def paginar_alunos_por_curso(alunos_com_skills, page, per_page=12):
    """
    Pagina os alunos por curso.

    Args:
        alunos_com_skills (list): Lista de alunos com skills
        page (int): Página atual
        per_page (int): Itens por página

    Returns:
        dict: Dados paginados
    """
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    return {
        'items': alunos_paginados,
        'page': page,
        'total_pages': total_pages
    }
