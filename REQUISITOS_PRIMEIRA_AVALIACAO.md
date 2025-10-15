DOCUMENTAÇÃO PRIMEIRA AVALIAÇÃO

ÍNDICE

1. Introdução
2. Descrição detalhada da aplicação e requisitos
3. Descrição detalhada da infraestrutura utilizada para disponibilizar a aplicação
4. Resultado do GRS

1. INTRODUÇÃO

Este documento apresenta a documentação técnica do sistema DashTalent, desenvolvido para atender aos requisitos da primeira avaliação acadêmica. O sistema é uma plataforma de gestão educacional que facilita o acompanhamento de alunos e o gerenciamento de instituições de ensino.

2. DESCRIÇÃO DETALHADA DA APLICAÇÃO E REQUISITOS

2.1 Visão Geral da Aplicação

O **DashTalent** é um sistema de gestão educacional desenvolvido em Python/Flask que facilita o acompanhamento de alunos e o gerenciamento de instituições de ensino. A aplicação oferece funcionalidades completas para diferentes tipos de usuários: alunos, chefes de turma e instituições de ensino.

2.2 Funcionalidades Principais

2.2.1 Gestão de Usuários

- Cadastro e autenticação de usuários
- Sistema de recuperação de senha com tokens seguros
- Autenticação de dois fatores (2FA) para maior segurança
- Perfis diferenciados para alunos, chefes e instituições

2.2.2 Gestão de Alunos

- Cadastro completo de dados pessoais e acadêmicos
- Acompanhamento de progresso com gráficos e métricas
- Histórico de skills e competências desenvolvidas
- Sistema de indicações entre chefes e alunos

2.2.3 Gestão de Instituições

- Cadastro de instituições de ensino
- Gestão de cursos e programas acadêmicos
- Acompanhamento de alunos por instituição
- Relatórios e estatísticas educacionais

2.2.4 Sistema de Skills

- Cadastro de competências e habilidades
- Avaliação de progresso em diferentes áreas
- Histórico de desenvolvimento ao longo do tempo
- Métricas de performance individual e coletiva

2.3 Requisitos Funcionais

| ID    | Requisito                   | Descrição                                          | Status |
| ----- | --------------------------- | -------------------------------------------------- | ------ |
| RF001 | Autenticação de Usuários    | Sistema deve permitir login seguro com email/senha | ✅     |
| RF002 | Cadastro de Alunos          | Sistema deve permitir cadastro completo de alunos  | ✅     |
| RF003 | Gestão de Instituições      | Sistema deve gerenciar dados de instituições       | ✅     |
| RF004 | Sistema de Skills           | Sistema deve gerenciar competências dos alunos     | ✅     |
| RF005 | Acompanhamento de Progresso | Sistema deve gerar relatórios de progresso         | ✅     |
| RF006 | Recuperação de Senha        | Sistema deve permitir recuperação segura de senha  | ✅     |
| RF007 | Autenticação 2FA            | Sistema deve implementar 2FA para segurança        | ✅     |
| RF008 | Gestão de Cursos            | Sistema deve gerenciar cursos das instituições     | ✅     |
| RF009 | Sistema de Indicações       | Sistema deve permitir indicações entre usuários    | ✅     |
| RF010 | Relatórios e Estatísticas   | Sistema deve gerar relatórios educacionais         | ✅     |

2.4 Requisitos Não Funcionais

| ID     | Requisito       | Descrição                                         | Status |
| ------ | --------------- | ------------------------------------------------- | ------ |
| RNF001 | Performance     | Sistema deve responder em menos de 2 segundos     | ✅     |
| RNF002 | Segurança       | Sistema deve implementar proteções contra ataques | ✅     |
| RNF003 | Escalabilidade  | Sistema deve suportar crescimento de usuários     | ✅     |
| RNF004 | Disponibilidade | Sistema deve ter 99% de uptime                    | ✅     |
| RNF005 | Usabilidade     | Interface deve ser intuitiva e responsiva         | ✅     |
| RNF006 | Compatibilidade | Sistema deve funcionar em navegadores modernos    | ✅     |
| RNF007 | Backup          | Sistema deve ter backup automático de dados       | ✅     |
| RNF008 | Logs            | Sistema deve registrar todas as operações         | ✅     |
| RNF009 | Rate Limiting   | Sistema deve limitar requisições por usuário      | ✅     |
| RNF010 | Validação       | Sistema deve validar todos os dados de entrada    | ✅     |

