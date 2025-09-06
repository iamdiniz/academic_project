import re
from utils.constants import CARGOS_VALIDOS, MODALIDADES_VALIDAS, NOTAS_MEC_VALIDAS

def validar_nome(nome, min_length=2, max_length=30):
    """
    Valida se o nome contém apenas letras e espaços
    
    Args:
        nome (str): Nome a ser validado
        min_length (int): Comprimento mínimo
        max_length (int): Comprimento máximo
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not nome or len(nome) < min_length or len(nome) > max_length:
        return False
    
    # Padrão: apenas letras, acentos e espaços
    pattern = r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$'
    return bool(re.match(pattern, nome))

def validar_email(email):
    """
    Valida formato básico de e-mail
    
    Args:
        email (str): E-mail a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not email:
        return False
    
    # Verifica se contém @ e .
    return '@' in email and '.' in email

def validar_contato(contato, min_digits=8):
    """
    Valida se o contato contém apenas números e tem o comprimento mínimo
    
    Args:
        contato (str): Contato a ser validado
        min_digits (int): Número mínimo de dígitos
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not contato:
        return False
    
    return contato.isdigit() and len(contato) >= min_digits

def validar_periodo(periodo, min_periodo=1, max_periodo=20):
    """
    Valida se o período está dentro do range permitido
    
    Args:
        periodo (str): Período a ser validado
        min_periodo (int): Período mínimo
        max_periodo (int): Período máximo
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not periodo:
        return False
    
    try:
        periodo_int = int(periodo)
        return min_periodo <= periodo_int <= max_periodo
    except ValueError:
        return False

def validar_cargo(cargo):
    """
    Valida se o cargo é válido
    
    Args:
        cargo (str): Cargo a ser validado
    
    Returns:
        bool: True se válido, False caso contrário
    """
    return cargo in CARGOS_VALIDOS

def validar_modalidade(modalidade):
    """
    Valida se a modalidade é válida
    
    Args:
        modalidade (str): Modalidade a ser validada
    
    Returns:
        bool: True se válido, False caso contrário
    """
    return modalidade in MODALIDADES_VALIDAS

def validar_nota_mec(nota_mec):
    """
    Valida se a nota MEC é válida
    
    Args:
        nota_mec (str): Nota MEC a ser validada
    
    Returns:
        bool: True se válido, False caso contrário
    """
    return nota_mec in NOTAS_MEC_VALIDAS
