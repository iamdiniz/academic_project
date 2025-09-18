"""
Serviço de Validação - Funções de validação movidas do app.py.
Código movido para organizar responsabilidades, mantendo a lógica original.
"""

import re


def validar_email_formato(email):
    """
    Valida formato de email - código movido do app.py.
    Mantém a lógica original: if '@' not in email or '.' not in email
    """
    return '@' not in email or '.' not in email


def validar_periodo_formato(periodo):
    """
    Valida formato de período - código movido do app.py.
    Mantém a lógica original: if not periodo.isdigit() or int(periodo) < 1 or int(periodo) > 20
    """
    return not periodo.isdigit() or int(periodo) < 1 or int(periodo) > 20


def validar_contato_formato(contato_jovem):
    """
    Valida formato de contato - código movido do app.py.
    Mantém a lógica original: if not contato_jovem.isdigit() or len(contato_jovem) < 8
    """
    return not contato_jovem.isdigit() or len(contato_jovem) < 8


def validar_skill_valor(valor):
    """
    Valida valor de skill - código movido do app.py.
    Mantém a lógica original: if valor is None or not valor.isdigit() or int(valor) < 0 or int(valor) > 10
    """
    return valor is None or not valor.isdigit() or int(valor) < 0 or int(valor) > 10


def validar_nome_formato(nome):
    """
    Valida formato de nome - código movido do app.py.
    Mantém a lógica original: if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', nome)
    """
    return not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', nome)


def validar_cargo_formato(cargo):
    """
    Valida formato de cargo - código movido do app.py.
    Mantém a lógica original: if cargo not in ['CEO', 'Gerente', 'Coordenador']
    """
    return cargo not in ['CEO', 'Gerente', 'Coordenador']


def validar_senha_formato(senha):
    """
    Valida formato de senha - código movido do app.py.
    Mantém a lógica original: if len(senha_nova) < 8
    """
    return len(senha) < 8


def validar_nota_mec_formato(nota_mec):
    """
    Valida formato de nota MEC - código movido do app.py.
    Mantém a lógica original: if nota_mec not in ['1', '2', '3', '4', '5']
    """
    return nota_mec not in ['1', '2', '3', '4', '5']


def validar_modalidade_formato(modalidade):
    """
    Valida formato de modalidade - código movido do app.py.
    Mantém a lógica original: if modalidade not in ['Presencial', 'Hibrido', 'EAD']
    """
    return modalidade not in ['Presencial', 'Hibrido', 'EAD']