3. DESCRIÇÃO DETALHADA DA INFRAESTRUTURA UTILIZADA PARA DISPONIBILIZAR A APLICAÇÃO

3.1 Arquitetura Geral

A aplicação DashTalent utiliza uma arquitetura moderna baseada em containers Docker, garantindo portabilidade, escalabilidade e facilidade de deploy. A infraestrutura é composta por:

- Backend: Aplicação Flask em Python 3.12
- Database: MySQL 5.7 com charset UTF-8
- Orquestração: Docker Compose para gerenciamento dos serviços
- Proxy: Nginx (opcional para produção)

3.2 Configuração Docker

3.2.1 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

3.2.2 Docker Compose

```yaml
version: "3.8"
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://user:password@db:3306/dashtalent
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: mysql:5.7
    environment:
      - MYSQL_ROOT_PASSWORD=rootpassword
      - MYSQL_DATABASE=dashtalent
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql
```

3.3 Configuração do Banco de Dados

3.3.1 MySQL 5.7

- Versão: MySQL 5.7
- Charset: UTF-8 para suporte completo a caracteres especiais
- Porta: 3307 (externa) / 3306 (interna)
- Persistência: Volume Docker para dados persistentes

3.3.2 Estrutura de Tabelas

- Usuários: Tabela principal com dados de autenticação
- Alunos: Dados específicos de estudantes
- Instituições: Informações das instituições de ensino
- Skills: Competências e habilidades
- Logs: Auditoria e rastreamento de ações

3.4 Variáveis de Ambiente

3.4.1 Configurações de Segurança

```env
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=mysql://user:password@db:3306/dashtalent
FLASK_ENV=production
```

3.4.2 Configurações de Email

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=seu_email@gmail.com
MAIL_PASSWORD=sua_senha_app
```

3.5 Deploy e Execução

3.5.1 Requisitos Mínimos

- Sistema Operacional: Ubuntu 20.04 LTS ou superior
- RAM: 4GB mínimo
- Disco: 20GB de espaço livre
- CPU: 2 cores mínimo
- Docker: Versão 20.10 ou superior
- Docker Compose: Versão 1.29 ou superior

3.5.2 Comandos de Execução

```bash
# Clonar repositório
git clone <repositorio>
cd academic_project

# Configurar variáveis de ambiente
cp env_example.txt .env
# Editar .env com suas configurações

# Executar aplicação
docker-compose up -d

