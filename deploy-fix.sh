#!/bin/bash

echo "Fazendo deploy do Dashboard Estoque v2.0 com correções..."

cd /Users/rodrigo/Documents/DashboardNovo/dashboard-v2

echo "Deploy iniciado..."
fly deploy

echo "Deploy concluído!"
echo "Acesse: https://dashboard-estoque-v2.fly.dev/estoque"