"""
Modelos de domínio - Re-exporta os modelos da estrutura antiga.
"""

# Re-exportar todos os modelos da estrutura antiga para manter compatibilidade
from models import (
    db,
    Chefe,
    InstituicaodeEnsino,
    Curso,
    Aluno,
    SkillsDoAluno,
    SkillsHistorico,
    Acompanhamento,
    Indicacao,
    TwoFactor,
    ResetarSenha,
    PasswordHistory,
    LogAcesso,
)

# Re-exportar constantes do domínio
from .constants import (
    CURSOS_PADRAO,
    HARD_SKILLS_POR_CURSO,
    SOFT_SKILLS
)
