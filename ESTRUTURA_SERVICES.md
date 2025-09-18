# 📁 ESTRUTURA COMPLETA DA PASTA SERVICES

## 📂 **PASTA: `academic_project/services/`**

```
services/
├── __init__.py                           # ✅ IMPLEMENTADO - Gerenciador de imports
├── audit_log_service.py                  # ✅ IMPLEMENTADO - Logs de auditoria
├── auth_service.py                       # ✅ IMPLEMENTADO - Autenticação e autorização
├── data_processing_service.py            # ✅ IMPLEMENTADO - Processamento de dados
├── email_service.py                      # ✅ IMPLEMENTADO - Envio de emails
├── pagination_service.py                 # ✅ IMPLEMENTADO - Paginação de dados
├── password_recovery_service.py          # ✅ IMPLEMENTADO - Recuperação de senha
├── password_validation_service.py        # ✅ IMPLEMENTADO - Validações de senha
├── rate_limit_service.py                 # ✅ IMPLEMENTADO - Rate limiting
├── skills_service.py                     # ✅ IMPLEMENTADO - Validações de skills
├── two_factor_service.py                 # ✅ IMPLEMENTADO - 2FA
├── user_service.py                       # ✅ IMPLEMENTADO - Operações de usuários
├── validation_service.py                 # ✅ IMPLEMENTADO - Validações de formato
├── admin_service.py                      # ⏳ PENDENTE - Operações administrativas
├── course_service.py                     # ⏳ PENDENTE - Operações de cursos
├── indication_service.py                 # ⏳ PENDENTE - Indicações e acompanhamentos
├── skills_history_service.py             # ⏳ PENDENTE - Histórico de skills
└── student_service.py                    # ⏳ PENDENTE - Operações de alunos
```

---

## ✅ **SERVIÇOS IMPLEMENTADOS (13 arquivos)**

### 1. **`__init__.py`** - Gerenciador Central

```python
"""
Módulo services - Contém os serviços de negócio do sistema.
Código movido do app.py para organizar responsabilidades.
"""

# Imports de todos os serviços
from .rate_limit_service import verificar_rate_limit, resetar_rate_limit
from .email_service import enviar_email, gerar_codigo_verificacao
# ... (todos os imports)

__all__ = [
    # Lista de todas as funções exportadas
]
```

### 2. **`audit_log_service.py`** - Logs de Auditoria

```python
"""
Serviço de Log de Auditoria - Código movido do app.py.
"""
def registrar_log(acao, usuario_nome, cargo, tipo_usuario):
    # Registra ações no banco de dados
```

### 3. **`auth_service.py`** - Autenticação

```python
"""
Serviço de Autenticação - Código movido do app.py.
"""
def load_user(user_id):
    # Carrega usuário para Flask-Login

def bloquear_chefe(f):
    # Decorator para bloquear chefes

def bloquear_instituicao(f):
    # Decorator para bloquear instituições
```

### 4. **`data_processing_service.py`** - Processamento de Dados

```python
"""
Serviço de Processamento de Dados - Código movido do app.py.
"""
def processar_aluno_com_skills(aluno):
    # Processa dados do aluno com skills

def processar_alunos_indicados_por_chefe(chefe_id):
    # Processa alunos indicados por chefe

def processar_alunos_acompanhados_por_chefe(chefe_id):
    # Processa alunos acompanhados por chefe

def processar_alunos_por_instituicao(instituicao_id):
    # Processa alunos por instituição

def processar_skills_para_edicao(skills_json):
    # Processa skills para edição

def calcular_total_skills_por_habilidades(skills_dict):
    # Calcula total de skills por habilidades
```

### 5. **`email_service.py`** - Envio de Emails

```python
"""
Serviço de Email - Código movido do app.py.
"""
def enviar_email(destinatario, assunto, corpo):
    # Envia email

def gerar_codigo_verificacao():
    # Gera código de verificação
```

### 6. **`pagination_service.py`** - Paginação

```python
"""
Serviço de Paginação - Código movido do app.py.
"""
def paginate_items(items, page, per_page=12):
    # Pagina lista de itens

def get_pagination_data(items, page, per_page=12):
    # Obtém dados de paginação
```

### 7. **`password_recovery_service.py`** - Recuperação de Senha

