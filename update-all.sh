#!/bin/bash

echo "🔄 Atualizando tudo automaticamente..."

# Atualizar VSCode extensions
echo "📦 Atualizando extensões do VSCode..."
code --update-extensions

# Atualizar Homebrew packages
echo "🍺 Atualizando Homebrew..."
brew update && brew upgrade

# Atualizar npm global packages
echo "📦 Atualizando pacotes npm globais..."
npm update -g

# Atualizar pip packages
echo "🐍 Atualizando pacotes Python..."
pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U 2>/dev/null

# Limpar caches
echo "🧹 Limpando caches..."
brew cleanup
npm cache clean --force 2>/dev/null

echo "✅ Tudo atualizado!"