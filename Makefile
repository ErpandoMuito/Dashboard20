# Makefile principal para desenvolvimento

# Backend
backend-dev:
	cd backend && uvicorn main:app --reload

backend-test:
	cd backend && pytest -v -m 'not e2e'

backend-install:
	cd backend && pip install -r requirements.txt -r requirements-test.txt

# Frontend
frontend-dev:
	cd frontend && npm start

frontend-build:
	cd frontend && npm run build

frontend-install:
	cd frontend && npm install

# Docker
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

# Deploy
deploy:
	fly deploy --app dashboard-estoque-v2

logs:
	fly logs -a dashboard-estoque-v2

status:
	fly status -a dashboard-estoque-v2

# GitHub Actions
gh-setup:
	@echo "Obtendo token do Fly.io..."
	@fly auth token
	@echo "\nAgora vá em: https://github.com/SEU_USUARIO/dashboard-v2/settings/secrets/actions"
	@echo "E adicione os secrets: FLY_API_TOKEN e TINY_API_TOKEN"

gh-test-e2e:
	@echo "Executando testes E2E via GitHub Actions..."
	gh workflow run e2e-manual.yml -f test_scope=smoke

# Testes completos
test: backend-test

# Setup inicial
setup: backend-install frontend-install

# Desenvolvimento local
dev:
	@echo "Iniciando backend e frontend..."
	@make -j2 backend-dev frontend-dev

.PHONY: backend-dev backend-test backend-install frontend-dev frontend-build frontend-install docker-up docker-down docker-logs deploy logs status test setup dev