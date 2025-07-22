from typing import Dict, Optional

class ProdutoModel:
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.codigo = data.get('codigo', '')
        self.nome = data.get('nome', '')
        self.unidade = data.get('unidade', 'UN')
        self.preco = float(data.get('preco', 0))
        self.saldo_estoque = data.get('saldo_estoque', {})
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nome': self.nome,
            'unidade': self.unidade,
            'preco': self.preco,
            'saldo_estoque': self.saldo_estoque
        }

class EstoqueAjuste:
    def __init__(self, produto_id: str, quantidade: int, tipo: str, observacoes: str = ''):
        self.produto_id = produto_id
        self.quantidade = quantidade
        self.tipo = tipo  # 'E' para entrada, 'S' para saída
        self.observacoes = observacoes