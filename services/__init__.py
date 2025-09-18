"""
Módulo services - Contém os serviços de negócio do sistema.
Código movido do app.py para organizar responsabilidades.
"""

from .rate_limit_service import (
    verificar_rate_limit, resetar_rate_limit,
    bloquear_usuario_permanentemente, desbloquear_usuario
)
from .email_service import (
    enviar_email, gerar_codigo_verificacao
)
from .two_factor_service import (
    _get_or_create_2fa_record, _generate_qr_data_uri,
    processar_two_factor_setup, processar_two_factor_verify, processar_two_factor_disable
)
from .audit_log_service import (
    registrar_log
)
from .pagination_service import (
    paginate_items, get_pagination_data
)
from .validation_service import (
    validar_email_formato, validar_periodo_formato, validar_contato_formato,
    validar_skill_valor, validar_nome_formato, validar_cargo_formato,
    validar_senha_formato, validar_nota_mec_formato, validar_modalidade_formato
)
from .password_validation_service import (
    validar_senha_minima, validar_confirmacao_senha,
    validar_campos_obrigatorios_instituicao, validar_campos_obrigatorios_chefe,
    validar_campos_obrigatorios_aluno, validar_campos_obrigatorios_aluno_edicao
)
from .skills_service import (
    validar_skills_por_curso
)
from .auth_service import (
    load_user, bloquear_chefe, bloquear_instituicao,
    processar_cadastro, processar_login, processar_perfil
)
from .data_processing_service import (
    processar_aluno_com_skills, processar_alunos_indicados_por_chefe,
    processar_alunos_acompanhados_por_chefe, processar_alunos_por_instituicao,
    processar_skills_para_edicao, calcular_total_skills_por_habilidades
)
from .user_service import (
    criar_instituicao_ensino, criar_chefe, atualizar_perfil_chefe,
    atualizar_perfil_instituicao, verificar_email_duplicado_instituicao,
    verificar_email_duplicado_chefe
)
from .password_recovery_service import (
    processar_solicitacao_recuperacao, verificar_codigo_digitado,
    processar_nova_senha, validar_token_reset,
    processar_esqueceu_senha, processar_verificar_codigo,
    processar_verificar_codigo_post, processar_nova_senha_page
)
from .admin_service import (
    admin_bloquear_usuario, admin_desbloquear_usuario
)
from .course_service import (
    cadastrar_curso, obter_cursos_instituicao, obter_cursos_por_instituicao,
    validar_curso_existe
)
from .indication_service import (
    indicar_aluno, remover_indicacao, acompanhar_aluno, remover_acompanhamento,
    obter_alunos_indicados, paginar_alunos_indicados
)
from .skills_history_service import (
    obter_historico_aluno, criar_snapshot_skills_inicial,
    salvar_historico_skills_atualizacao, obter_estatisticas_evolucao
)
from .student_service import (
    cadastrar_aluno, remover_aluno, obter_detalhes_aluno, atualizar_aluno,
    obter_alunos_por_curso, paginar_alunos_por_curso
)

__all__ = [
    # Rate Limit Service
    'verificar_rate_limit', 'resetar_rate_limit', 'bloquear_usuario_permanentemente', 'desbloquear_usuario',
    # Email Service
    'enviar_email', 'gerar_codigo_verificacao',
    # Two Factor Service
    '_get_or_create_2fa_record', '_generate_qr_data_uri',
    'processar_two_factor_setup', 'processar_two_factor_verify', 'processar_two_factor_disable',
    # Audit Log Service
    'registrar_log',
    # Pagination Service
    'paginate_items', 'get_pagination_data',
    # Validation Service
    'validar_email_formato', 'validar_periodo_formato', 'validar_contato_formato',
    'validar_skill_valor', 'validar_nome_formato', 'validar_cargo_formato',
    'validar_senha_formato', 'validar_nota_mec_formato', 'validar_modalidade_formato',
    # Password Validation Service
    'validar_senha_minima', 'validar_confirmacao_senha',
    'validar_campos_obrigatorios_instituicao', 'validar_campos_obrigatorios_chefe',
    'validar_campos_obrigatorios_aluno', 'validar_campos_obrigatorios_aluno_edicao',
    # Skills Service
    'validar_skills_por_curso',
    # Auth Service
    'load_user', 'bloquear_chefe', 'bloquear_instituicao',
    'processar_cadastro', 'processar_login', 'processar_perfil',
    # Data Processing Service
    'processar_aluno_com_skills', 'processar_alunos_indicados_por_chefe',
    'processar_alunos_acompanhados_por_chefe', 'processar_alunos_por_instituicao',
    'processar_skills_para_edicao', 'calcular_total_skills_por_habilidades',
    # User Service
    'criar_instituicao_ensino', 'criar_chefe', 'atualizar_perfil_chefe',
    'atualizar_perfil_instituicao', 'verificar_email_duplicado_instituicao',
    'verificar_email_duplicado_chefe',
    # Password Recovery Service
    'processar_solicitacao_recuperacao', 'verificar_codigo_digitado',
    'processar_nova_senha', 'validar_token_reset',
    'processar_esqueceu_senha', 'processar_verificar_codigo',
    'processar_verificar_codigo_post', 'processar_nova_senha_page',
    # Admin Service
    'admin_bloquear_usuario', 'admin_desbloquear_usuario',
    # Course Service
    'cadastrar_curso', 'obter_cursos_instituicao', 'obter_cursos_por_instituicao',
    'validar_curso_existe',
    # Indication Service
    'indicar_aluno', 'remover_indicacao', 'acompanhar_aluno', 'remover_acompanhamento',
    'obter_alunos_indicados', 'paginar_alunos_indicados',
    # Skills History Service
    'obter_historico_aluno', 'criar_snapshot_skills_inicial',
    'salvar_historico_skills_atualizacao', 'obter_estatisticas_evolucao',
    # Student Service
    'cadastrar_aluno', 'remover_aluno', 'obter_detalhes_aluno', 'atualizar_aluno',
    'obter_alunos_por_curso', 'paginar_alunos_por_curso'
]
