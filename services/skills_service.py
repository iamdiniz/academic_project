"""
Serviço de Skills - Funções de validação de skills movidas do app.py.
Código movido para organizar responsabilidades, mantendo a lógica original.
"""

from domain import HARD_SKILLS_POR_CURSO, SOFT_SKILLS


def validar_skills_por_curso(curso, hard_skills_dict, soft_skills_dict):
    """
    Valida skills por curso - código movido do app.py.
    Mantém a lógica original exatamente igual.
    """
    # Curso deve ser válido
    if curso not in HARD_SKILLS_POR_CURSO:
        return False, f"Curso '{curso}' não é permitido."
    # Hard skills: 5, nomes exatos, valores entre 0 e 10
    hard_labels = HARD_SKILLS_POR_CURSO[curso]
    if set(hard_skills_dict.keys()) != set(hard_labels):
        return False, f"As hard skills devem ser exatamente: {', '.join(hard_labels)}."
    for valor in hard_skills_dict.values():
        if not isinstance(valor, int) or valor < 0 or valor > 10:
            return False, "Todas as hard skills devem ser números inteiros de 0 a 10."
    # Soft skills: 5, nomes exatos, valores entre 0 e 10
    if set(soft_skills_dict.keys()) != set(SOFT_SKILLS):
        return False, f"As soft skills devem ser exatamente: {', '.join(SOFT_SKILLS)}."
    for valor in soft_skills_dict.values():
        if not isinstance(valor, int) or valor < 0 or valor > 10:
            return False, "Todas as soft skills devem ser números inteiros de 0 a 10."
    return True, ""
