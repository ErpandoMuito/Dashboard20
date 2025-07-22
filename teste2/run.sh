#!/bin/bash

echo "==========================================="
echo "🔍 INICIANDO SISTEMA DEBUG - LOGS SÃO VIDA!"
echo "==========================================="
echo ""

# Mostrar informações do sistema
echo "📊 INFORMAÇÕES DO SISTEMA:"
echo "  - Data/Hora: $(date)"
echo "  - Diretório: $(pwd)"
echo "  - Usuário: $(whoami)"
echo "  - Python: $(python3 --version)"
echo "  - PIP: $(pip3 --version)"
echo ""

# Verificar se Redis está rodando
echo "🔴 VERIFICANDO REDIS..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping > /dev/null 2>&1; then
        echo "  ✅ Redis está rodando!"
        echo "  - Versão: $(redis-cli --version)"
        echo "  - Info: $(redis-cli INFO server | grep redis_version)"
    else
        echo "  ❌ Redis não está respondendo!"
        echo "  Tentando iniciar Redis..."
        redis-server --daemonize yes
        sleep 2
        if redis-cli ping > /dev/null 2>&1; then
            echo "  ✅ Redis iniciado com sucesso!"
        else
            echo "  ❌ Falha ao iniciar Redis!"
        fi
    fi
else
    echo "  ⚠️ redis-cli não encontrado!"
fi
echo ""

# Criar diretório static se não existir
echo "📁 VERIFICANDO ESTRUTURA DE DIRETÓRIOS..."
if [ ! -d "static" ]; then
    echo "  - Criando diretório static/"
    mkdir -p static
fi
echo "  ✅ Estrutura OK"
echo ""

# Instalar dependências
echo "📦 INSTALANDO DEPENDÊNCIAS..."
echo "  - Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✅ Ambiente virtual criado"
else
    echo "  ✅ Ambiente virtual já existe"
fi

echo "  - Ativando ambiente virtual..."
source venv/bin/activate

echo "  - Instalando pacotes..."
pip install --upgrade pip
pip install -r requirements.txt
echo ""

# Mostrar variáveis de ambiente relevantes
echo "🔐 VARIÁVEIS DE AMBIENTE:"
echo "  - REDIS_URL: ${REDIS_URL:-não definida}"
echo "  - TINY_API_TOKEN: ${TINY_API_TOKEN:0:10}..."
echo "  - PATH: $PATH"
echo ""

# Criar arquivo .env se não existir
if [ ! -f ".env" ]; then
    echo "📝 Criando arquivo .env de exemplo..."
    cat > .env << EOF
# Configurações do Redis
REDIS_URL=redis://localhost:6379

# Token da API Tiny (obter em tiny.com.br)
TINY_API_TOKEN=seu_token_aqui
EOF
    echo "  ✅ Arquivo .env criado!"
    echo "  ⚠️ IMPORTANTE: Edite o arquivo .env com suas credenciais!"
else
    echo "✅ Arquivo .env encontrado"
fi
echo ""

# Iniciar servidor
echo "🚀 INICIANDO SERVIDOR..."
echo "  - URL: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Debug UI: http://localhost:8000/static/index.html"
echo ""
echo "📋 LOGS DO SERVIDOR:"
echo "==========================================="

# Executar com muitos logs
export PYTHONUNBUFFERED=1
python3 backend.py