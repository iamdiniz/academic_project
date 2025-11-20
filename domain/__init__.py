"""
Módulo domain - Re-exporta modelos e constantes da estrutura antiga.
"""

from .models import *
from .constants import *

__all__ = [
    # Models
    'LogAcesso', 'InstituicaodeEnsino', 'Curso', 'Aluno', 'Chefe',
    'SkillsDoAluno', 'SkillsHistorico', 'Acompanhamento', 'Indicacao',
    'TwoFactor', 'ResetarSenha', 'PasswordHistory',
    # Constants
    'CURSOS_PADRAO', 'HARD_SKILLS_POR_CURSO', 'SOFT_SKILLS',
    # Database
    'db'
]
