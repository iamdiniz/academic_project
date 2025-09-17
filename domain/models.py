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
    LogAcesso,
)

# Re-exportar constantes da estrutura antiga
from models.base import (
    CURSOS_PADRAO,
    HARD_SKILLS_POR_CURSO,
    SOFT_SKILLS
)
