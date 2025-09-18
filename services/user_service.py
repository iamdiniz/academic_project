"""
Serviço de Operações de Usuário - Gerencia cadastro, perfil e operações de usuário.
Código movido do app.py para organizar responsabilidades.
"""

import re
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from domain import db, Chefe, InstituicaodeEnsino, Curso


def criar_instituicao_ensino(dados_formulario):
    """
    Cria uma nova instituição de ensino.

    Args:
        dados_formulario: Dicionário com dados do formulário

    Returns:
        tuple: (sucesso: bool, mensagem: str, instituicao: InstituicaodeEnsino ou None)
    """
    try:
        nova_instituicao = InstituicaodeEnsino(
            nome_instituicao=dados_formulario['instituicao_nome'],
            email=dados_formulario['email'],
            senha=generate_password_hash(dados_formulario['senha']),
            infraestrutura=dados_formulario.get('infraestrutura', ''),
            nota_mec=dados_formulario.get('nota_mec'),
            areas_de_formacao=", ".join(
                dados_formulario['cursos_selecionados']),
            modalidades=dados_formulario.get('modalidades', ''),
            quantidade_de_alunos=0,
            reitor=dados_formulario['nome'],
            endereco_instituicao=dados_formulario['endereco']
        )
        db.session.add(nova_instituicao)
        db.session.commit()

        # Salva os cursos selecionados na tabela cursos
        for nome_curso in dados_formulario['cursos_selecionados']:
            curso = Curso(
                nome=nome_curso,
                id_instituicao=nova_instituicao.id_instituicao
            )
            db.session.add(curso)
        db.session.commit()

        return True, 'Cadastro de Instituição realizado com sucesso! Faça login agora.', nova_instituicao

    except IntegrityError:
        db.session.rollback()
        return False, 'Erro: E-mail ou instituição já cadastrados.', None


def criar_chefe(dados_formulario):
    """
    Cria um novo chefe.

    Args:
        dados_formulario: Dicionário com dados do formulário

    Returns:
        tuple: (sucesso: bool, mensagem: str, chefe: Chefe ou None)
    """
    try:
        novo_chefe = Chefe(
            nome=dados_formulario['nome'],
            email=dados_formulario['email'],
            senha=generate_password_hash(dados_formulario['senha']),
            nome_empresa=dados_formulario['empresa_nome'],
            cargo=dados_formulario['cargo']
        )
        db.session.add(novo_chefe)
        db.session.commit()

        return True, 'Cadastro de Chefe realizado com sucesso! Faça login agora.', novo_chefe

    except IntegrityError:
        db.session.rollback()
        return False, 'Erro: E-mail ou chefe já cadastrados.', None


def atualizar_perfil_chefe(chefe, dados_formulario):
    """
    Atualiza o perfil de um chefe.

    Args:
        chefe: Objeto Chefe do banco de dados
        dados_formulario: Dicionário com dados do formulário

    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    try:
        # Validação do nome
        nome = dados_formulario['nome'].strip()
        if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', nome):
            return False, "O nome deve ter entre 2 e 30 letras e não pode conter números."

        # Validação do email duplicado
        novo_email = dados_formulario['email']
        email_existente = Chefe.query.filter(
            Chefe.email == novo_email, Chefe.id_chefe != chefe.id_chefe).first()
        if email_existente:
            return False, "Já existe um chefe cadastrado com este e-mail."

        # Validação do cargo
        cargo = dados_formulario['cargo']
        if cargo not in ['CEO', 'Gerente', 'Coordenador']:
            return False, "Selecione um cargo válido."

        # Atualizar dados
        chefe.nome = nome
        chefe.cargo = cargo
        chefe.nome_empresa = dados_formulario.get('nome_empresa', '')
        chefe.email = novo_email

        # Atualizar senha se fornecida
        senha_nova = dados_formulario.get('senha', '')
        if senha_nova:
            chefe.senha = generate_password_hash(senha_nova)

        db.session.commit()
        return True, "Perfil atualizado com sucesso!"

    except IntegrityError:
        db.session.rollback()
        return False, "Já existe um chefe cadastrado com este e-mail."


def atualizar_perfil_instituicao(instituicao, dados_formulario):
    """
    Atualiza o perfil de uma instituição.

    Args:
        instituicao: Objeto InstituicaodeEnsino do banco de dados
        dados_formulario: Dicionário com dados do formulário

    Returns:
        tuple: (sucesso: bool, mensagem: str)
    """
    try:
        # Validações
        nome_instituicao = dados_formulario['nome_instituicao'].strip()
        reitor = dados_formulario['reitor'].strip()

        if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,50}$', nome_instituicao):
            return False, "O nome da instituição deve ter entre 2 e 50 letras e não pode conter números."

        if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', reitor):
            return False, "O nome do reitor deve ter entre 2 e 30 letras e não pode conter números."

        # Validação do email duplicado
        novo_email = dados_formulario['email']
        email_existente = InstituicaodeEnsino.query.filter(
            InstituicaodeEnsino.email == novo_email,
            InstituicaodeEnsino.id_instituicao != instituicao.id_instituicao
        ).first()
        if email_existente:
            return False, "Já existe uma instituição cadastrada com este e-mail."

        # Validações específicas
        nota_mec = dados_formulario['nota_mec']
        if nota_mec not in ['1', '2', '3', '4', '5']:
            return False, "Nota MEC deve ser um valor entre 1 e 5."

        modalidades = dados_formulario['modalidades']
        if modalidades not in ['Presencial', 'Hibrido', 'EAD']:
            return False, "Selecione uma modalidade válida."

        # Atualizar dados
        instituicao.nome_instituicao = nome_instituicao
        instituicao.endereco_instituicao = dados_formulario['endereco_instituicao']
        instituicao.reitor = reitor
        instituicao.infraestrutura = dados_formulario['infraestrutura']
        instituicao.nota_mec = int(nota_mec)
        instituicao.modalidades = modalidades
        instituicao.email = novo_email

        # Atualizar senha se fornecida
        senha_nova = dados_formulario.get('senha', '')
        if senha_nova:
            instituicao.senha = generate_password_hash(senha_nova)

        db.session.commit()
        return True, "Perfil atualizado com sucesso!"

    except IntegrityError:
        db.session.rollback()
        return False, "Já existe uma instituição cadastrada com este e-mail."


def verificar_email_duplicado_instituicao(email):
    """
    Verifica se já existe uma instituição com o email fornecido.

    Args:
        email: Email para verificar

    Returns:
        bool: True se email já existe, False caso contrário
    """
    return InstituicaodeEnsino.query.filter_by(email=email).first() is not None


def verificar_email_duplicado_chefe(email):
    """
    Verifica se já existe um chefe com o email fornecido.

    Args:
        email: Email para verificar

    Returns:
        bool: True se email já existe, False caso contrário
    """
    return Chefe.query.filter_by(email=email).first() is not None
