## Mostra o HELP
all: help
	@echo "Ola $(LOGNAME), da uma olhada no help para ver os comandos"

## Faz as migrações e cria o banco de dados
migrations:
	python3 manage.py makemigrations
	python3 manage.py migrate

## Inicia o servidor
start:
	python3 manage.py runserver

## Roda os testes
test:
	python3 manage.py test

## Inicia o servidor e faz as migrações
full_start: migrations start

## Cria um super usuário
superuser:
	python3 manage.py createsuperuser

# region para montar o help
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=30

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
#endregion

