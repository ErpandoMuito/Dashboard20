#!/bin/bash
#
# Script para testar o Dashboard v2.0 - Teste 3
# Executa validações e testes automatizados
#

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Dashboard v2.0 - Script de Teste ===${NC}"
echo "Executando testes do Teste 3..."
echo ""

# Verifica se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 não está instalado!${NC}"
    exit 1
fi

# Executa o teste
python3 /Users/rodrigo/Documents/DashboardNovo/teste3

# Captura o código de saída
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Todos os testes passaram!${NC}"
else
    echo ""
    echo -e "${RED}✗ Alguns testes falharam. Verifique o relatório.${NC}"
fi

exit $EXIT_CODE