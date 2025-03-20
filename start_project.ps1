# Script PowerShell para iniciar o projeto Django
# Autor: Cascade
# Data: 2025-03-20

# Definir preferência de ação de erro para parar em erros
$ErrorActionPreference = "Stop"

# Definir cores para saída
$GREEN = [ConsoleColor]::Green
$YELLOW = [ConsoleColor]::Yellow
$RED = [ConsoleColor]::Red
$CYAN = [ConsoleColor]::Cyan

# Função para exibir mensagens coloridas
function Write-ColoredMessage {
    param (
        [string]$Message,
        [ConsoleColor]$Color = [ConsoleColor]::White
    )
    Write-Host $Message -ForegroundColor $Color
}

# Função para verificar se um comando existe
function Test-CommandExists {
    param (
        [string]$Command
    )
    
    $exists = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    return $exists
}

# Verificar se o Python está instalado
Write-ColoredMessage "Verificando se o Python está instalado..." $CYAN
if (-not (Test-CommandExists "python")) {
    Write-ColoredMessage "O Python não está instalado. Por favor, instale o Python 3.8 ou superior." $RED
    exit 1
}

# Verificar versão do Python
$pythonVersion = (python --version) 2>&1
Write-ColoredMessage "Encontrado $pythonVersion" $GREEN

# Verificar se o pip está instalado
Write-ColoredMessage "Verificando se o pip está instalado..." $CYAN
if (-not (Test-CommandExists "pip")) {
    Write-ColoredMessage "O pip não está instalado. Por favor, instale o pip." $RED
    exit 1
}

# Criar ambiente virtual se não existir
$venvPath = ".venv"
if (-not (Test-Path $venvPath)) {
    Write-ColoredMessage "Criando ambiente virtual..." $CYAN
    python -m venv $venvPath
    if (-not $?) {
        Write-ColoredMessage "Falha ao criar ambiente virtual." $RED
        exit 1
    }
    Write-ColoredMessage "Ambiente virtual criado com sucesso." $GREEN
} else {
    Write-ColoredMessage "Ambiente virtual já existe." $GREEN
}

# Ativar ambiente virtual
Write-ColoredMessage "Ativando ambiente virtual..." $CYAN
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
try {
    & $activateScript
    Write-ColoredMessage "Ambiente virtual ativado." $GREEN
} catch {
    Write-ColoredMessage "Falha ao ativar ambiente virtual: $_" $RED
    exit 1
}

# Instalar dependências
Write-ColoredMessage "Instalando dependências..." $CYAN
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    if (-not $?) {
        Write-ColoredMessage "Falha ao instalar dependências." $RED
        exit 1
    }
    Write-ColoredMessage "Dependências instaladas com sucesso." $GREEN
} else {
    Write-ColoredMessage "requirements.txt não encontrado. Instalando Django..." $YELLOW
    pip install django
    if (-not $?) {
        Write-ColoredMessage "Falha ao instalar Django." $RED
        exit 1
    }
    Write-ColoredMessage "Django instalado com sucesso." $GREEN
}

# Criar diretório estático se não existir
$staticPath = "static"
if (-not (Test-Path $staticPath)) {
    Write-ColoredMessage "Criando diretório estático..." $CYAN
    New-Item -ItemType Directory -Path $staticPath | Out-Null
    Write-ColoredMessage "Diretório estático criado." $GREEN
}

# Criar migrações
Write-ColoredMessage "Criando migrações..." $CYAN
python manage.py makemigrations
if (-not $?) {
    Write-ColoredMessage "Falha ao criar migrações." $RED
    exit 1
}
Write-ColoredMessage "Migrações criadas com sucesso." $GREEN

# Aplicar migrações
Write-ColoredMessage "Aplicando migrações..." $CYAN
python manage.py migrate
if (-not $?) {
    Write-ColoredMessage "Falha ao aplicar migrações." $RED
    exit 1
}
Write-ColoredMessage "Migrações aplicadas com sucesso." $GREEN

# Coletar arquivos estáticos
Write-ColoredMessage "Coletando arquivos estáticos..." $CYAN
python manage.py collectstatic --noinput
if (-not $?) {
    Write-ColoredMessage "Falha ao coletar arquivos estáticos." $YELLOW
    Write-ColoredMessage "Isso não é crítico, continuando..." $YELLOW
}

# Criar superusuário se não existir
Write-ColoredMessage "Verificando se superusuário existe..." $CYAN
$superuserExists = python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
print(User.objects.filter(is_superuser=True).exists())
"

if ($superuserExists -eq "False") {
    Write-ColoredMessage "Nenhum superusuário encontrado. Deseja criar um? (s/n)" $YELLOW
    $createSuperuser = Read-Host
    if ($createSuperuser -eq "s") {
        python manage.py createsuperuser
    }
}

# Iniciar servidor de desenvolvimento
Write-ColoredMessage "Iniciando servidor de desenvolvimento..." $CYAN
Write-ColoredMessage "O servidor estará disponível em http://127.0.0.1:8000/" $GREEN
Write-ColoredMessage "Pressione Ctrl+C para parar o servidor." $YELLOW
python manage.py runserver
