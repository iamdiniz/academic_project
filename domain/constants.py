"""
Constantes do sistema - Define os valores padrão para cursos e skills.
"""

# Lista de cursos padrão disponíveis no sistema
CURSOS_PADRAO = [
    "Administração", "Agronomia", "Arquitetura", "Biologia", "Ciência da Computação",
    "Direito", "Educação Física", "Enfermagem", "Engenharia", "Farmácia", "Física",
    "Matemática", "Medicina", "Pedagogia", "Psicologia", "Química", "Sistemas de Informação",
]

# Mapeamento de hard skills por curso
HARD_SKILLS_POR_CURSO = {
    "Administração": [
        "Gestão de Pessoas", "Finanças", "Marketing", "Empreendedorismo", "Planejamento Estratégico"
    ],
    "Agronomia": [
        "Manejo de Solo", "Fitotecnia", "Irrigação", "Agroquímica", "Topografia"
    ],
    "Arquitetura": [
        "Desenho Técnico", "AutoCAD", "Maquetes", "Projetos Estruturais", "História da Arquitetura"
    ],
    "Biologia": [
        "Genética", "Microbiologia", "Ecologia", "Botânica", "Zoologia"
    ],
    "Ciência da Computação": [
        "Algoritmos", "Estruturas de Dados", "Programação", "Banco de Dados", "Redes de Computadores"
    ],
    "Direito": [
        "Direito Constitucional", "Direito Civil", "Direito Penal", "Processo Civil", "Processo Penal"
    ],
    "Educação Física": [
        "Fisiologia do Exercício", "Biomecânica", "Treinamento Esportivo", "Avaliação Física", "Primeiros Socorros"
    ],
    "Enfermagem": [
        "Procedimentos de Enfermagem", "Farmacologia", "Saúde Pública", "Cuidados Intensivos", "Primeiros Socorros"
    ],
    "Engenharia": [
        "Cálculo", "Física", "Desenho Técnico", "Materiais de Construção", "Gestão de Projetos"
    ],
    "Farmácia": [
        "Farmacologia", "Análises Clínicas", "Química Farmacêutica", "Microbiologia", "Toxicologia"
    ],
    "Física": [
        "Mecânica", "Eletromagnetismo", "Óptica", "Termodinâmica", "Física Moderna"
    ],
    "Matemática": [
        "Álgebra", "Geometria", "Cálculo", "Estatística", "Matemática Discreta"
    ],
    "Medicina": [
        "Anatomia", "Fisiologia", "Patologia", "Clínica Médica", "Cirurgia"
    ],
    "Pedagogia": [
        "Didática", "Psicologia da Educação", "Planejamento Escolar", "Avaliação Educacional", "Gestão Escolar"
    ],
    "Psicologia": [
        "Psicologia Clínica", "Psicologia Organizacional", "Psicopatologia", "Psicologia do Desenvolvimento", "Psicoterapia"
    ],
    "Química": [
        "Química Orgânica", "Química Inorgânica", "Fisico-Química", "Análises Químicas", "Bioquímica"
    ],
    "Sistemas de Informação": [
        "Java", "Python", "DevOps", "API", "Banco de Dados"
    ]
}

# Lista de soft skills padrão
SOFT_SKILLS = [
    "Participação", "Comunicação", "Proatividade",
    "Criatividade", "Trabalho em Equipe"
]