```python
"""
Serviço de Recuperação de Senha - Código movido do app.py.
"""
def processar_solicitacao_recuperacao(email):
    # Processa solicitação de recuperação

def verificar_codigo_digitado(email, codigo):
    # Verifica código digitado

def processar_nova_senha(email, codigo, nova_senha):
    # Processa nova senha

def validar_token_reset(email, codigo):
    # Valida token de reset
```

### 8. **`password_validation_service.py`** - Validações de Senha

```python
"""
Serviço de Validação de Senha - Código movido do app.py.
"""
def validar_senha_minima(senha):
    # Valida senha mínima

def validar_confirmacao_senha(senha, confirmar_senha):
    # Valida confirmação de senha

def validar_campos_obrigatorios_instituicao(dados):
    # Valida campos obrigatórios da instituição

def validar_campos_obrigatorios_chefe(dados):
    # Valida campos obrigatórios do chefe

def validar_campos_obrigatorios_aluno(dados):
    # Valida campos obrigatórios do aluno

def validar_campos_obrigatorios_aluno_edicao(dados):
    # Valida campos obrigatórios na edição do aluno
```

### 9. **`rate_limit_service.py`** - Rate Limiting

```python
"""
Serviço de Rate Limiting - Código movido do app.py.
"""
def verificar_rate_limit(email):
    # Verifica rate limit

def resetar_rate_limit(email):
    # Reseta rate limit

def bloquear_usuario_permanentemente(email):
    # Bloqueia usuário permanentemente

def desbloquear_usuario(email):
    # Desbloqueia usuário
```

### 10. **`skills_service.py`** - Validações de Skills

```python
"""
Serviço de Skills - Código movido do app.py.
"""
def validar_skills_por_curso(curso, hard_skills_dict, soft_skills_dict):
    # Valida skills por curso
```

### 11. **`two_factor_service.py`** - Autenticação de Dois Fatores

```python
"""
Serviço de 2FA - Código movido do app.py.
"""
def _get_or_create_2fa_record(user_id, user_type):
    # Obtém ou cria registro 2FA

def _generate_qr_data_uri(secret_key, user_email):
    # Gera QR code para 2FA
```

### 12. **`user_service.py`** - Operações de Usuários

```python
"""
Serviço de Usuários - Código movido do app.py.
"""
def criar_instituicao_ensino(dados):
    # Cria instituição de ensino

def criar_chefe(dados):
    # Cria chefe

def atualizar_perfil_chefe(chefe_id, dados):
    # Atualiza perfil do chefe

def atualizar_perfil_instituicao(instituicao_id, dados):
    # Atualiza perfil da instituição

def verificar_email_duplicado_instituicao(email, instituicao_id=None):
    # Verifica email duplicado da instituição

def verificar_email_duplicado_chefe(email, chefe_id=None):
    # Verifica email duplicado do chefe
```

### 13. **`validation_service.py`** - Validações de Formato

```python
"""
Serviço de Validação - Código movido do app.py.
"""
def validar_email_formato(email):
    # Valida formato de email

def validar_periodo_formato(periodo):
    # Valida formato de período

def validar_contato_formato(contato):
    # Valida formato de contato

def validar_skill_valor(valor):
    # Valida valor de skill

def validar_nome_formato(nome):
    # Valida formato de nome

def validar_cargo_formato(cargo):
    # Valida formato de cargo

def validar_senha_formato(senha):
    # Valida formato de senha

def validar_nota_mec_formato(nota_mec):
    # Valida formato de nota MEC

def validar_modalidade_formato(modalidade):
    # Valida formato de modalidade
```

---

## ⏳ **SERVIÇOS PENDENTES (5 arquivos)**

### 1. **`admin_service.py`** - Operações Administrativas

```python
"""
Serviço Administrativo - Código a ser movido do app.py.
"""
def bloquear_usuario_admin(email, motivo):
    # Bloqueia usuário via admin

def desbloquear_usuario_admin(email):
    # Desbloqueia usuário via admin

def listar_usuarios_bloqueados():
    # Lista usuários bloqueados

def obter_estatisticas_sistema():
    # Obtém estatísticas do sistema
```

### 2. **`course_service.py`** - Operações de Cursos

