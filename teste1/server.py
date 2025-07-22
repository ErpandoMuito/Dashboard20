#!/usr/bin/env python3
"""
Servidor minimalista para Dashboard de Estoque
Serve tanto a API quanto os arquivos estáticos
"""

import uvicorn
from fastapi.staticfiles import StaticFiles
from main import app

# IMPORTANTE: Montar arquivos estáticos em /static ao invés de /
# para não conflitar com as rotas da API
app.mount("/static", StaticFiles(directory=".", html=True), name="static")

# Redirecionar raiz para index.html
from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)