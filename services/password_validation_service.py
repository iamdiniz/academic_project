"""
Serviço de Validação de Senha.
Define e aplica a política de senhas da aplicação.
"""

import re

PASSWORD_POLICY_MESSAGE = (
    "A senha deve ter pelo menos 10 caracteres e incluir letras maiúsculas, "
    "letras minúsculas, números e caracteres especiais."
)


def _senha_para_validacao(senha: str) -> str:
    return senha or ""


def avaliar_requisitos_senha(senha: str):
    """
    Retorna um dicionário com o status de cada requisito da política.
    """
    senha_normalizada = _senha_para_validacao(senha)
    return {
        'comprimento': len(senha_normalizada) >= 10,
        'maiuscula': bool(re.search(r'[A-Z]', senha_normalizada)),
        'minuscula': bool(re.search(r'[a-z]', senha_normalizada)),
        'digito': bool(re.search(r'\d', senha_normalizada)),
        'especial': bool(re.search(r'[^A-Za-z0-9]', senha_normalizada)),
    }


def validar_senha_minima(senha):
    """
    Retorna True quando a senha NÃO atende à política de segurança.
    Mantém compatibilidade com chamadas existentes.
    """
    requisitos = avaliar_requisitos_senha(senha)
    return not senha or not all(requisitos.values())


def validar_confirmacao_senha(senha, confirmar_senha):
    """
    Valida confirmação de senha - código movido do app.py.
    Mantém a lógica original: if senha != confirmar_senha
    """
    return senha != confirmar_senha


def validar_campos_obrigatorios_instituicao(nome, email, senha, instituicao_nome, endereco, cursos_selecionados):
    """
    Valida campos obrigatórios para instituição - código movido do app.py.
    Mantém a lógica original: if not nome or not email or not senha or not instituicao_nome or not endereco or not cursos_selecionados
    """
    return not nome or not email or not senha or not instituicao_nome or not endereco or not cursos_selecionados


def validar_campos_obrigatorios_chefe(nome, email, senha, empresa_nome, cargo):
    """
    Valida campos obrigatórios para chefe - código movido do app.py.
    Mantém a lógica original: if not nome or not email or not senha or not empresa_nome or not cargo
    """
    return not nome or not email or not senha or not empresa_nome or not cargo


def validar_campos_obrigatorios_aluno(nome_jovem, data_nascimento, endereco_jovem, contato_jovem, email, curso, formacao, periodo):
    """
    Valida campos obrigatórios para aluno - código movido do app.py.
    Mantém a lógica original: if not nome_jovem or not data_nascimento or not endereco_jovem or not contato_jovem or not email or not curso or not formacao or not periodo
    """
    return not nome_jovem or not data_nascimento or not endereco_jovem or not contato_jovem or not email or not curso or not formacao or not periodo


def validar_campos_obrigatorios_aluno_edicao(nome_jovem, data_nascimento, contato_jovem, email, endereco_jovem, formacao, periodo):
    """
    Valida campos obrigatórios para edição de aluno - código movido do app.py.
    Mantém a lógica original: if not nome_jovem or not data_nascimento or not contato_jovem or not email or not endereco_jovem or not formacao or not periodo
    """
    return not nome_jovem or not data_nascimento or not contato_jovem or not email or not endereco_jovem or not formacao or not periodo
