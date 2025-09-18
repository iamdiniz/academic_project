"""
Serviço de Validação de Senha - Funções de validação de senha movidas do app.py.
Código movido para organizar responsabilidades, mantendo a lógica original.
"""


def validar_senha_minima(senha):
    """
    Valida senha mínima - código movido do app.py.
    Mantém a lógica original: if not senha or len(senha) < 8
    """
    return not senha or len(senha) < 8


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
