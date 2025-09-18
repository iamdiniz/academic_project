"""
Serviço para operações de histórico de skills.
Inclui funcionalidades para gerenciar e processar histórico de habilidades dos alunos.
"""

import json
import pytz
from datetime import datetime
from domain import SkillsHistorico, Aluno, Acompanhamento, db


def obter_historico_aluno(id_aluno, chefe_id):
    """
    Obtém o histórico de skills de um aluno para um chefe específico.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        tuple: (historicos_dict, historico_pares, aluno)
    """
    historicos = SkillsHistorico.query.filter_by(
        id_aluno=id_aluno, id_chefe=chefe_id
    ).order_by(SkillsHistorico.data.desc()).all()

    aluno = Aluno.query.get_or_404(id_aluno)
    historicos_dict = []
    fuso_brasil = pytz.timezone('America/Recife')

    for hist in historicos:
        # Converte para o fuso de Recife se não tiver tzinfo
        data_brasil = hist.data
        if data_brasil and data_brasil.tzinfo is None:
            data_brasil = pytz.utc.localize(
                data_brasil).astimezone(fuso_brasil)
        elif data_brasil:
            data_brasil = data_brasil.astimezone(fuso_brasil)

        hard = json.loads(
            hist.hard_skills_json) if hist.hard_skills_json else {}
        soft = json.loads(
            hist.soft_skills_json) if hist.soft_skills_json else {}

        historicos_dict.append({
            'data': data_brasil,
            'hard_skills': hard,
            'soft_skills': soft
        })

    # Gera pares para comparação de evolução
    historico_pares = []
    if len(historicos_dict) > 1:
        for i in range(len(historicos_dict) - 1):
            atual = historicos_dict[i]
            anterior = historicos_dict[i + 1]
            historico_pares.append({
                'data': atual['data'],
                'atual': atual,
                'anterior': anterior
            })
    elif len(historicos_dict) == 1:
        historico_pares.append({
            'data': historicos_dict[0]['data'],
            'atual': historicos_dict[0],
            'anterior': None
        })

    return historicos_dict, historico_pares, aluno


def criar_snapshot_skills_inicial(id_aluno, chefe_id):
    """
    Cria um snapshot inicial das skills quando um chefe começa a acompanhar um aluno.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        bool: True se criado com sucesso, False caso contrário
    """
    try:
        # Verifica se já existe histórico para este chefe
        historico_existente = SkillsHistorico.query.filter_by(
            id_aluno=id_aluno, id_chefe=chefe_id
        ).count()

        if historico_existente > 0:
            return True  # Já existe, não precisa criar

        aluno = Aluno.query.get(id_aluno)
        if not aluno or not aluno.skills:
            return False

        # Cria o snapshot inicial
        novo_historico = SkillsHistorico(
            id_aluno=aluno.id_aluno,
            id_chefe=chefe_id,
            hard_skills_json=aluno.skills.hard_skills_json,
            soft_skills_json=aluno.skills.soft_skills_json
        )
        db.session.add(novo_historico)
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def salvar_historico_skills_atualizacao(id_aluno, hard_skills_dict, soft_skills_dict):
    """
    Salva o histórico de skills após uma atualização para todos os chefes que acompanham o aluno.

    Args:
        id_aluno (int): ID do aluno
        hard_skills_dict (dict): Dicionário com hard skills
        soft_skills_dict (dict): Dicionário com soft skills

    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    try:
        acompanhamentos = Acompanhamento.query.filter_by(
            id_aluno=id_aluno).all()
        fuso_brasil = pytz.timezone('America/Recife')
        data_atualizacao = datetime.now(fuso_brasil)

        for ac in acompanhamentos:
            novo_historico = SkillsHistorico(
                id_aluno=id_aluno,
                id_chefe=ac.id_chefe,
                hard_skills_json=json.dumps(hard_skills_dict),
                soft_skills_json=json.dumps(soft_skills_dict),
                data=data_atualizacao
            )
            db.session.add(novo_historico)

        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False


def obter_estatisticas_evolucao(historicos_dict):
    """
    Calcula estatísticas de evolução das skills.

    Args:
        historicos_dict (list): Lista de históricos processados

    Returns:
        dict: Estatísticas de evolução
    """
    if len(historicos_dict) < 2:
        return {
            'tem_evolucao': False,
            'melhorias_hard': [],
            'melhorias_soft': [],
            'pioras_hard': [],
            'pioras_soft': []
        }

    # Compara o mais recente com o anterior
    atual = historicos_dict[0]
    anterior = historicos_dict[1]

    melhorias_hard = []
    pioras_hard = []
    melhorias_soft = []
    pioras_soft = []

    # Analisa hard skills
    for skill, valor_atual in atual['hard_skills'].items():
        valor_anterior = anterior['hard_skills'].get(skill, 0)
        diferenca = valor_atual - valor_anterior

        if diferenca > 0:
            melhorias_hard.append({
                'skill': skill,
                'anterior': valor_anterior,
                'atual': valor_atual,
                'diferenca': diferenca
            })
        elif diferenca < 0:
            pioras_hard.append({
                'skill': skill,
                'anterior': valor_anterior,
                'atual': valor_atual,
                'diferenca': abs(diferenca)
            })

    # Analisa soft skills
    for skill, valor_atual in atual['soft_skills'].items():
        valor_anterior = anterior['soft_skills'].get(skill, 0)
        diferenca = valor_atual - valor_anterior

        if diferenca > 0:
            melhorias_soft.append({
                'skill': skill,
                'anterior': valor_anterior,
                'atual': valor_atual,
                'diferenca': diferenca
            })
        elif diferenca < 0:
            pioras_soft.append({
                'skill': skill,
                'anterior': valor_anterior,
                'atual': valor_atual,
                'diferenca': abs(diferenca)
            })

    return {
        'tem_evolucao': True,
        'melhorias_hard': melhorias_hard,
        'melhorias_soft': melhorias_soft,
        'pioras_hard': pioras_hard,
        'pioras_soft': pioras_soft
    }
