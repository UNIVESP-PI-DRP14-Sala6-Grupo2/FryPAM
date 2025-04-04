# FryPAM

FryPAM é um sistema de Gerenciamento de Acesso Privilegiado para ambientes de nuvem, fornecendo acesso seguro e controlado a contas de nuvem em diferentes provedores.

## Recursos

- Suporte multi-tenant para gerenciar diferentes unidades organizacionais
- Gerenciamento de usuários com múltiplos papéis (Administrador, Usuário, Validador)
- Suporte para múltiplos provedores de nuvem:
  - Amazon Web Services (AWS)
  - Microsoft Azure (WIP)
  - Google Cloud Platform (GCP) (WIP)
  - Oracle Cloud Infrastructure (OCI) (WIP)
- Fluxo de trabalho de solicitação de senha com processo de aprovação
- Janelas de acesso com tempo limitado
- Suporte a Docker para ambientes de desenvolvimento e produção

## Arquitetura e Fluxo de Trabalho

```
                                       ┌───────────────┐
                                       │               │
                                       │   Interface   │
                                       │  de Usuário   │
                                       │   (Django)    │
                                       │               │
                                       └───────┬───────┘
                                               │
                                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         Sistema FryPAM                                │
│                                                                       │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐      │
│   │               │     │               │     │               │      │
│   │  Validação    │---->│  Aprovação    │---->│   Acesso      │      │
│   │  de Usuário   │     │  de Acesso    │     │  Temporário   │      │
│   │               │     │               │     │               │      │
│   └───────────────┘     └───────────────┘     └───────┬───────┘      │
│                                                       │               │
└───────────────────────────────────────────────────────┼───────────────┘
                                                        │
                                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                     Provedores de Nuvem                               │
│                                                                       │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐      │
│   │    AWS        │     │  Azure (WIP)  │     │   GCP (WIP)   │      │
│   │   ATIVO       │     │    Futuro     │     │    Futuro     │      │
│   │    ✓          │     │               │     │               │      │
│   └───────────────┘     └───────────────┘     └───────────────┘      │
│                                                                       │
│                         ┌───────────────┐                             │
│                         │  OCI (WIP)    │                             │
│                         │    Futuro     │                             │
│                         │               │                             │
│                         └───────────────┘                             │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Fluxo de Solicitação de Acesso

1. **Solicitação**: O usuário solicita acesso a uma conta AWS específica
2. **Validação**: O validador (responsável) revisa e aprova a solicitação
3. **Aprovação**: O sistema concede acesso temporário à conta solicitada
4. **Utilização**: O usuário acessa a conta durante o período de tempo aprovado
5. **Expiração**: Ao final do período, o acesso é automaticamente revogado

> **Nota**: Na versão atual, apenas a integração com AWS está completamente implementada. As integrações com Azure, GCP e OCI estão planejadas para versões futuras.

## Requisitos

- Python 3.x
- Django 5.1
- Docker e Docker Compose (opcional, para implantação em contêineres)

## Instalação

### Configuração para Desenvolvimento Local

1. Clone o repositório:
   ```
   git clone https://github.com/your-org/FryPAM.git
   cd FryPAM
   ```

2. Crie um ambiente virtual e instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure o banco de dados:
   ```
   make migrations
   ```

4. Crie um superusuário:
   ```
   make superuser
   ```

5. Inicie o servidor de desenvolvimento:
   ```
   make start
   ```

### Configuração com Docker

1. Construa e inicie os contêineres:
   ```
   docker-compose up -d
   ```

2. Execute as migrações dentro do contêiner:
   ```
   docker-compose exec web python manage.py migrate
   ```

3. Crie um superusuário dentro do contêiner:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

## Utilização

Acesse a aplicação em:
- Desenvolvimento local: http://localhost:8000/
- Servidor de desenvolvimento: https://FryPAM-dev.pavops.net/

Faça login com suas credenciais de administrador para:
- Gerenciar usuários e atribuir papéis
- Configurar tenants e contas de nuvem
- Processar solicitações de senha

## Desenvolvimento

### Comandos Make Disponíveis

- `make help` - Mostra os comandos disponíveis
- `make migrations` - Executa migrações de banco de dados
- `make start` - Inicia o servidor de desenvolvimento
- `make test` - Executa testes
- `make full_start` - Executa migrações e inicia o servidor
- `make superuser` - Cria uma conta de superusuário

## Licença

[Sua Licença Aqui]

## Contato

[Suas Informações de Contato]