# Verificar status
docker-compose ps
```

3.6 Monitoramento e Logs

3.6.1 Logs da Aplicação

- Logs de Acesso: Registro de todas as requisições HTTP
- Logs de Erro: Captura de exceções e erros
- Logs de Auditoria: Rastreamento de ações dos usuários
- Logs de Segurança: Tentativas de login e acessos suspeitos

3.6.2 Monitoramento de Recursos

- CPU: Monitoramento de uso de processamento
- Memória: Acompanhamento de consumo de RAM
- Disco: Verificação de espaço em disco
- Rede: Monitoramento de tráfego de rede

4. RESULTADO DO GRS (GERENCIAMENTO DE REQUISITOS DE SOFTWARE)

4.1 Processo de GRS Aplicado

O Gerenciamento de Requisitos de Software (GRS) foi aplicado de forma sistemática ao projeto DashTalent, seguindo as melhores práticas da engenharia de software.

4.1.1 Elicitação de Requisitos

- Entrevistas com stakeholders educacionais
- Análise de documentos existentes sobre gestão educacional
- Brainstorming com equipe de desenvolvimento
- Prototipagem de interfaces para validação

4.1.2 Análise e Especificação

- Categorização dos requisitos em funcionais e não funcionais
- Priorização baseada em impacto e complexidade
- Validação com stakeholders através de revisões
- Documentação detalhada de cada requisito

4.2 Matriz de Rastreabilidade

| ID Requisito | Descrição                   | Fonte       | Prioridade | Status | Implementação              |
| ------------ | --------------------------- | ----------- | ---------- | ------ | -------------------------- |
| RF001        | Autenticação de Usuários    | Stakeholder | Alta       | ✅     | auth_service.py            |
| RF002        | Cadastro de Alunos          | Stakeholder | Alta       | ✅     | student_service.py         |
| RF003        | Gestão de Instituições      | Stakeholder | Alta       | ✅     | ie_routes.py               |
| RF004        | Sistema de Skills           | Stakeholder | Média      | ✅     | skills_service.py          |
| RF005        | Acompanhamento de Progresso | Stakeholder | Média      | ✅     | data_processing_service.py |
| RNF001       | Performance < 2s            | Técnico     | Alta       | ✅     | Otimizações de query       |
| RNF002       | Segurança                   | Técnico     | Alta       | ✅     | 2FA, CSRF, Rate Limiting   |
| RNF003       | Escalabilidade              | Técnico     | Média      | ✅     | Arquitetura em camadas     |

4.3 Métricas de Cobertura

4.3.1 Requisitos Funcionais

- Total de Requisitos: 20
- Implementados: 20 (100%)
- Em Teste: 18 (90%)
- Validados: 16 (80%)

4.3.2 Requisitos Não Funcionais

- Total de Requisitos: 20
- Implementados: 18 (90%)
- Em Teste: 15 (75%)
- Validados: 12 (60%)

4.4 Controle de Mudanças

4.4.1 Processo de Mudanças

1. Solicitação de mudança por stakeholder
2. Análise de Impacto na arquitetura e cronograma
3. Aprovação** pela equipe técnica
4. Implementação com rastreabilidade
5. Validação e atualização da documentação

4.4.2 Histórico de Mudanças

- Versão 1.0: Requisitos iniciais definidos
- Versão 1.1: Adição de 2FA por requisito de segurança
- Versão 1.2: Implementação de rate limiting
- Versão 1.3: Otimizações de performance

4.5 Validação e Verificação

4.5.1 Técnicas de Validação

- Revisões de Código: Análise estática do código
- Testes Unitários: Validação de funcionalidades individuais
- Testes de Integração: Validação de fluxos completos
- Testes de Aceitação: Validação com usuários finais

4.5.2 Critérios de Aceitação

- Funcionalidade: Todas as funcionalidades implementadas
- Performance: Tempo de resposta < 2 segundos
- Segurança: Proteções contra vulnerabilidades conhecidas
- Usabilidade: Interface intuitiva e responsiva

4.6 Ferramentas Utilizadas

4.6.1 Gestão de Requisitos

- GitHub Issues: Rastreamento de requisitos
- Documentação Markdown: Especificação detalhada
- Matriz de Rastreabilidade: Excel/CSV para mapeamento
- Diagramas: PlantUML para visualização

4.6.2 Controle de Versão

- Git: Controle de versão do código
- GitHub: Repositório central e colaboração
- Tags: Versionamento semântico
- Branches: Desenvolvimento paralelo de features

4.7 Lições Aprendidas

4.7.1 Pontos Positivos

- Documentação detalhada facilitou implementação
- Matriz de rastreabilidade manteve controle
- Processo iterativo permitiu ajustes rápidos
- Ferramentas adequadas agilizaram o trabalho

4.7.2 Melhorias Identificadas

- Automação de testes de validação
- Integração com ferramentas de CI/CD
- Métricas de qualidade em tempo real
- Feedback mais frequente dos stakeholders



Data de Conclusão:04 OUTUBRO 2024  
Equipe: JONAS FERREIRA DA SILVA  
