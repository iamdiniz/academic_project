# 🔐 CONFIGURAÇÃO DE SEGURANÇA - VARIÁVEIS DE AMBIENTE

## 🚨 IMPORTANTE: Configuração de Segurança

Este projeto agora está configurado para usar **variáveis de ambiente** em vez de senhas hardcoded no código.

## 📋 Passos para Configurar:

### 1. Criar o arquivo `.env`

```bash
# Renomeie o arquivo de exemplo
mv env_example.txt .env
```

### 2. Editar o arquivo `.env`

```bash
# Abra o arquivo .env e configure suas variáveis
nano .env
```

### 3. Gerar uma chave secreta segura

```bash
# Execute este comando para gerar uma chave única
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Configurar as variáveis no `.env`

```env
# Exemplo de configuração (ALTERE AS SENHAS!)
DB_USER=root
DB_PASS=sua_senha_super_segura_aqui
DB_HOST=db
DB_PORT=3306
DB_NAME=educ_invest

# URL completa do banco
DATABASE_URL=mysql+pymysql://root:sua_senha_super_segura_aqui@db:3306/educ_invest?charset=utf8mb4

# Chave secreta do Flask (GERE UMA NOVA!)
FLASK_SECRET_KEY=sua_chave_gerada_pelo_comando_acima
```

## 🔧 O que foi modificado:

### ✅ **app.py:**

- ❌ Removida: `app.secret_key = 'minha-chave-teste'`
- ✅ Adicionada: `app.secret_key = os.getenv('FLASK_SECRET_KEY')`
- ❌ Removida: `'mysql+pymysql://root:educ123@db:3306/educ_invest?charset=utf8mb4'`
- ✅ Mantida: `database_url = os.getenv("DATABASE_URL")`
- 🔧 Adicionada: `load_dotenv()` para carregar o arquivo .env

### ✅ **docker-compose.yaml:**

- ❌ Removidas: Senhas hardcoded
- ✅ Adicionado: `env_file: - .env`
- ✅ Adicionadas: Referências às variáveis `${VARIABLE_NAME}`

### ✅ **Novos arquivos:**

- `.env` (não commitado)
- `env_example.txt` (pode ser commitado)
- `.gitignore` (protege arquivos sensíveis)
- `SETUP_SECURITY.md` (este arquivo)

## 🚀 Como executar:

### Desenvolvimento local:

```bash
# 1. Configure o arquivo .env
# 2. Execute o projeto
python app.py
```

### Com Docker:

```bash
# 1. Configure o arquivo .env
# 2. Execute o docker-compose
docker-compose up --build
```

## 🔒 Segurança:

- ✅ **Nenhuma senha no código fonte**
- ✅ **Variáveis de ambiente para configurações sensíveis**
- ✅ **Arquivo .env protegido pelo .gitignore**
- ✅ **Validação de variáveis obrigatórias**
- ✅ **Pronto para produção**

## ⚠️ Lembre-se:

1. **NUNCA** commite o arquivo `.env`
2. **SEMPRE** use o `env_example.txt` como modelo
3. **ALTERE** as senhas padrão
4. **GERE** uma nova chave secreta para cada ambiente

## 🆘 Em caso de problemas:

Se você receber erros sobre variáveis não definidas:

1. Verifique se o arquivo `.env` existe
2. Verifique se todas as variáveis estão configuradas
3. Verifique se não há espaços extras nas variáveis
4. Reinicie o Docker se estiver usando containers