```python
"""
Serviço de Cursos - Código a ser movido do app.py.
"""
def criar_curso(dados):
    # Cria novo curso

def listar_cursos_instituicao(instituicao_id):
    # Lista cursos da instituição

def buscar_alunos_por_curso(curso_id, periodo=None):
    # Busca alunos por curso

def filtrar_alunos_por_periodo(alunos, periodo):
    # Filtra alunos por período

def ordenar_alunos_por_skills(alunos, ordenacao):
    # Ordena alunos por skills

def obter_estatisticas_curso(curso_id):
    # Obtém estatísticas do curso
```

### 3. **`indication_service.py`** - Indicações e Acompanhamentos

```python
"""
Serviço de Indicações - Código a ser movido do app.py.
"""
def indicar_aluno(chefe_id, aluno_id):
    # Indica aluno para chefe

def remover_indicacao(chefe_id, aluno_id):
    # Remove indicação

def acompanhar_aluno(chefe_id, aluno_id):
    # Inicia acompanhamento

def remover_acompanhamento(chefe_id, aluno_id):
    # Remove acompanhamento

def listar_alunos_indicados(chefe_id):
    # Lista alunos indicados

def listar_alunos_acompanhados(chefe_id):
    # Lista alunos acompanhados

def verificar_indicacao_existe(chefe_id, aluno_id):
    # Verifica se indicação existe

def verificar_acompanhamento_existe(chefe_id, aluno_id):
    # Verifica se acompanhamento existe
```

### 4. **`skills_history_service.py`** - Histórico de Skills

```python
"""
Serviço de Histórico de Skills - Código a ser movido do app.py.
"""
def criar_historico_skills(aluno_id, skills_anteriores, skills_novas):
    # Cria histórico de skills

def buscar_historico_aluno(aluno_id):
    # Busca histórico do aluno

def calcular_evolucao_skills(aluno_id):
    # Calcula evolução das skills

def gerar_comparacao_historico(aluno_id, data_inicio, data_fim):
    # Gera comparação do histórico

def obter_estatisticas_evolucao(aluno_id):
    # Obtém estatísticas de evolução

def exportar_historico_aluno(aluno_id):
    # Exporta histórico do aluno
```

### 5. **`student_service.py`** - Operações de Alunos

```python
"""
Serviço de Alunos - Código a ser movido do app.py.
"""
def criar_aluno(dados):
    # Cria novo aluno

def atualizar_aluno(aluno_id, dados):
    # Atualiza dados do aluno

def remover_aluno(aluno_id):
    # Remove aluno

def buscar_aluno_por_id(aluno_id):
    # Busca aluno por ID

def atualizar_skills_aluno(aluno_id, skills_dict):
    # Atualiza skills do aluno

def validar_dados_aluno(dados):
    # Valida dados do aluno

def obter_estatisticas_aluno(aluno_id):
    # Obtém estatísticas do aluno

def buscar_alunos_por_filtros(filtros):
    # Busca alunos por filtros

def exportar_dados_aluno(aluno_id):
    # Exporta dados do aluno
```

---

## 📊 **ESTATÍSTICAS FINAIS**

### **✅ Implementado:**

- **13 serviços** funcionais
- **~200+ linhas** removidas do `app.py`
- **34 rotas** no `app.py` (todas funcionais)
- **1494 linhas** no `app.py` atual

### **⏳ Potencial:**

- **5 novos serviços** podem ser criados
- **~15-20 rotas** ainda podem ser migradas
- **~300-400 linhas** adicionais podem ser removidas
- **Resultado final:** `app.py` com **~1000-1100 linhas**

### **🎯 Ordem de Implementação Sugerida:**

1. **`student_service.py`** - Maior impacto (4 rotas principais)
2. **`indication_service.py`** - Funcionalidades relacionadas
3. **`course_service.py`** - Operações de cursos
4. **`skills_history_service.py`** - Histórico de skills
5. **`admin_service.py`** - Operações administrativas

---

## 🔧 **COMO USAR**

### **Importar um serviço:**

```python
from services import nome_da_funcao
# ou
from services.nome_do_servico import nome_da_funcao
```

### **Exemplo de uso:**

```python
# Antes (no app.py)
if '@' not in email or '.' not in email:
    flash("Email inválido", "danger")

# Depois (usando service)
if validar_email_formato(email):
    flash("Email inválido", "danger")
```

---

**📝 Nota:** Todos os serviços mantêm a lógica original do `app.py`, apenas organizando o código em módulos específicos para melhor manutenção e reutilização.
