#!/usr/bin/env python3
"""
Teste direto com a API do Tiny - Adicionar e remover 1 unidade do PH-510
"""
import asyncio
import sys
from pathlib import Path

# Adicionar o diretório backend ao path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.services.tiny_api import TinyAPIClient
from app.core.config import settings

async def main():
    """Teste direto de adicionar e remover estoque"""
    print("=== Teste Direto Tiny API - PH-510 ===\n")
    
    client = TinyAPIClient()
    
    try:
        # 1. Buscar produto
        print("1. Buscando produto PH-510...")
        produto = await client.buscar_produto_por_codigo("PH-510")
        
        if not produto:
            print("❌ Produto não encontrado!")
            return
            
        produto_id = produto['id']
        print(f"✅ Produto encontrado: {produto['nome']} (ID: {produto_id})")
        print(f"   Tipo do ID: {type(produto_id)} - Valor: '{produto_id}'")
        
        # 2. Obter saldo inicial
        estoque = await client.obter_estoque(produto_id)
        saldo_inicial = float(estoque.get('produto', {}).get('saldo', '0'))
        print(f"   Saldo inicial: {int(saldo_inicial)} unidades")
        
        # 3. Adicionar 1 unidade
        print("\n2. Adicionando 1 unidade...")
        resultado = await client.alterar_estoque(
            produto_id=produto_id,
            quantidade=1,
            tipo='E',
            observacoes='Teste Dashboard v2.0 - Adição de 1 unidade'
        )
        
        if resultado['success']:
            print(f"✅ {resultado['message']}")
            
            # Verificar novo saldo
            await asyncio.sleep(2)
            estoque = await client.obter_estoque(produto_id)
            saldo_apos_adicao = float(estoque.get('produto', {}).get('saldo', '0'))
            print(f"   Saldo após adição: {int(saldo_apos_adicao)} unidades")
        else:
            print(f"❌ {resultado['message']}")
            return
        
        # 4. Remover 1 unidade
        print("\n3. Removendo 1 unidade...")
        resultado = await client.alterar_estoque(
            produto_id=produto_id,
            quantidade=1,
            tipo='S',
            observacoes='Teste Dashboard v2.0 - Remoção de 1 unidade'
        )
        
        if resultado['success']:
            print(f"✅ {resultado['message']}")
            
            # Verificar saldo final
            await asyncio.sleep(2)
            estoque = await client.obter_estoque(produto_id)
            saldo_final = float(estoque.get('produto', {}).get('saldo', '0'))
            print(f"   Saldo final: {int(saldo_final)} unidades")
            
            print(f"\n📊 Resumo:")
            print(f"   - Saldo inicial: {int(saldo_inicial)}")
            print(f"   - Após adicionar 1: {int(saldo_apos_adicao)}")
            print(f"   - Após remover 1: {int(saldo_final)}")
            print(f"   - Variação total: {int(saldo_final - saldo_inicial)}")
        else:
            print(f"❌ {resultado['message']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.client.aclose()

if __name__ == "__main__":
    asyncio.run(main())