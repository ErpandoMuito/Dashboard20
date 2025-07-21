"""
Testes unitários para os modelos Pydantic
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.estoque import EntradaEstoqueRequest, EntradaEstoqueResponse, ProdutoInfo


class TestEntradaEstoqueRequest:
    """Testes para o modelo de requisição de entrada"""
    
    @pytest.mark.unit
    def test_criar_entrada_valida(self):
        """Deve criar entrada com dados válidos"""
        entrada = EntradaEstoqueRequest(
            codigo_produto="PH-510",
            quantidade=100,
            descricao="Teste",
            deposito="Geral"
        )
        
        assert entrada.codigo_produto == "PH-510"
        assert entrada.quantidade == 100
        assert entrada.tipo == "E"  # Default
        assert isinstance(entrada.data, datetime)
    
    @pytest.mark.unit
    def test_quantidade_deve_ser_positiva(self):
        """Não deve aceitar quantidade zero ou negativa"""
        with pytest.raises(ValidationError) as exc_info:
            EntradaEstoqueRequest(
                codigo_produto="PH-510",
                quantidade=0
            )
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('quantidade',) for error in errors)
    
    @pytest.mark.unit
    def test_codigo_produto_obrigatorio(self):
        """Código do produto é obrigatório"""
        with pytest.raises(ValidationError) as exc_info:
            EntradaEstoqueRequest(quantidade=100)
        
        errors = exc_info.value.errors()
        assert any(error['loc'] == ('codigo_produto',) for error in errors)
    
    @pytest.mark.unit
    def test_valores_default(self):
        """Deve usar valores default corretos"""
        entrada = EntradaEstoqueRequest(
            codigo_produto="PH-510",
            quantidade=50
        )
        
        assert entrada.deposito == "Geral"
        assert entrada.tipo == "E"
        assert entrada.descricao is None
        assert entrada.data.date() == datetime.now().date()


class TestEntradaEstoqueResponse:
    """Testes para o modelo de resposta"""
    
    @pytest.mark.unit
    def test_resposta_sucesso(self):
        """Deve criar resposta de sucesso"""
        response = EntradaEstoqueResponse(
            success=True,
            message="Entrada realizada",
            produto_id="123",
            saldo_atual=1500
        )
        
        assert response.success is True
        assert response.produto_id == "123"
        assert response.saldo_atual == 1500
    
    @pytest.mark.unit
    def test_resposta_erro(self):
        """Deve criar resposta de erro"""
        response = EntradaEstoqueResponse(
            success=False,
            message="Produto não encontrado"
        )
        
        assert response.success is False
        assert response.produto_id is None
        assert response.saldo_atual is None
        assert response.tiny_response is None


class TestProdutoInfo:
    """Testes para o modelo de informações do produto"""
    
    @pytest.mark.unit
    def test_criar_produto_info(self):
        """Deve criar informações do produto"""
        produto = ProdutoInfo(
            id="123",
            codigo="PH-510",
            nome="Arruela Trava",
            unidade="UN",
            saldo=1000
        )
        
        assert produto.id == "123"
        assert produto.codigo == "PH-510"
        assert produto.nome == "Arruela Trava"
        assert produto.unidade == "UN"
        assert produto.saldo == 1000
    
    @pytest.mark.unit
    def test_todos_campos_obrigatorios(self):
        """Todos os campos são obrigatórios"""
        with pytest.raises(ValidationError) as exc_info:
            ProdutoInfo(
                id="123",
                codigo="PH-510"
                # Faltando nome, unidade e saldo
            )
        
        errors = exc_info.value.errors()
        assert len(errors) == 3
        missing_fields = {error['loc'][0] for error in errors}
        assert missing_fields == {'nome', 'unidade', 'saldo'}