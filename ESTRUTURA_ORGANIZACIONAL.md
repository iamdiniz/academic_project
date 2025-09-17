# Estrutura Organizacional do Projeto

Este documento descreve a nova organização do projeto, separando responsabilidades em camadas bem definidas.

## Estrutura de Pastas

```
academic_project/
├── domain/                    # Camada de Domínio
│   ├── __init__.py           # Exports do módulo domain
│   ├── constants.py          # Constantes do sistema
│   └── models.py             # Modelos de dados (entidades)
├── services/                 # Camada de Serviços
│   ├── __init__.py           # Exports do módulo services
│   ├── rate_limit_service.py # Serviço de rate limiting
│   ├── email_service.py      # Serviço de email
│   ├── two_factor_service.py # Serviço de 2FA
│   └── audit_log_service.py  # Serviço de auditoria
├── models/                   # Modelos antigos (manter para compatibilidade)
├── static/                   # Arquivos estáticos
├── templates/                # Templates HTML
└── app.py                    # Aplicação principal
```

## Camada de Domínio (`domain/`)

### `constants.py`

Contém todas as constantes do sistema:

- `CURSOS_PADRAO`: Lista de cursos disponíveis
- `HARD_SKILLS_POR_CURSO`: Mapeamento de hard skills por curso
- `SOFT_SKILLS`: Lista de soft skills padrão

### `models.py`

Contém todos os modelos de dados do sistema:

- `LogAcesso`: Logs de auditoria
- `InstituicaodeEnsino`: Instituições de ensino
- `Curso`: Cursos oferecidos
- `Aluno`: Alunos cadastrados
- `Chefe`: Chefes/gestores
- `SkillsDoAluno`: Habilidades dos alunos
- `SkillsHistorico`: Histórico de habilidades
- `Acompanhamento`: Acompanhamentos entre chefes e alunos
- `Indicacao`: Indicações de alunos
- `TwoFactor`: Configurações de 2FA
- `ResetarSenha`: Tokens de recuperação de senha

## Camada de Serviços (`services/`)

### `rate_limit_service.py`

Gerencia tentativas de login e bloqueios:

- `verificar_rate_limit()`: Verifica se pode tentar login
- `resetar_rate_limit()`: Reseta contador após login bem-sucedido
- `bloquear_usuario_permanentemente()`: Bloqueia usuário permanentemente
- `desbloquear_usuario()`: Desbloqueia usuário

### `email_service.py`

Gerencia envio de emails:

- `enviar_email()`: Função genérica de envio
- `gerar_codigo_verificacao()`: Gera códigos de 6 dígitos
- `enviar_email_recuperacao_senha()`: Email de recuperação
- `enviar_email_boas_vindas()`: Email de boas-vindas
- `enviar_email_notificacao_indicacao()`: Notificação de indicação

### `two_factor_service.py`

Gerencia autenticação de dois fatores:

- `_get_or_create_2fa_record()`: Obtém ou cria registro 2FA
- `_generate_qr_data_uri()`: Gera QR code para configuração
- `verificar_codigo_2fa()`: Verifica código 2FA
- `ativar_2fa()`: Ativa 2FA
- `desativar_2fa()`: Desativa 2FA
- `is_2fa_habilitado()`: Verifica se 2FA está ativo

### `audit_log_service.py`

Gerencia logs de auditoria:

- `registrar_log()`: Função genérica de log
- `registrar_login()`: Log de login
- `registrar_logout()`: Log de logout
- `registrar_cadastro()`: Log de cadastro
- `registrar_2fa_setup()`: Log de configuração 2FA
- `registrar_indicacao()`: Log de indicação
- `registrar_acompanhamento()`: Log de acompanhamento
- `obter_logs_usuario()`: Obtém logs de um usuário
- `obter_logs_recentes()`: Obtém logs recentes

## Como Usar a Nova Estrutura

### Importando Modelos e Constantes

```python
from domain import (
    LogAcesso, InstituicaodeEnsino, Curso, Aluno, Chefe,
    CURSOS_PADRAO, HARD_SKILLS_POR_CURSO, SOFT_SKILLS, db
)
```

### Importando Serviços

```python
from services import (
    verificar_rate_limit, resetar_rate_limit,
    enviar_email, gerar_codigo_verificacao,
    _get_or_create_2fa_record, _generate_qr_data_uri,
    registrar_log
)
```

### Exemplo de Uso dos Serviços

```python
# Rate Limiting
permitido, mensagem, tentativas = verificar_rate_limit(email)
if permitido:
    # Processar login
    resetar_rate_limit(email)

# Email
sucesso, msg = enviar_email_recuperacao_senha(email, nome, codigo)

# 2FA
qr_uri, otpauth_uri = _generate_qr_data_uri('DashTalent', email, secret)

# Auditoria
registrar_login(nome_usuario, cargo, tipo_usuario)
```

## Benefícios da Nova Estrutura

1. **Separação de Responsabilidades**: Cada camada tem uma responsabilidade específica
2. **Reutilização**: Serviços podem ser reutilizados em diferentes partes da aplicação
3. **Manutenibilidade**: Código mais organizado e fácil de manter
4. **Testabilidade**: Serviços podem ser testados independentemente
5. **Escalabilidade**: Estrutura preparada para crescimento do projeto

## Migração

A estrutura antiga em `models/` foi mantida para compatibilidade. Para migrar gradualmente:

1. Importe os novos módulos onde necessário
2. Substitua chamadas diretas por chamadas aos serviços
3. Teste cada mudança antes de prosseguir
4. Remova imports antigos quando não forem mais necessários

## Próximos Passos

1. Atualizar `app.py` para usar os novos serviços
2. Criar testes unitários para os serviços
3. Documentar APIs dos serviços
4. Implementar cache onde apropriado
5. Adicionar validações nos serviços

