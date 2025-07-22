#!/bin/bash

# Script para fazer build de todos os frontends React

echo "🚀 Iniciando build de todos os frontends..."

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para fazer build
build_frontend() {
    local teste_dir=$1
    local teste_name=$2
    
    echo -e "\n${YELLOW}📦 Building ${teste_name}...${NC}"
    
    if [ -d "$teste_dir" ]; then
        cd "$teste_dir"
        
        # Verificar se é um projeto React
        if [ -f "package.json" ]; then
            # Instalar dependências se necessário
            if [ ! -d "node_modules" ]; then
                echo "Installing dependencies..."
                npm install
            fi
            
            # Fazer build
            echo "Building React app..."
            npm run build
            
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ ${teste_name} build concluído!${NC}"
            else
                echo -e "${RED}✗ Erro no build de ${teste_name}${NC}"
            fi
        else
            # Se não for React, criar um app React simples
            echo "Criando React app para ${teste_name}..."
            
            # Criar package.json
            cat > package.json << EOF
{
  "name": "${teste_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

            # Criar estrutura básica
            mkdir -p src public
            
            # Criar public/index.html
            cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Dashboard - %TESTE_NAME%</title>
</head>
<body>
    <noscript>Você precisa habilitar JavaScript para usar este app.</noscript>
    <div id="root"></div>
</body>
</html>
EOF
            sed -i "s/%TESTE_NAME%/${teste_name}/g" public/index.html

            # Criar src/index.js
            cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

            # Criar src/App.js com base no teste
            case $teste_name in
                "teste1")
                    cp /Users/rodrigo/Documents/DashboardNovo/dashboard-v2/teste1/index.html src/App.js
                    # Converter HTML para React component
                    ;;
                "teste5")
                    # Usar o HTML existente como base
                    echo "import React from 'react';" > src/App.js
                    echo "function App() { return <div>Dashboard ${teste_name}</div>; }" >> src/App.js
                    echo "export default App;" >> src/App.js
                    ;;
                *)
                    cat > src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const response = await axios.get(`/TESTE_NAME/api/health`);
      setData(response.data);
    } catch (error) {
      console.error('Erro ao carregar dados:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>Dashboard TESTE_NAME</h1>
      {loading ? (
        <p>Carregando...</p>
      ) : (
        <pre>{JSON.stringify(data, null, 2)}</pre>
      )}
    </div>
  );
}

export default App;
EOF
                    sed -i "s/TESTE_NAME/${teste_name}/g" src/App.js
                    ;;
            esac
            
            # Instalar e fazer build
            npm install
            npm run build
        fi
        
        cd - > /dev/null
    else
        echo -e "${RED}✗ Diretório ${teste_dir} não encontrado${NC}"
    fi
}

# Base directory
BASE_DIR="/Users/rodrigo/Documents/DashboardNovo/dashboard-v2"

# Build cada teste
for i in 1 2 3 4 5; do
    build_frontend "$BASE_DIR/teste$i" "teste$i"
done

echo -e "\n${GREEN}✅ Build de todos os frontends concluído!${NC}"
echo -e "${YELLOW}📝 Nota: Os builds estão em cada pasta teste*/build/${NC}"