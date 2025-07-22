# Dashboard Estoque - Backend Flask

Backend simples em Flask para gerenciamento de estoque integrado com Tiny ERP.

## Instalação

1. Criar ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. Instalar dependências:
```bash
pip install -r requirements.txt
```

3. Configurar variáveis de ambiente:
```bash
cp .env.example .env
# Editar .env com seu token Tiny
```

4. Executar:
```bash
python app.py
```

## Endpoints

- `GET /health` - Status do serviço
- `GET /api/v2/estoque/produto/{codigo}` - Buscar produto por código
- `POST /api/v2/estoque/ajustar` - Ajustar estoque (genérico)
- `POST /api/v2/estoque/ph510/adicionar` - Adicionar 1 unidade ao PH-510
- `POST /api/v2/estoque/ph510/remover` - Remover 1 unidade do PH-510

## Deploy

Para deploy em produção com gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_app()
```