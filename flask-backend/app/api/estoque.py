from flask import Blueprint, jsonify, request
from ..services.tiny_api import tiny_client
from ..core.redis_client import redis_client
from ..models.estoque import ProdutoModel, EstoqueAjuste
import logging

logger = logging.getLogger(__name__)

estoque_bp = Blueprint('estoque', __name__)

@estoque_bp.route('/produto/<codigo>', methods=['GET'])
def obter_produto(codigo):
    """Busca produto por código"""
    try:
        # Primeiro tenta buscar no cache Redis
        cache_key = f"produto:codigo:{codigo}"
        cached = redis_client.get(cache_key)
        
        if cached:
            logger.info(f"Produto {codigo} encontrado no cache")
            return jsonify(cached)
        
        # Se não estiver no cache, busca no Tiny
        produto_data = tiny_client.buscar_produto_por_codigo(codigo)
        
        if not produto_data:
            return jsonify({'error': f'Produto {codigo} não encontrado'}), 404
        
        # Busca detalhes completos do produto
        produto_completo = tiny_client.obter_produto(produto_data['id'])
        
        if produto_completo:
            # Busca estoque
            estoque_data = tiny_client.obter_estoque(produto_data['id'])
            
            # Processa dados do estoque
            saldo_estoque = {}
            if estoque_data and 'depositos' in estoque_data:
                for deposito in estoque_data['depositos']:
                    dep = deposito.get('deposito', {})
                    nome_deposito = dep.get('nome', 'Desconhecido')
                    saldo = float(dep.get('saldo', 0))
                    saldo_estoque[nome_deposito] = saldo
                
                # Calcula total
                saldo_estoque['Total'] = sum(saldo_estoque.values())
            
            # Monta objeto produto
            produto = {
                'id': produto_completo.get('id'),
                'codigo': produto_completo.get('codigo'),
                'nome': produto_completo.get('nome'),
                'unidade': produto_completo.get('unidade', 'UN'),
                'preco': float(produto_completo.get('preco', 0)),
                'saldo_estoque': saldo_estoque
            }
            
            # Salva no cache por 5 minutos
            redis_client.set(cache_key, produto, ex=300)
            
            return jsonify(produto)
        
        return jsonify({'error': 'Erro ao obter detalhes do produto'}), 500
        
    except Exception as e:
        logger.error(f"Erro ao obter produto {codigo}: {e}")
        return jsonify({'error': str(e)}), 500

@estoque_bp.route('/ajustar', methods=['POST'])
def ajustar_estoque():
    """Ajusta estoque de um produto (adiciona ou remove)"""
    try:
        data = request.get_json()
        
        # Validações
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        produto_id = data.get('produto_id')
        quantidade = data.get('quantidade')
        tipo = data.get('tipo', 'E')  # E=Entrada, S=Saída
        observacoes = data.get('observacoes', '')
        
        if not produto_id:
            return jsonify({'error': 'produto_id é obrigatório'}), 400
        
        if quantidade is None:
            return jsonify({'error': 'quantidade é obrigatória'}), 400
        
        # Converte quantidade para inteiro
        try:
            quantidade = int(quantidade)
        except ValueError:
            return jsonify({'error': 'quantidade deve ser um número'}), 400
        
        # Valida tipo
        if tipo not in ['E', 'S']:
            return jsonify({'error': 'tipo deve ser "E" (entrada) ou "S" (saída)'}), 400
        
        # Faz o ajuste no Tiny
        resultado = tiny_client.alterar_estoque(
            produto_id=produto_id,
            quantidade=abs(quantidade),  # Tiny sempre espera valor positivo
            tipo=tipo,
            observacoes=observacoes
        )
        
        if resultado['success']:
            # Limpa cache do produto para forçar atualização
            # Precisamos descobrir o código do produto para limpar o cache correto
            produto = tiny_client.obter_produto(produto_id)
            if produto and produto.get('codigo'):
                cache_key = f"produto:codigo:{produto['codigo']}"
                redis_client.delete(cache_key)
                logger.info(f"Cache limpo para produto {produto['codigo']}")
            
            return jsonify({
                'success': True,
                'message': resultado['message'],
                'tipo': tipo,
                'quantidade': quantidade
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['message']
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao ajustar estoque: {e}")
        return jsonify({'error': str(e)}), 500

@estoque_bp.route('/ph510/adicionar', methods=['POST'])
def adicionar_estoque_ph510():
    """Adiciona 1 unidade ao estoque do PH-510"""
    try:
        # Busca o produto PH-510
        produto = tiny_client.buscar_produto_por_codigo('PH-510')
        
        if not produto:
            return jsonify({'error': 'Produto PH-510 não encontrado'}), 404
        
        # Adiciona 1 unidade
        resultado = tiny_client.alterar_estoque(
            produto_id=produto['id'],
            quantidade=1,
            tipo='E',
            observacoes='Entrada manual via Dashboard (+1)'
        )
        
        if resultado['success']:
            # Limpa cache
            redis_client.delete('produto:codigo:PH-510')
            
            # Busca estoque atualizado
            produto_atualizado = tiny_client.buscar_produto_por_codigo('PH-510')
            estoque_data = tiny_client.obter_estoque(produto['id'])
            
            saldo_total = 0
            if estoque_data and 'depositos' in estoque_data:
                for deposito in estoque_data['depositos']:
                    saldo_total += float(deposito.get('deposito', {}).get('saldo', 0))
            
            return jsonify({
                'success': True,
                'message': 'Estoque aumentado em 1 unidade',
                'produto': 'PH-510',
                'novo_saldo': saldo_total
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['message']
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao adicionar estoque PH-510: {e}")
        return jsonify({'error': str(e)}), 500

@estoque_bp.route('/ph510/remover', methods=['POST'])
def remover_estoque_ph510():
    """Remove 1 unidade do estoque do PH-510"""
    try:
        # Busca o produto PH-510
        produto = tiny_client.buscar_produto_por_codigo('PH-510')
        
        if not produto:
            return jsonify({'error': 'Produto PH-510 não encontrado'}), 404
        
        # Remove 1 unidade
        resultado = tiny_client.alterar_estoque(
            produto_id=produto['id'],
            quantidade=1,
            tipo='S',
            observacoes='Saída manual via Dashboard (-1)'
        )
        
        if resultado['success']:
            # Limpa cache
            redis_client.delete('produto:codigo:PH-510')
            
            # Busca estoque atualizado
            produto_atualizado = tiny_client.buscar_produto_por_codigo('PH-510')
            estoque_data = tiny_client.obter_estoque(produto['id'])
            
            saldo_total = 0
            if estoque_data and 'depositos' in estoque_data:
                for deposito in estoque_data['depositos']:
                    saldo_total += float(deposito.get('deposito', {}).get('saldo', 0))
            
            return jsonify({
                'success': True,
                'message': 'Estoque reduzido em 1 unidade',
                'produto': 'PH-510',
                'novo_saldo': saldo_total
            })
        else:
            return jsonify({
                'success': False,
                'error': resultado['message']
            }), 400
            
    except Exception as e:
        logger.error(f"Erro ao remover estoque PH-510: {e}")
        return jsonify({'error': str(e)}), 500