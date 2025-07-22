#!/usr/bin/env python3
"""
Script para testar busca do produto PH-510 na API do Tiny
"""
import asyncio
import os
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append(str(Path(__file__).parent / "backend"))

# Importar após adicionar ao path
from app.services.tiny_api import TinyAPIClient
from app.core.config import settings

async def test_buscar_produto():
    """Testa busca do produto PH-510"""
    print("=== Teste de Busca do Produto PH-510 ===\n")
    
    # Verificar se temos o token configurado
    if not settings.TINY_API_TOKEN:
        print("❌ ERRO: Token da API Tiny não configurado!")
        print("Configure a variável TINY_API_TOKEN no arquivo .env")
        return
    
    print(f"✓ Token configurado: {settings.TINY_API_TOKEN[:10]}...")
    print(f"✓ URL Base: {settings.TINY_API_BASE_URL}\n")
    
    # Criar cliente
    client = TinyAPIClient()
    
    try:
        print("Buscando produto PH-510...")
        produto = await client.buscar_produto_por_codigo("PH-510")
        
        if produto:
            print(f"\n✅ Produto encontrado!")
            print(f"ID: {produto.get('id')}")
            print(f"Código: {produto.get('codigo')}")
            print(f"Nome: {produto.get('nome')}")
            print(f"Unidade: {produto.get('unidade')}")
            print(f"Preço: R$ {produto.get('preco', '0.00')}")
            
            # Buscar estoque
            print("\nBuscando informações de estoque...")
            estoque = await client.obter_estoque(produto['id'])
            if estoque:
                saldo = estoque.get('produto', {}).get('saldo', '0')
                print(f"✅ Saldo em estoque: {saldo} unidades")
            else:
                print("❌ Não foi possível obter informações de estoque")
                
        else:
            print("❌ Produto PH-510 não encontrado!")
            print("\nTentando buscar produtos com 'PH' no código...")
            
            # Tentar buscar apenas por 'PH'
            produtos_ph = await client.buscar_produto_por_codigo("PH")
            if produtos_ph:
                print(f"Encontrado produto com 'PH': {produtos_ph.get('nome')} (código: {produtos_ph.get('codigo')})")
    
    except Exception as e:
        print(f"❌ Erro ao buscar produto: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.client.aclose()

async def test_alterar_estoque():
    """Testa alteração de estoque (apenas se encontrar o produto)"""
    client = TinyAPIClient()
    
    try:
        # Primeiro buscar o produto
        produto = await client.buscar_produto_por_codigo("PH-510")
        if not produto:
            print("\n⚠️  Não é possível testar alteração de estoque sem encontrar o produto")
            return
            
        produto_id = produto['id']
        print(f"\n=== Teste de Alteração de Estoque ===")
        print(f"Produto: {produto['nome']} (ID: {produto_id})")
        
        # Teste de entrada
        print("\nTestando entrada de 1 unidade...")
        resultado = await client.alterar_estoque(
            produto_id=produto_id,
            quantidade=1,
            tipo='E',
            observacoes='Teste de entrada via script Python'
        )
        
        if resultado['success']:
            print(f"✅ {resultado['message']}")
        else:
            print(f"❌ {resultado['message']}")
            
    except Exception as e:
        print(f"❌ Erro ao alterar estoque: {e}")
    
    finally:
        await client.client.aclose()

async def main():
    """Função principal"""
    await test_buscar_produto()
    # await test_alterar_estoque()  # Descomentado apenas se quiser testar alteração

if __name__ == "__main__":
    asyncio.run(main())