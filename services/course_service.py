"""
Serviço para operações relacionadas a cursos.
Inclui funcionalidades de cadastro, validação e gerenciamento de cursos.
"""

# Imports removidos - não utilizados neste serviço
from domain import Curso, db


def cadastrar_curso(nome_curso, id_instituicao):
    """
    Cadastra um novo curso para uma instituição.

    Args:
        nome_curso (str): Nome do curso
        id_instituicao (int): ID da instituição

    Returns:
        tuple: (sucesso, mensagem)
    """
    if not nome_curso or not nome_curso.strip():
        return False, "Nome do curso é obrigatório."

    # Verifica se já existe para esta instituição
    ja_existe = Curso.query.filter_by(
        nome=nome_curso,
        id_instituicao=id_instituicao
    ).first()

    if ja_existe:
        return False, "Este curso já foi cadastrado!"

    try:
        novo_curso = Curso(
            nome=nome_curso.strip(),
            id_instituicao=id_instituicao
        )
        db.session.add(novo_curso)
        db.session.commit()
        return True, "Curso cadastrado com sucesso!"
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao cadastrar curso: {str(e)}"


def obter_cursos_instituicao(id_instituicao):
    """
    Obtém todos os cursos de uma instituição.

    Args:
        id_instituicao (int): ID da instituição

    Returns:
        list: Lista de cursos da instituição
    """
    return Curso.query.filter_by(id_instituicao=id_instituicao).all()


def obter_cursos_por_instituicao(instituicoes):
    """
    Obtém cursos organizados por instituição.

    Args:
        instituicoes (list): Lista de instituições

    Returns:
        dict: Dicionário com cursos por instituição
    """
    cursos_por_instituicao = {}
    for inst in instituicoes:
        cursos = Curso.query.filter_by(
            id_instituicao=inst.id_instituicao).all()
        cursos_por_instituicao[inst.id_instituicao] = [
            curso.nome for curso in cursos]

        # Debug: verificar se há cursos
        if not cursos:
            print(
                f"DEBUG: Instituição {inst.nome_instituicao} (ID: {inst.id_instituicao}) não tem cursos cadastrados")
        else:
            print(
                f"DEBUG: Instituição {inst.nome_instituicao} (ID: {inst.id_instituicao}) tem {len(cursos)} cursos: {[curso.nome for curso in cursos]}")

    return cursos_por_instituicao


def validar_curso_existe(nome_curso, id_instituicao):
    """
    Valida se um curso existe para uma instituição.

    Args:
        nome_curso (str): Nome do curso
        id_instituicao (int): ID da instituição

    Returns:
        bool: True se o curso existe, False caso contrário
    """
    curso = Curso.query.filter_by(
        nome=nome_curso,
        id_instituicao=id_instituicao
    ).first()
    return curso is not None
