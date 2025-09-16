from .acompanhamentos import Acompanhamento, Indicacao
from .alunos import Aluno
from .auth import TwoFactor, ResetarSenha
from .base import db
from .chefes import Chefe
from .cursos import Curso
from .instituicao import InstituicaodeEnsino
from .logs import LogAcesso
from .skills import SkillsDoAluno, SkillsHistorico

__all__ = [
    'Acompanhamento', 'Aluno', 'Chefe', 'Curso', 'db',
    'Indicacao', 'InstituicaodeEnsino', 'LogAcesso',
    'ResetarSenha', 'SkillsDoAluno', 'SkillsHistorico', 'TwoFactor'
]