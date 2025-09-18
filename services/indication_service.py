"""
Serviço para operações de indicações e acompanhamentos.
Inclui funcionalidades para indicar alunos, acompanhar e gerenciar relacionamentos.
"""

from domain import Indicacao, Acompanhamento, Aluno, db
from math import ceil


def indicar_aluno(id_aluno, chefe_id):
    """
    Indica um aluno para um chefe.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        tuple: (sucesso, mensagem, status_code)
    """
    # Verifica se já existe indicação deste chefe para este aluno
    ja_indicado = Indicacao.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno
    ).first()

    if ja_indicado:
        return False, "Você já indicou este aluno.", 400

    try:
        nova_indicacao = Indicacao(id_chefe=chefe_id, id_aluno=id_aluno)
        db.session.add(nova_indicacao)
        db.session.commit()
        return True, "Aluno indicado com sucesso!", 200
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao indicar aluno: {str(e)}", 500


def remover_indicacao(id_aluno, chefe_id):
    """
    Remove a indicação de um aluno.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        tuple: (sucesso, mensagem, status_code)
    """
    aluno = Aluno.query.get_or_404(id_aluno)

    # Verifica se o aluno foi indicado pelo chefe logado
    if aluno.indicado_por != chefe_id:
        return False, "Você não indicou este aluno.", 400

    try:
        # Remove a indicação
        aluno.indicado_por = None
        db.session.commit()
        return True, "Indicação removida com sucesso!", 200
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao remover indicação: {str(e)}", 500


def acompanhar_aluno(id_aluno, chefe_id):
    """
    Adiciona um aluno à lista de acompanhamento de um chefe.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        tuple: (sucesso, mensagem, status_code)
    """
    # Verifica se já está acompanhando
    acompanhamento = Acompanhamento.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno
    ).first()

    if acompanhamento:
        return False, "Você já está acompanhando este aluno.", 400

    try:
        novo_acompanhamento = Acompanhamento(
            id_chefe=chefe_id, id_aluno=id_aluno)
        db.session.add(novo_acompanhamento)
        db.session.commit()
        return True, "Aluno adicionado à sua lista de acompanhamento!", 200
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao acompanhar aluno: {str(e)}", 500


def remover_acompanhamento(id_aluno, chefe_id):
    """
    Remove um aluno da lista de acompanhamento de um chefe.

    Args:
        id_aluno (int): ID do aluno
        chefe_id (int): ID do chefe

    Returns:
        tuple: (sucesso, mensagem)
    """
    ac = Acompanhamento.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno
    ).first()

    if ac:
        try:
            db.session.delete(ac)
            db.session.commit()
            return True, "Aluno removido do acompanhamento."
        except Exception as e:
            db.session.rollback()
            return False, f"Erro ao remover acompanhamento: {str(e)}"
    else:
        return False, "Acompanhamento não encontrado."


def obter_alunos_indicados(instituicao_id):
    """
    Obtém todos os alunos indicados de uma instituição.

    Args:
        instituicao_id (int): ID da instituição

    Returns:
        list: Lista de dados dos alunos indicados
    """
    alunos = Aluno.query.filter_by(id_instituicao=instituicao_id).all()
    dados_alunos = []

    for aluno in alunos:
        for indicacao in aluno.indicacoes:
            chefe = indicacao.chefe
            dados_alunos.append({
                "id_aluno": aluno.id_aluno,
                "nome": aluno.nome_jovem,
                "curso": aluno.curso,
                "periodo": aluno.periodo,
                "chefe_nome": chefe.nome if chefe else 'Não informado',
                "chefe_empresa": chefe.nome_empresa if chefe else 'Não informado',
                "data_indicacao": indicacao.data_indicacao.strftime('%d/%m/%Y') if indicacao.data_indicacao else 'Sem data'
            })

    return dados_alunos


def paginar_alunos_indicados(dados_alunos, page, per_page=12):
    """
    Pagina os dados dos alunos indicados.

    Args:
        dados_alunos (list): Lista de dados dos alunos
        page (int): Página atual
        per_page (int): Itens por página

    Returns:
        dict: Dados paginados
    """
    total = len(dados_alunos)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = dados_alunos[start:end]

    return {
        'items': alunos_paginados,
        'page': page,
        'total_pages': total_pages
    }
