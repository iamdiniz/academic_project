"""
Serviço de Processamento de Dados - Processa dados de alunos e skills.
Código movido do app.py para organizar responsabilidades.
"""

import json
from domain import Aluno, SkillsDoAluno, Indicacao, Acompanhamento


def processar_aluno_com_skills(aluno):
    """
    Processa um aluno e suas skills, retornando um dicionário formatado.

    Args:
        aluno: Objeto Aluno do banco de dados

    Returns:
        dict: Dicionário com dados do aluno e suas skills formatadas
    """
    skills = aluno.skills
    hard_labels = []
    hard_skills = []
    soft_labels = []
    soft_skills = []

    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}

        hard_labels = list(hard_dict.keys())
        hard_skills = list(hard_dict.values())
        soft_labels = list(soft_dict.keys())
        soft_skills = list(soft_dict.values())

    return {
        "id_aluno": aluno.id_aluno,
        "nome": aluno.nome_jovem,
        "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
        "curso": aluno.curso,
        "periodo": aluno.periodo,
        "contato_jovem": aluno.contato_jovem,
        "email": aluno.email,
        "hard_labels": hard_labels,
        "hard_skills": hard_skills,
        "soft_labels": soft_labels,
        "soft_skills": soft_skills
    }


def processar_alunos_indicados_por_chefe(chefe_id):
    """
    Processa todos os alunos indicados por um chefe específico.

    Args:
        chefe_id: ID do chefe

    Returns:
        list: Lista de dicionários com dados dos alunos processados
    """
    # Busca todos os alunos indicados por este chefe usando a tabela Indicacao
    indicacoes = Indicacao.query.filter_by(id_chefe=chefe_id).all()
    alunos = [indicacao.aluno for indicacao in indicacoes]

    alunos_com_skills = []
    for aluno in alunos:
        alunos_com_skills.append(processar_aluno_com_skills(aluno))

    return alunos_com_skills


def processar_alunos_acompanhados_por_chefe(chefe_id):
    """
    Processa todos os alunos acompanhados por um chefe específico.

    Args:
        chefe_id: ID do chefe

    Returns:
        list: Lista de dicionários com dados dos alunos processados
    """
    acompanhamentos = Acompanhamento.query.filter_by(id_chefe=chefe_id).all()
    alunos_com_skills = []

    for ac in acompanhamentos:
        aluno = ac.aluno
        alunos_com_skills.append(processar_aluno_com_skills(aluno))

    return alunos_com_skills


def processar_alunos_por_instituicao(instituicao_id, filtro_curso=None):
    """
    Processa todos os alunos de uma instituição, opcionalmente filtrados por curso.

    Args:
        instituicao_id: ID da instituição
        filtro_curso: Nome do curso para filtrar (opcional)

    Returns:
        list: Lista de dicionários com dados dos alunos processados
    """
    if filtro_curso:
        alunos = Aluno.query.filter_by(
            id_instituicao=instituicao_id, curso=filtro_curso).all()
    else:
        alunos = Aluno.query.filter_by(id_instituicao=instituicao_id).all()

    alunos_com_skills = []
    for aluno in alunos:
        alunos_com_skills.append(processar_aluno_com_skills(aluno))

    return alunos_com_skills


def processar_skills_para_edicao(aluno):
    """
    Processa as skills de um aluno para exibição em formulário de edição.

    Args:
        aluno: Objeto Aluno do banco de dados

    Returns:
        tuple: (hard_dict, soft_dict) com as skills formatadas
    """
    skills = aluno.skills
    hard_dict = {}
    soft_dict = {}

    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}

    return hard_dict, soft_dict


def calcular_total_skills_por_habilidades(aluno, habilidades):
    """
    Calcula o total de skills de um aluno para habilidades específicas.

    Args:
        aluno: Objeto Aluno do banco de dados
        habilidades: Lista de habilidades no formato ['tipo:nome', ...]

    Returns:
        int: Total de pontos das habilidades especificadas
    """
    skills = aluno.skills
    total = 0

    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}

        for hab in habilidades:
            if ':' in hab:
                tipo, nome = hab.split(':', 1)
                if tipo == 'hard':
                    total += hard_dict.get(nome, 0)
                elif tipo == 'soft':
                    total += soft_dict.get(nome, 0)

    return total
