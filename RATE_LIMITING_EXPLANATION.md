# Sistema de Rate Limiting - DashTalent

## Como Funciona o Rate Limiting

O sistema de rate limiting protege contra ataques de força bruta com um **sistema de duas fases** que escala a segurança conforme as tentativas falhadas.

### Comportamento do Sistema

```
FASE 1 (Primeiras 5 tentativas):
✅ 1ª tentativa: Acesso normal (registrada em log se falhar)
✅ 2ª tentativa: Acesso normal (registrada em log se falhar)
✅ 3ª tentativa: Acesso normal (registrada em log se falhar)
✅ 4ª tentativa: Acesso normal (registrada em log se falhar)
✅ 5ª tentativa: Aviso "Última tentativa antes do bloqueio temporário" (registrada em log se falhar)
❌ 6ª tentativa: Bloqueio temporário de 10 minutos (registrada em log)

FASE 2 (Após desbloqueio temporário):
✅ 1ª tentativa: Acesso normal (registrada em log se falhar)
✅ 2ª tentativa: Acesso normal (registrada em log se falhar)
✅ 3ª tentativa: Acesso normal (registrada em log se falhar)
✅ 4ª tentativa: Acesso normal (registrada em log se falhar)
✅ 5ª tentativa: Aviso "Última tentativa antes do bloqueio permanente" (registrada em log se falhar)
❌ 6ª tentativa: Bloqueio permanente (até redefinir senha) (registrada em log)
```

### Configurações Atuais

- **MAX_LOGIN_ATTEMPTS**: 5 (permite 5 tentativas por fase)
- **BLOCK_DURATION**: 600 segundos (10 minutos de bloqueio temporário)
- **WARNING_THRESHOLD**: 5 (aviso na 5ª tentativa)
- **LOG_FILE**: `logs/login_failures.log` (arquivo de log de falhas de login)

### Fluxo de Funcionamento Detalhado

#### FASE 1 - Primeira Escalação

1. **1ª tentativa**: Sistema inicializa contador na FASE 1. Se falhar, registra em log.
2. **2ª tentativa**: Login processado normalmente. Se falhar, registra em log.
3. **3ª tentativa**: Login processado normalmente. Se falhar, registra em log.
4. **4ª tentativa**: Login processado normalmente. Se falhar, registra em log.
5. **5ª tentativa**: Aviso "Última tentativa antes do bloqueio temporário". Se falhar, registra em log.
6. **6ª tentativa**: Bloqueio temporário de 10 minutos. Registra em log.

#### Transição para FASE 2

- Após 10 minutos de bloqueio temporário, o sistema automaticamente avança para FASE 2
- Contador é resetado para 0, mas a fase muda para 2

#### FASE 2 - Segunda Escalação

1. **1ª tentativa**: Login processado normalmente. Se falhar, registra em log.
2. **2ª tentativa**: Login processado normalmente. Se falhar, registra em log.
3. **3ª tentativa**: Login processado normalmente. Se falhar, registra em log.
4. **4ª tentativa**: Login processado normalmente. Se falhar, registra em log.
5. **5ª tentativa**: Aviso "Última tentativa antes do bloqueio permanente". Se falhar, registra em log.
6. **6ª tentativa**: Bloqueio permanente (até redefinir senha). Registra em log.

### Recuperação do Sistema

- **Login bem-sucedido**: Volta para FASE 1 (independente da fase atual)
- **Desbloqueio manual**: Reseta para FASE 1
- **Bloqueio permanente**: Requer redefinição de senha

### Bloqueio Permanente

Além do bloqueio temporário, existe um sistema de bloqueio permanente:

- **Lista**: `usuarios_bloqueados` (set de emails)
- **Verificação**: Antes do rate limiting
- **Mensagem**: "Sua conta foi bloqueada permanentemente. Redefina a senha para continuar."
- **Desbloqueio**: Apenas manual via função `desbloquear_usuario()`

### Funções Disponíveis

```python
# Verificar rate limiting
permitido, mensagem, tentativas_restantes = verificar_rate_limit(email)

# Resetar contador após login bem-sucedido (volta para FASE 1)
resetar_rate_limit(email)

# Bloquear usuário permanentemente
bloquear_usuario_permanentemente(email)

# Desbloquear usuário (volta para FASE 1)
desbloquear_usuario(email)

# Registrar falha de login em arquivo de log
registrar_falha_login(email, tentativa_numero)

# Obter número da tentativa atual
tentativa_atual = obter_numero_tentativa_atual(email)
```

### Exemplo de Uso

```python
# No processo de login
email = request.form['email']
senha = request.form['senha']

# Verificar bloqueio permanente
if email in usuarios_bloqueados:
    flash("Sua conta foi bloqueada permanentemente. Redefina a senha para continuar.", "danger")
    return render_template('login.html')

# Verificar rate limiting (com sistema de duas fases)
permitido, mensagem_rate_limit, _ = verificar_rate_limit(email)
if not permitido:
    flash(mensagem_rate_limit, "danger")
    return render_template('login.html')

# Processar login...
# Se login bem-sucedido:
resetar_rate_limit(email)  # Volta para FASE 1
```

### Sistema de Logging de Falhas

Todas as falhas de login são registradas em arquivo de log para auditoria e segurança:

- **Localização**: `logs/login_failures.log`
- **Formato**: `[YYYY-MM-DD HH:MM:SS] FALHA DE LOGIN - Email: {email} - Tentativa: {numero}/5`
- **Registro**: Cada tentativa falhada é registrada, incluindo a 5ª tentativa consecutiva no mesmo dia
- **Criação automática**: O diretório `logs/` é criado automaticamente se não existir

**Exemplo de entrada no log:**
```
[2024-01-15 14:30:25] FALHA DE LOGIN - Email: usuario@exemplo.com - Tentativa: 1/5
[2024-01-15 14:30:45] FALHA DE LOGIN - Email: usuario@exemplo.com - Tentativa: 2/5
[2024-01-15 14:31:10] FALHA DE LOGIN - Email: usuario@exemplo.com - Tentativa: 3/5
[2024-01-15 14:31:35] FALHA DE LOGIN - Email: usuario@exemplo.com - Tentativa: 4/5
[2024-01-15 14:32:00] FALHA DE LOGIN - Email: usuario@exemplo.com - Tentativa: 5/5
```

### Segurança

- **Por email**: Mais granular que por IP
- **Duas fases**: Escalação progressiva de segurança
- **Temporário**: Bloqueio de 10 minutos evita abuso
- **Permanente**: Para contas comprometidas
- **Reset automático**: Após login bem-sucedido
- **Logs em arquivo**: Todas as falhas de login são registradas em arquivo de log
- **Auditoria completa**: Inclui registro da 5ª tentativa consecutiva no mesmo dia

### Cenários de Teste

1. **Usuário normal**: 1-5 tentativas → Login bem-sucedido → Reset para FASE 1 (falhas registradas em log)
2. **Usuário com problemas**: 6 tentativas → Bloqueio temporário de 10 minutos → FASE 2 → 6 tentativas → Bloqueio permanente (todas as falhas registradas em log)
3. **Usuário recuperado**: Login bem-sucedido → Volta para FASE 1
4. **Usuário desbloqueado**: Desbloqueio manual → Volta para FASE 1
