# FryPAM - Privileged Access Management
# Makefile para facilitar o desenvolvimento e operações

# Configurações
PYTHON = python3
MANAGE = $(PYTHON) manage.py
PIP = pip3
APP_NAME = pam
DOCKER_COMPOSE = docker-compose

# Cores para output
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
BLUE   := $(shell tput -Txterm setaf 4)
WHITE  := $(shell tput -Txterm setaf 7)
RED    := $(shell tput -Txterm setaf 1)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=30

## Mostra o HELP
all: help
	@echo "Olá $(LOGNAME), dê uma olhada no help para ver os comandos disponíveis"

## Instala as dependências do projeto
install:
	@echo "$(BLUE)Instalando dependências...$(RESET)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)Dependências instaladas com sucesso!$(RESET)"




## Atualiza as dependências do projeto
update-deps:
	@echo "$(BLUE)Atualizando dependências...$(RESET)"
	$(PIP) install --upgrade -r requirements.txt
	@echo "$(GREEN)Dependências atualizadas com sucesso!$(RESET)"

## Faz as migrações e cria o banco de dados
migrations:
	@echo "$(BLUE)Criando migrações...$(RESET)"
	$(MANAGE) makemigrations
	@echo "$(BLUE)Aplicando migrações...$(RESET)"
	$(MANAGE) migrate
	@echo "$(GREEN)Migrações aplicadas com sucesso!$(RESET)"

## Inicia o servidor de desenvolvimento
start:
	@echo "$(BLUE)Iniciando servidor de desenvolvimento...$(RESET)"
	$(MANAGE) runserver

## Inicia o servidor em uma porta específica (make start-port PORT=8001)
start-port:
	@echo "$(BLUE)Iniciando servidor na porta $(PORT)...$(RESET)"
	$(MANAGE) runserver 0.0.0.0:$(PORT)

## Roda os testes
test:
	@echo "$(BLUE)Executando testes...$(RESET)"
	$(MANAGE) test

## Roda os testes com cobertura
test-coverage:
	@echo "$(BLUE)Executando testes com cobertura...$(RESET)"
	coverage run --source='.' $(MANAGE) test
	coverage report
	coverage html
	@echo "$(GREEN)Relatório de cobertura gerado em htmlcov/index.html$(RESET)"

## Inicia o servidor e faz as migrações
full-start: migrations start

## Cria um super usuário
superuser:
	@echo "$(BLUE)Criando super usuário...$(RESET)"
	$(MANAGE) createsuperuser

## Coleta arquivos estáticos
collectstatic:
	@echo "$(BLUE)Coletando arquivos estáticos...$(RESET)"
	$(MANAGE) collectstatic --noinput
	@echo "$(GREEN)Arquivos estáticos coletados com sucesso!$(RESET)"

## Limpa arquivos Python compilados
clean:
	@echo "$(BLUE)Limpando arquivos compilados...$(RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	@echo "$(GREEN)Limpeza concluída!$(RESET)"

## Verifica a qualidade do código com flake8
lint:
	@echo "$(BLUE)Verificando qualidade do código...$(RESET)"
	flake8 $(APP_NAME)
	@echo "$(GREEN)Verificação concluída!$(RESET)"

## Formata o código com black
format:
	@echo "$(BLUE)Formatando código com black...$(RESET)"
	black $(APP_NAME)
	@echo "$(GREEN)Formatação concluída!$(RESET)"

## Inicia o ambiente Docker
docker-up:
	@echo "$(BLUE)Iniciando containers Docker...$(RESET)"
	$(DOCKER_COMPOSE) up -d
	@echo "$(GREEN)Containers iniciados!$(RESET)"

## Para o ambiente Docker
docker-down:
	@echo "$(BLUE)Parando containers Docker...$(RESET)"
	$(DOCKER_COMPOSE) down
	@echo "$(GREEN)Containers parados!$(RESET)"

## Exibe logs dos containers Docker
docker-logs:
	@echo "$(BLUE)Exibindo logs dos containers...$(RESET)"
	$(DOCKER_COMPOSE) logs -f

## Reinicia o ambiente Docker
docker-restart: docker-down docker-up
	@echo "$(GREEN)Ambiente Docker reiniciado!$(RESET)"

## Cria um backup do banco de dados
backup:
	@echo "$(BLUE)Criando backup do banco de dados...$(RESET)"
	$(MANAGE) dumpdata --exclude auth.permission --exclude contenttypes > backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "$(GREEN)Backup criado com sucesso!$(RESET)"

## Restaura um backup do banco de dados (make restore FILE=backup_file.json)
restore:
	@echo "$(BLUE)Restaurando backup do banco de dados...$(RESET)"
	$(MANAGE) loaddata $(FILE)
	@echo "$(GREEN)Backup restaurado com sucesso!$(RESET)"

## Gera documentação das APIs
api-docs:
	@echo "$(BLUE)Gerando documentação das APIs...$(RESET)"
	$(MANAGE) spectacular --file schema.yml
	@echo "$(GREEN)Documentação gerada com sucesso!$(RESET)"

## Cria e ativa um ambiente virtual
setup-virtualenv:
	@echo "$(BLUE)Criando ambiente virtual...$(RESET)"
	$(PIP) install virtualenv
	virtualenv .venv
	@echo "$(GREEN)Ambiente virtual criado com sucesso!$(RESET)"
	@echo "$(YELLOW)Para ativar o ambiente virtual, execute:$(RESET)"
	@echo "$(YELLOW)source .venv/bin/activate$(RESET)"

## Configura ambiente de desenvolvimento completo
setup-dev: install migrations collectstatic
	@echo "$(GREEN)Ambiente de desenvolvimento configurado com sucesso!$(RESET)"
	@echo "$(YELLOW)Agora você pode criar um superusuário com 'make superuser' e iniciar o servidor com 'make start'$(RESET)"

## Limpa e reinicia o banco de dados (CUIDADO: remove todos os dados)
reset-db:
	@echo "$(RED)ATENÇÃO: Esta operação irá remover todos os dados do banco!$(RESET)"
	@read -p "Tem certeza que deseja continuar? (s/N): " confirm; \
	if [ "$$confirm" = "s" ] || [ "$$confirm" = "S" ]; then \
		echo "$(BLUE)Reiniciando banco de dados...$(RESET)"; \
		$(MANAGE) reset_db --noinput; \
		$(MANAGE) migrate; \
		echo "$(GREEN)Banco de dados reiniciado com sucesso!$(RESET)"; \
	else \
		echo "$(YELLOW)Operação cancelada.$(RESET)"; \
	fi

## Verifica a segurança das dependências
check-security:
	@echo "$(BLUE)Verificando vulnerabilidades nas dependências...$(RESET)"
	safety check -r requirements.txt
	@echo "$(GREEN)Verificação concluída!$(RESET)"

## Exibe versões das dependências instaladas
show-deps:
	@echo "$(BLUE)Dependências instaladas:$(RESET)"
	$(PIP) freeze

## Show help
help:
	@echo ''
	@echo 'Uso:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.PHONY: all help install update-deps migrations start start-port test test-coverage full-start superuser collectstatic clean lint format docker-up docker-down docker-logs docker-restart backup restore api-docs setup-dev reset-db check-security show-deps
