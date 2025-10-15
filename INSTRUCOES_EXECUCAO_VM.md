# 🖥️ INSTRUÇÕES PARA MÁQUINA VIRTUAL - DASHTALENT

## 📋 **REQUISITOS DO SISTEMA**

### **Especificações Mínimas da VM:**

- **Sistema Operacional:** Ubuntu 20.04 LTS ou superior
- **RAM:** Mínimo 4GB (Recomendado: 8GB)
- **Armazenamento:** Mínimo 20GB de espaço livre
- **CPU:** 2 cores (Recomendado: 4 cores)
- **Rede:** Acesso à internet para download de dependências

---

## 🚀 **INSTALAÇÃO E CONFIGURAÇÃO**

### **1. Preparação do Ambiente**

```bash
# Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências básicas
sudo apt install -y curl wget git vim nano

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalações
docker --version
docker-compose --version
```

### **2. Clonagem do Projeto**

```bash
# Clonar o repositório (substitua pela URL real)
git clone [URL_DO_REPOSITORIO] dashTalent
cd dashTalent

# Ou se for um arquivo compactado
# wget [URL_DO_ARQUIVO_ZIP]
# unzip dashTalent.zip
# cd dashTalent
```

### **3. Configuração das Variáveis de Ambiente**

```bash
# Copiar arquivo de exemplo
cp env_example.txt .env

# Editar arquivo de configuração
nano .env
```

**Conteúdo do arquivo .env:**

```env
# Banco de Dados
DB_USER=root
DB_PASS=DashTalent2024!
DB_HOST=db
DB_PORT=3306
DB_NAME=educ_invest

# URL completa do banco
DATABASE_URL=mysql+pymysql://root:DashTalent2024!@db:3306/educ_invest?charset=utf8mb4

# Chave secreta do Flask (gerar nova)
FLASK_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

### **4. Execução da Aplicação**

```bash
# Construir as imagens Docker
docker-compose build

# Executar a aplicação
docker-compose up -d

# Verificar status dos containers
docker-compose ps

# Ver logs da aplicação
docker-compose logs -f backend
```

### **5. Verificação da Instalação**

```bash
# Verificar se a aplicação está rodando
curl http://localhost:5000

# Verificar banco de dados
docker-compose exec db mysql -u root -p
# Senha: DashTalent2024!
```

---

## 🌐 **ACESSO À APLICAÇÃO**

### **URLs de Acesso:**

- **Aplicação Principal:** http://localhost:5000
- **Banco de Dados:** localhost:3307
- **Interface Web:** http://[IP_DA_VM]:5000

### **Contas de Teste:**

#### **Instituição de Ensino:**

- **Email:** instituicao@teste.com
- **Senha:** instituicao123
- **Nome:** Universidade Teste

#### **Chefe/Gestor:**

- **Email:** chefe@teste.com
- **Senha:** chefe123
- **Nome:** João Silva

#### **Aluno:**

- **Email:** aluno@teste.com
- **Senha:** aluno123
- **Nome:** Maria Santos

---

## 🔧 **COMANDOS ÚTEIS**

### **Gerenciamento de Containers:**

```bash
# Parar a aplicação
docker-compose down

# Reiniciar a aplicação
docker-compose restart

# Ver logs em tempo real
docker-compose logs -f

# Acessar container da aplicação
docker-compose exec backend bash

# Acessar banco de dados
docker-compose exec db mysql -u root -p
```

### **Backup e Restore:**

```bash
# Backup do banco de dados
docker-compose exec db mysqldump -u root -p educ_invest > backup.sql

# Restore do banco de dados
docker-compose exec -T db mysql -u root -p educ_invest < backup.sql
```

### **Limpeza do Sistema:**

```bash
# Parar e remover containers
docker-compose down -v

# Remover imagens
docker-compose down --rmi all

# Limpeza completa do Docker
docker system prune -a
```

---

## 🐛 **SOLUÇÃO DE PROBLEMAS**

### **Problema: Aplicação não inicia**

```bash
# Verificar logs
docker-compose logs backend

# Verificar se o banco está rodando
docker-compose ps

# Reiniciar tudo
docker-compose down && docker-compose up -d
```

### **Problema: Erro de conexão com banco**

```bash
# Verificar se o banco está acessível
docker-compose exec backend ping db

# Verificar variáveis de ambiente
docker-compose exec backend env | grep DATABASE
```

### **Problema: Porta já em uso**

```bash
# Verificar processos usando a porta
sudo netstat -tulpn | grep :5000

# Parar processo conflitante
sudo kill -9 [PID]
```

### **Problema: Permissões Docker**

```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Fazer logout e login novamente
# Ou executar:
newgrp docker
```

---

## 📊 **MONITORAMENTO**

### **Status dos Serviços:**

```bash
# Status geral
docker-compose ps

# Uso de recursos
docker stats

# Logs de todos os serviços
docker-compose logs
```

### **Métricas de Performance:**

- **CPU:** `docker stats --no-stream`
- **Memória:** `docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}"`
- **Rede:** `docker network ls`

---

## 🔒 **CONFIGURAÇÕES DE SEGURANÇA**

### **Firewall (Opcional):**

```bash
# Instalar UFW
sudo apt install ufw

# Configurar regras básicas
sudo ufw allow ssh
sudo ufw allow 5000
sudo ufw enable
```

### **SSL/HTTPS (Para Produção):**

```bash
# Instalar certbot
sudo apt install certbot

# Gerar certificado (substitua pelo domínio real)
sudo certbot certonly --standalone -d seu-dominio.com
```

---

## 📝 **NOTAS IMPORTANTES**

1. **Primeira Execução:** A primeira execução pode demorar alguns minutos para baixar as imagens Docker
2. **Banco de Dados:** O banco é criado automaticamente na primeira execução
3. **Dados de Teste:** O sistema inclui dados de exemplo para demonstração
4. **Backup:** Faça backup regular dos dados importantes
5. **Atualizações:** Sempre teste em ambiente de desenvolvimento antes de atualizar em produção

---

## 📞 **SUPORTE**

Para problemas ou dúvidas:

- **Logs da Aplicação:** `docker-compose logs backend`
- **Logs do Banco:** `docker-compose logs db`
- **Status dos Containers:** `docker-compose ps`
- **Documentação:** Consulte `DOCUMENTACAO_PRIMEIRA_AVALIACAO.md`

---

**🎯 A aplicação estará disponível em:** http://localhost:5000  
**📅 Data de Criação:** Dezembro 2024  
**👥 Equipe:** Desenvolvedores Acadêmicos
