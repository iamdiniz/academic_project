# Sistema de Rate Limiting - DashTalent

## Como Funciona o Rate Limiting

O sistema de rate limiting protege contra ataques de força bruta com um **sistema de duas fases** que escala a segurança conforme as tentativas falhadas.

### Comportamento do Sistema

```
FASE 1 (Primeiras 3 tentativas):
✅ 1ª tentativa: Acesso normal
✅ 2ª tentativa: Acesso normal
✅ 3ª tentativa: Aviso "Última tentativa antes do bloqueio temporário"
❌ 4ª tentativa: Bloqueio temporário de 5 minutos

FASE 2 (Após desbloqueio temporário):
✅ 1ª tentativa: Acesso normal (com aviso "Você está na FASE 2 de segurança")
✅ 2ª tentativa: Acesso normal (com aviso "Você está na FASE 2 de segurança")
✅ 3ª tentativa: Aviso "Última tentativa antes do bloqueio permanente"
❌ 4ª tentativa: Bloqueio permanente (até redefinir senha)
```

### Configurações Atuais

- **MAX_LOGIN_ATTEMPTS**: 3 (permite 3 tentativas por fase)
- **BLOCK_DURATION**: 300 segundos (5 minutos de bloqueio temporário)
- **WARNING_THRESHOLD**: 3 (aviso na 3ª tentativa)

### Fluxo de Funcionamento Detalhado

#### FASE 1 - Primeira Escalação

1. **1ª tentativa**: Sistema inicializa contador na FASE 1
2. **2ª tentativa**: Login processado normalmente
3. **3ª tentativa**: Aviso "Última tentativa antes do bloqueio temporário"
4. **4ª tentativa**: Bloqueio temporário de 5 minutos

#### Transição para FASE 2

- Após 5 minutos de bloqueio temporário, o sistema automaticamente avança para FASE 2
- Contador é resetado para 0, mas a fase muda para 2

#### FASE 2 - Segunda Escalação

1. **1ª tentativa**: Aviso "Você está na FASE 2 de segurança. Cuidado com suas tentativas."
2. **2ª tentativa**: Aviso "Você está na FASE 2 de segurança. Cuidado com suas tentativas."
3. **3ª tentativa**: Aviso "Última tentativa antes do bloqueio permanente"
4. **4ª tentativa**: Bloqueio permanente (até redefinir senha)

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

### Segurança

- **Por email**: Mais granular que por IP
- **Duas fases**: Escalação progressiva de segurança
- **Temporário**: Bloqueio de 5 minutos evita abuso
- **Permanente**: Para contas comprometidas
- **Reset automático**: Após login bem-sucedido
- **Logs**: Todas as tentativas são registradas

### Cenários de Teste

1. **Usuário normal**: 1-3 tentativas → Login bem-sucedido → Reset para FASE 1
2. **Usuário com problemas**: 4 tentativas → Bloqueio temporário → FASE 2 → 4 tentativas → Bloqueio permanente
3. **Usuário recuperado**: Login bem-sucedido → Volta para FASE 1
4. **Usuário desbloqueado**: Desbloqueio manual → Volta para FASE 1
