# Build stage para React
FROM node:18-alpine as frontend-build
WORKDIR /app
COPY react-frontend/package*.json ./
RUN npm install
COPY react-frontend/ ./
RUN npm run build

# Stage final com Flask
FROM python:3.11-slim
WORKDIR /app

# Instalar dependências do Flask
COPY flask-backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do Flask
COPY flask-backend/ .

# Copiar build do React para ser servido pelo Flask
COPY --from=frontend-build /app/build ./static

# Variáveis de ambiente
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]