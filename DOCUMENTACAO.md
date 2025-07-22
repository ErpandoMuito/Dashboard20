# Documentação Técnica - DashboardNext v1.1.196

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Endpoints de API](#2-endpoints-de-api)
3. [Lógica de Semanas](#3-lógica-de-semanas)
4. [Estoque](#4-estoque)
5. [Integração com Tiny ERP](#5-integração-com-tiny-erp)
6. [Fluxos Críticos](#6-fluxos-críticos)
7. [Padrões de Código](#7-padrões-de-código)
8. [FAQ & Pitfalls](#8-faq--pitfalls)
9. [TODO & Gaps](#9-todo--gaps)

---

## 1. Visão Geral

DashboardNext é um sistema empresarial de dashboard integrado com o Tiny ERP, desenvolvido em Next.js 15 com TypeScript. O sistema gerencia notas fiscais, produtos, pedidos e fornece analytics em tempo real através de uma interface moderna e responsiva.

### Arquitetura de Alto Nível

```mermaid
graph TB
    subgraph "Fonte Externa"
        TINY[Tiny ERP API]
    end
    
    subgraph "Backend - Fly.io"
        WORKER[Worker de Sincronização<br/>7h-18h SP]
        REDIS[(Redis/Upstash<br/>Banco Principal)]
        API[API Routes<br/>Next.js]
    end
    
    subgraph "Frontend"
        UI[Interface React<br/>Next.js 15 + TypeScript]
        COMP[Componentes<br/>shadcn/ui + TanStack]
    end
    
    TINY -->|Polling 60s| WORKER
    WORKER -->|Salva dados| REDIS
    REDIS <-->|Consulta/Atualiza| API
    API <-->|JSON| UI
    UI --> COMP
    
    style TINY fill:#f9f,stroke:#333,stroke-width:2px
    style REDIS fill:#f96,stroke:#333,stroke-width:2px
    style WORKER fill:#9f9,stroke:#333,stroke-width:2px
```

### Stack Tecnológico

| Camada | Tecnologias |
|--------|-------------|
| **Frontend** | Next.js 15.3.4, React 19, TypeScript (strict), Tailwind CSS, shadcn/ui |
| **Tabelas** | TanStack Table v8 com ordenação e filtros |
| **Gráficos** | Recharts para visualizações |
| **Backend** | API Routes do Next.js com validação de tipos |
| **Banco** | Redis/Upstash com índices otimizados |
| **Deploy** | Fly.io (região GRU) - App + Worker |
| **Build** | Turbopack (dev), Standalone (prod) |

### Estrutura de Diretórios

```
/
├── app/                    # Next.js App Router
│   ├── api/               # API Routes (backend)
│   └── (páginas)          # Interfaces do sistema
├── components/            # Componentes React reutilizáveis
│   └── ui/               # shadcn/ui base components
├── lib/                   # Lógica de negócio e utilitários
├── worker/                # Worker de sincronização isolado
├── scripts/               # Scripts de manutenção
└── docs/                  # Documentação adicional
```

📝 **Revisar em futuras sprints**: Avaliar migração para monorepo com workspaces.

---

## 2. Endpoints de API

### 2.1 Notas Fiscais

#### GET `/api/notas`
Lista todas as notas fiscais com filtros e blacklist aplicados.

**Parâmetros Query:**
- `forceShow` (boolean): Ignora filtros quando true

**Resposta 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "123456789",
      "numero": "005182",
      "data_emissao": "19/06/2025",
      "cliente": { "nome": "VIBRACOUSTIC" },
      "valor": 1500.00,
      "itens": [
        {
          "item": {
            "codigo": "PH-511",
            "descricao": "PRODUTO EXEMPLO",
            "quantidade": "100",
            "valor_unitario": "15.00"
          }
        }
      ],
      "_apenasEmbalagem": false,
      "_processadoEm": 1737456789
    }
  ]
}
```

**Resposta 500:**
```json
{
  "success": false,
  "error": "Erro ao buscar notas"
}
```

#### POST `/api/notas/sync`
Sincroniza notas manualmente (executa worker uma vez).

**Body:**
```json
{
  "periodo": "hoje" | "3dias" | "7dias" | "15dias" | "30dias"
}
```

**Resposta 200:**
```json
{
  "success": true,
  "message": "Sincronização iniciada",
  "detalhes": {
    "notasNovas": 5,
    "notasAtualizadas": 0,
    "erros": []
  }
}
```

### 2.2 Pedidos

#### GET `/api/pedidos`
Lista todos os pedidos importados.

**Resposta 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "ped_123",
      "pedido_numero": "4530789012",
      "uploaded_at": "2025-07-21T10:00:00Z",
      "itens": [
        {
          "codigo": "PH-510",
          "entregas": [
            {
              "data": "25/07/2025",
              "quantidade": 100,
              "status": "Firm"
            }
          ]
        }
      ]
    }
  ]
}
```

#### POST `/api/pedidos/upload`
Processa e salva PDF de pedido.

**Body (multipart/form-data):**
- `file`: Arquivo PDF do pedido

**Processamento adicional:**
1. Extrai dados do PDF usando regex específicas
2. Identifica cliente pelo conteúdo do PDF
3. **Grava índice**: `pedido:numero:{numero}` → `pedido.id`
4. Adiciona ao set do cliente: `pedidos:cliente:vibracoustic`

**Resposta 200:**
```json
{
  "success": true,
  "message": "Pedido processado com sucesso",
  "pedido": {
    "id": "ped_123",
    "pedido_numero": "4530789012",
    "cliente_nome": "VIBRACOUSTIC",
    "ph_codes": ["PH-510", "PH-511"],
    "total_firm": 1500,
    "total_forecast": 3000
  }
}
```

#### GET `/api/pedidos/pdf/[id]`
Retorna o PDF do pedido para visualização.

**Parâmetros:**
- `id`: ID do pedido

**Resposta 200:** 
- Content-Type: `application/pdf`
- Body: Arquivo PDF binário

#### POST `/api/pedidos/snapshot`
Salva snapshot semanal dos pedidos.

**Body:**
```json
{
  "semana": "2025-W28"
}
```

**Resposta 200:**
```json
{
  "success": true,
  "message": "Snapshot salvo com sucesso",
  "stats": {
    "pedidosSalvos": 15,
    "semana": "2025-W28"
  }
}
```

### 2.3 Produtos

#### GET `/api/produtos`
Lista todos os produtos cadastrados.

**Resposta 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "prod_123",
      "codigo": "PH-510",
      "nome": "ARRUELA TRAVA",
      "preco": 125.00,
      "unidade": "UN",
      "saldo_estoque": {
        "Fundição": 1000,
        "Total": 1500
      }
    }
  ]
}
```

#### GET `/api/produtos/[codigo]/ultima-nota`
Retorna a nota fiscal mais recente do produto.

**Parâmetros:**
- `codigo`: Código do produto (ex: PH-510)

**Resposta 200:**
```json
{
  "success": true,
  "nota": {
    "numero": "005182",
    "data_emissao": "19/06/2025",
    "cliente": "VIBRACOUSTIC",
    "quantidade": "100"
  }
}
```

### 2.4 Requisições de Compra

#### GET `/api/requisicoes`
Lista requisições com filtros por status.

**Parâmetros Query:**
- `status`: criada | aprovada | negada | pedido_feito | entregue

**Resposta 200:**
```json
{
  "success": true,
  "data": [
    {
      "id": "req_123",
      "numero": 1,
      "created_at": "2025-07-21T10:00:00Z",
      "status": "aprovada",
      "solicitante": "João Silva",
      "itens": [
        {
          "produto": "PH-510",
          "quantidade": 100,
          "preco_unitario": 125.00
        }
      ],
      "valor_total": 12500.00
    }
  ]
}
```

#### POST `/api/requisicoes`
Cria nova requisição de compra.

**Body:**
```json
{
  "solicitante": "João Silva",
  "observacoes": "Urgente para produção",
  "itens": [
    {
      "produto": "PH-510",
      "quantidade": 100,
      "preco_unitario": 125.00,
      "observacao": "Confirmar prazo"
    }
  ]
}
```

### 2.5 Autenticação

#### POST `/api/auth/login`
Autentica usuário no sistema.

**Body:**
```json
{
  "username": "admin",
  "password": "senha123"
}
```

**Resposta 200:**
```json
{
  "success": true,
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

📝 **Revisar em futuras sprints**: Implementar JWT com refresh tokens.

---

## 3. Lógica de Semanas

### 3.1 Conceito das "Sextas-Feiras Diferenciadas"

O sistema agrupa todas as entregas pela **sexta-feira da semana ISO correspondente**. Isso significa que qualquer entrega marcada para qualquer dia da semana será visualizada como se fosse na sexta-feira daquela semana.

### 3.2 Algoritmo Principal

```mermaid
flowchart TD
    A[Data de Entrega] --> B{É sexta-feira?}
    B -->|Sim| C[Mantém a data]
    B -->|Não| D[Calcula semana ISO]
    D --> E[Encontra sexta-feira<br/>da semana ISO]
    E --> F[Data ajustada]
    C --> G[Aplica cor da semana]
    F --> G
    G --> H{Data < Hoje?}
    H -->|Sim| I[Backlog<br/>Cor: Vermelho]
    H -->|Não| J{Dentro de 30 dias?}
    J -->|Sim| K[Firm<br/>Cor da semana]
    J -->|Não| L[Forecast<br/>Cor: Âmbar]
```

### 3.3 Função Principal

```typescript
// lib/semanas-por-sexta.ts
export function getProximaSexta(data: Date): Date {
  const diaSemana = data.getDay()
  const diasAteSexta = (5 - diaSemana + 7) % 7
  
  const sexta = new Date(data)
  sexta.setDate(data.getDate() + diasAteSexta)
  
  return sexta
}

// lib/month-weeks.ts
export function getSemanaDaData(data: Date): number {
  const primeiroDia = startOfMonth(data)
  const semanaISO = getISOWeek(data)
  const semanaPrimeiroDia = getISOWeek(primeiroDia)
  
  return semanaISO - semanaPrimeiroDia + 1
}
```

### 3.4 Exemplos Práticos

#### Exemplo 1: Julho 2025
```
Entrega original: Quarta, 23/07/2025
Semana ISO: 30 (21/07 a 27/07)
Sexta da semana: 25/07/2025
Semana do mês: 4
Cor aplicada: Amarelo
```

#### Exemplo 2: Caso especial - Final de mês
```
Entrega original: Quarta, 30/07/2025
Semana ISO: 31 (28/07 a 03/08)
Sexta da semana: 01/08/2025 ⚠️
Problema: Entrega de julho agrupada em agosto
Status atual: BUG identificado, aguardando correção
```

### 3.5 Sistema de Cores

| Semana | Cor | Hex |
|--------|-----|-----|
| Semana 1 | Azul | #3B82F6 |
| Semana 2 | Roxo | #8B5CF6 |
| Semana 3 | Verde | #10B981 |
| Semana 4 | Amarelo | #F59E0B |
| Semana 5 | Laranja | #F97316 |
| Backlog | Vermelho | #EF4444 |
| Forecast | Âmbar | #D97706 |

### 3.6 Comportamento em Viradas de Ano ISO

O sistema utiliza semanas ISO (ISO 8601), onde:
- A semana 1 do ano é a primeira semana que contém uma quinta-feira
- Semanas vão de segunda a domingo
- Pode haver semana 52 ou 53 no final do ano

**Exemplo de virada de ano:**
```
Data: 30/12/2025 (terça-feira)
Semana ISO: 01/2026 (pois 01/01/2026 é quinta)
Sexta ajustada: 02/01/2026
Implicação: Entrega de dezembro aparece em janeiro
```

### 3.7 Timezone e Horário de Verão

**Timezone fixo**: `America/Sao_Paulo`

```typescript
// O sistema sempre usa horário de São Paulo
const agora = new Date()
const horaLocal = agora.toLocaleString('pt-BR', { 
  timeZone: 'America/Sao_Paulo' 
})

// Horário de verão: Ignorado nos cálculos de semana
// As funções date-fns trabalham com datas UTC internamente
// Apenas a exibição considera o timezone
```

**Nota**: Brasil não tem mais horário de verão desde 2019, mas o código está preparado caso retorne.

### 3.8 Tabela de Datas Problemáticas para Testes

| Data Original | Contexto | Semana ISO | Sexta Ajustada | Observação |
|---------------|----------|------------|----------------|------------|
| 30/12/2025 (ter) | Fim de ano | 2026-W01 | 02/01/2026 | Cruza anos |
| 31/12/2025 (qua) | Último dia | 2026-W01 | 02/01/2026 | Cruza anos |
| 01/01/2026 (qui) | Ano novo | 2026-W01 | 02/01/2026 | Quinta→Sexta |
| 28/02/2026 (sáb) | Fim fevereiro | 2026-W09 | 27/02/2026 | Sábado→Sexta anterior |
| 01/03/2026 (dom) | Início março | 2026-W09 | 27/02/2026 | Domingo→Sexta anterior |
| 17/02/2026 (ter) | Carnaval | 2026-W08 | 20/02/2026 | Feriado móvel |
| 10/04/2026 (sex) | Sexta Santa | 2026-W15 | 10/04/2026 | Já é sexta |
| 29/06/2026 (seg) | Meio do ano | 2026-W27 | 03/07/2026 | Cruza meses |
| 07/09/2026 (seg) | Independência | 2026-W37 | 11/09/2026 | Feriado nacional |
| 25/12/2026 (sex) | Natal | 2026-W52 | 25/12/2026 | Já é sexta |

📝 **Revisar em futuras sprints**: Corrigir agrupamento de final de mês.

---

## 4. Estoque

### 4.1 Visão Geral

O sistema **não gerencia estoque operacionalmente**. Ele apenas:
- **Sincroniza** dados do Tiny ERP
- **Visualiza** saldos atuais
- **Calcula** necessidades baseadas em pedidos
- **Aplica abatimento visual** de notas em pedidos

### 4.2 Estrutura de Dados de Estoque

```typescript
interface ProdutoEstoque {
  codigo: string
  nome: string
  saldo_estoque: {
    [deposito: string]: number  // Ex: "Fundição": 1000
    Total: number               // Soma de todos depósitos
  }
  preco: number
  unidade: string
}
```

### 4.3 Sistema de Abatimento

O abatimento é um **cálculo visual** que mostra quanto dos pedidos já foi atendido por notas fiscais.

```typescript
// lib/abatimento.ts
export function calcularAbatimento(
  pedidos: Pedido[],
  notas: NotaFiscal[]
): Map<string, AbatimentoInfo> {
  const abatimentos = new Map()
  
  // Para cada produto nas notas
  for (const nota of notas) {
    for (const item of nota.itens) {
      const codigo = item.codigo
      const quantidade = Number(item.quantidade)
      
      // Encontra pedidos do mesmo produto
      const pedidosDoProduto = pedidos.filter(p => 
        p.itens.some(i => i.codigo === codigo)
      )
      
      // Abate dos pedidos mais antigos primeiro (FIFO)
      let qtdRestante = quantidade
      for (const pedido of pedidosDoProduto.sort(byData)) {
        if (qtdRestante <= 0) break
        
        // Abate quantidade do pedido
        const abatido = Math.min(qtdRestante, pedido.quantidade)
        qtdRestante -= abatido
        
        // Registra abatimento
        abatimentos.set(pedido.id, {
          quantidade: abatido,
          notaNumero: nota.numero,
          data: nota.data_emissao
        })
      }
    }
  }
  
  return abatimentos
}
```

### 4.4 Cálculo de Necessidades

```typescript
// Fórmula: Necessidade = Backlog + Demanda_Futura - Estoque_Atual
const necessidade = Math.max(0, 
  backlogTotal + demandaProximas4Semanas - estoqueAtual
)
```

### 4.5 Sincronização com Tiny

#### Endpoint de Estoque
```typescript
// POST para /produto.obter.estoque.php
const payload = {
  token: TINY_API_TOKEN,
  formato: 'JSON',
  id: produtoId
}

// Resposta
{
  "retorno": {
    "status": "OK",
    "depositos": [
      {
        "deposito": {
          "nome": "Fundição",
          "saldo": "1000.00",
          "empresa": "Matriz"
        }
      }
    ]
  }
}
```

### 4.6 Validações e Regras

1. **Estoque nunca negativo**: Interface mostra 0 se cálculo resultar negativo
2. **Depósito prioritário**: "Fundição" destacado quando disponível
3. **Unidades**: Sempre respeita unidade do Tiny (UN, PC, KG, etc)
4. **Atualização**: Worker sincroniza a cada 60 segundos

### 4.7 Convenção de Chaves no Redis

**Estrutura de chaves para dados principais:**

| Padrão de Chave | Descrição | Exemplo | TTL |
|-----------------|-----------|---------|-----|
| `nota:{id}` | Dados completos da nota fiscal | `nota:123456789` | Não |
| `nota:numero:{numero}` | Índice número → ID | `nota:numero:005182` | Não |
| `notas:all` | Set com todos IDs de notas | `notas:all` | Não |
| `notas:produto:{codigo}` | Sorted set de notas por produto | `notas:produto:PH-510` | Não |
| `produto:{id}` | **OBSOLETO** - não usar | `produto:123` | - |
| `produto:codigo:{codigo}` | Dados do produto por código | `produto:codigo:PH-510` | Não |
| `produto:imagem:{codigo}` | Cache de imagem base64 | `produto:imagem:PH-510` | Não |
| `pedido:{id}` | Dados do pedido importado | `pedido:ped_123` | Não |
| `pedido:pdf:{id}` | PDF em base64 | `pedido:pdf:ped_123` | Não |
| `pedidos:all` | Set com todos IDs de pedidos | `pedidos:all` | Não |
| `pedidos:snapshot:{semana}:{id}` | Snapshot histórico | `pedidos:snapshot:2025-W28:ped_123` | Não |
| `pedidos:snapshots:semanas` | Set de semanas com snapshots | `pedidos:snapshots:semanas` | Não |
| `requisicao:{id}` | Dados de requisição | `requisicao:req_123` | Não |
| `img:req:{id}:{tipo}` | Imagem de requisição | `img:req:req_123:produto` | 90 dias |
| `requisicoes:produto:{produto}` | Índice por produto | `requisicoes:produto:PH-510` | Não |
| `config:blacklist` | Lista de empresas bloqueadas | `config:blacklist` | Não |
| `worker:ultima_execucao` | Metadata do worker | `worker:ultima_execucao` | Não |

**Convenções importantes:**
- IDs sempre prefixados com tipo (`ped_`, `req_`, etc)
- Códigos de produto sempre em maiúsculas
- Datas no formato ISO para ordenação
- Índices usam sorted sets com timestamp como score

### 4.8 Tratamento de Discrepâncias de Estoque

Quando `saldo_estoque.Total` não corresponde à soma dos depósitos:

```typescript
// lib/estoque-utils.ts
function validarEstoque(produto: Produto) {
  const somaDepositos = Object.entries(produto.saldo_estoque)
    .filter(([key]) => key !== 'Total')
    .reduce((sum, [_, valor]) => sum + valor, 0)
  
  if (Math.abs(somaDepositos - produto.saldo_estoque.Total) > 0.01) {
    console.warn(`⚠️ Discrepância de estoque em ${produto.codigo}:`, {
      somaDepositos,
      totalDeclarado: produto.saldo_estoque.Total,
      diferenca: somaDepositos - produto.saldo_estoque.Total
    })
    
    // Sistema mantém o Total do Tiny como fonte de verdade
    // Apenas loga o aviso para investigação
  }
}
```

**Política**: O sistema **sempre confia no campo Total** retornado pelo Tiny, apenas logando avisos quando há discrepâncias.

📝 **Revisar em futuras sprints**: Implementar histórico de movimentações.

---

## 5. Integração com Tiny ERP

### 5.1 Configuração e Autenticação

| Parâmetro | Valor |
|-----------|-------|
| **Base URL** | `https://api.tiny.com.br/api2` |
| **Token** | `fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb` |
| **Formato** | `JSON` |
| **Encoding** | `application/x-www-form-urlencoded` |
| **Env Var** | `TINY_API_TOKEN` |

### 5.2 Endpoints Consumidos

#### 5.2.1 Buscar Produtos
```http
POST /produtos.pesquisa.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&pesquisa=PH-510
```

**Schema de Resposta Completo:**
```json
{
  "retorno": {
    "status": "OK" | "Erro",
    "erros": [{
      "erro": "string"  // Mensagem de erro
    }],
    "produtos": [{
      "produto": {
        "id": "string",                    // ID interno do Tiny
        "codigo": "string",                // Código do produto (SKU)
        "nome": "string",                  // Nome/descrição
        "unidade": "string",               // UN, PC, KG, etc
        "preco": "string",                 // Preço de venda
        "preco_custo": "string?",          // Preço de custo
        "preco_custo_medio": "string?",    // Custo médio
        "situacao": "A" | "I" | "E",       // Ativo, Inativo, Excluído
        "tipo": "P" | "S",                 // Produto ou Serviço
        "class_fiscal": "string?",         // NCM
        "marca": "string?",                // Marca
        "gtin_ean": "string?",             // Código de barras
        "localizacao": "string?",          // Local no estoque
        "peso_liquido": "string?",         // Peso em KG
        "peso_bruto": "string?",           // Peso com embalagem
        "estoque_minimo": "string?",       // Quantidade mínima
        "estoque_maximo": "string?",       // Quantidade máxima
        "anexos": [{                       // Imagens/documentos
          "anexo": "string"                // URL do anexo
        }]
      }
    }]
  }
}
```

#### 5.2.2 Obter Detalhes do Produto
```http
POST /produto.obter.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&id=123456
```

**Schema de Resposta:** Mesmo schema de 5.2.1, mas com apenas um produto.

#### 5.2.3 Buscar Notas Fiscais
```http
POST /notas.fiscais.pesquisa.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&dataInicial=01/07/2025&dataFinal=21/07/2025&situacao=6,7&tipoNota=S
```

**Parâmetros:**
- `situacao`: 6 (Autorizada), 7 (Emitida)
- `tipoNota`: S (Saída), E (Entrada)
- `cliente`: Nome do cliente (opcional)
- `numero_ecommerce`: Número do pedido (opcional)

**Schema de Resposta:**
```json
{
  "retorno": {
    "status": "OK" | "Erro",
    "notas_fiscais": [{
      "nota_fiscal": {
        "id": "string",
        "tipo_nota": "S" | "E",
        "natureza_operacao": "string",
        "numero": "string",
        "serie": "string",
        "situacao": "6" | "7" | "8" | "9",  // 6=Autorizada, 7=Emitida, 8=Cancelada, 9=Denegada
        "cliente": {
          "nome": "string",
          "tipoPessoa": "F" | "J",           // Física ou Jurídica
          "cpf_cnpj": "string",
          "ie": "string?",                   // Inscrição Estadual
          "endereco": "string?",
          "numero": "string?",
          "complemento": "string?",
          "bairro": "string?",
          "cidade": "string?",
          "uf": "string?"
        },
        "data_emissao": "string",            // DD/MM/YYYY
        "valor": "string",
        "valor_produtos": "string?",
        "valor_desconto": "string?",
        "valor_frete": "string?"
      }
    }]
  }
}
```

#### 5.2.4 Obter Nota Completa
```http
POST /nota.fiscal.obter.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&id=789012
```

**Schema de Resposta Completo:**
```json
{
  "retorno": {
    "status": "OK" | "Erro",
    "nota_fiscal": {
      "id": "string",
      "tipo_nota": "S" | "E",
      "numero": "string",
      "serie": "string",
      "data_emissao": "string",              // DD/MM/YYYY
      "data_saida": "string?",               // DD/MM/YYYY
      "hora_saida": "string?",               // HH:MM:SS
      "situacao": "6" | "7" | "8" | "9",
      "chave_acesso": "string?",             // 44 dígitos
      "protocolo": "string?",
      "motivo_cancelamento": "string?",
      "natureza_operacao": "string",
      "regime_tributario": "1" | "2" | "3",  // 1=Simples, 2=Simples Excesso, 3=Normal
      "finalidade": "1" | "2" | "3" | "4",   // 1=Normal, 2=Complementar, 3=Ajuste, 4=Devolução
      "presenca": "0" | "1" | "2" | "3" | "4" | "5" | "9",
      "cliente": {
        "codigo": "string?",
        "nome": "string",
        "tipoPessoa": "F" | "J",
        "cpf_cnpj": "string",
        "ie": "string?",
        "rg": "string?",
        "contribuinte": "1" | "2" | "9",     // 1=ICMS, 2=Isento, 9=Não contribuinte
        "endereco": "string",
        "numero": "string",
        "complemento": "string?",
        "bairro": "string",
        "cep": "string",
        "cidade": "string",
        "uf": "string",
        "pais": "string?",
        "fone": "string?",
        "email": "string?"
      },
      "vendedor": {
        "codigo": "string?",
        "nome": "string?"
      },
      "transporte": {
        "transportadora": "string?",
        "cpf_cnpj": "string?",
        "ie": "string?",
        "endereco": "string?",
        "cidade": "string?",
        "uf": "string?",
        "placa": "string?",
        "uf_veiculo": "string?",
        "marca": "string?",
        "tipo_frete": "E" | "D" | "0" | "1" | "2" | "3" | "4" | "9",
        "qtde_volumes": "string?",
        "especie": "string?",
        "numero_volumes": "string?",
        "peso_bruto": "string?",
        "peso_liquido": "string?"
      },
      "itens": [{
        "item": {
          "codigo": "string",
          "descricao": "string",
          "unidade": "string",
          "ncm": "string?",
          "quantidade": "string",
          "valor_unitario": "string",
          "valor_total": "string",
          "valor_desconto": "string?",
          "valor_frete": "string?",
          "valor_seguro": "string?",
          "valor_outras_despesas": "string?",
          "tipo": "P" | "S",                  // Produto ou Serviço
          "origem": "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8",
          "informacoes_adicionais": "string?",
          "numero_pedido_compra": "string?",
          "numero_item_pedido_compra": "string?",
          "cfop": "string",
          "cst": "string?",
          "csosn": "string?",
          "percentual_reducao": "string?",
          "valor_base_icms": "string?",
          "aliquota_icms": "string?",
          "aliquota_icms_st": "string?",
          "valor_icms": "string?",
          "valor_icms_st": "string?",
          "valor_base_icms_st": "string?",
          "cst_pis": "string?",
          "aliquota_pis": "string?",
          "valor_pis": "string?",
          "cst_cofins": "string?",
          "aliquota_cofins": "string?",
          "valor_cofins": "string?",
          "cst_ipi": "string?",
          "aliquota_ipi": "string?",
          "valor_ipi": "string?",
          "classe_enquadramento_ipi": "string?",
          "codigo_enquadramento_ipi": "string?",
          "cnpj_produtor": "string?"
        }
      }],
      "duplicatas": [{
        "duplicata": {
          "numero": "string",
          "data_vencimento": "string",        // DD/MM/YYYY
          "valor": "string",
          "obs": "string?",
          "forma_pagamento": "string?"
        }
      }],
      "parcelas": [{
        "parcela": {
          "dias": "string",
          "data": "string",                   // DD/MM/YYYY
          "valor": "string",
          "obs": "string?",
          "forma_pagamento": "string?"
        }
      }],
      "formas_pagamento": [{
        "forma_pagamento": {
          "forma": "string",
          "valor": "string"
        }
      }],
      "totais": {
        "base_icms": "string",
        "valor_icms": "string",
        "valor_icms_desonerado": "string?",
        "base_icms_st": "string",
        "valor_icms_st": "string",
        "valor_produtos": "string",
        "valor_frete": "string",
        "valor_seguro": "string",
        "valor_desconto": "string",
        "valor_ipi": "string",
        "valor_ipi_devolvido": "string?",
        "valor_pis": "string",
        "valor_cofins": "string",
        "valor_outras_despesas": "string",
        "valor_nota": "string",
        "valor_aproximado_tributos": "string?"
      },
      "informacoes_adicionais": "string?",
      "informacoes_fisco": "string?",
      "obs_internas": "string?",
      "obs_cliente": "string?"
    }
  }
}
```

#### 5.2.5 Obter Estoque do Produto
```http
POST /produto.obter.estoque.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&id=123456
```

**Schema de Resposta:**
```json
{
  "retorno": {
    "status": "OK" | "Erro",
    "produto": {
      "id": "string",
      "codigo": "string",
      "nome": "string",
      "unidade": "string",
      "saldo": "string",                     // Saldo total
      "saldoReservado": "string?"            // Quantidade reservada
    },
    "depositos": [{
      "deposito": {
        "id": "string",
        "nome": "string",
        "desconsiderar": "S" | "N",          // Se deve considerar no total
        "saldo": "string",
        "empresa": "string",                  // Nome da empresa/filial
        "saldoVirtual": "string?"             // Saldo incluindo pedidos
      }
    }]
  }
}
```

### 5.3 Mapeamento de Campos Tiny → Modelo Interno

| Campo Tiny | Campo Interno | Observações |
|------------|---------------|-------------|
| `produto.codigo` | `codigo` | Mantém formato original |
| `produto.nome` | `nome` | String sem tratamento |
| `produto.preco` | `preco` | String → Number no frontend |
| `produto.unidade` | `unidade` | UN, PC, KG, etc |
| `deposito.nome` | `saldo_estoque[nome]` | Chave do objeto |
| `deposito.saldo` | `saldo_estoque[nome]` | String → Number |
| `nota_fiscal.numero` | `numero` | String com zeros à esquerda |
| `nota_fiscal.data_emissao` | `data_emissao` | DD/MM/YYYY mantido |
| `nota_fiscal.cliente.nome` | `cliente.nome` | Normalizado por função |
| `item.codigo` | `item.codigo` | Aplicado mapeamento SKU |
| `item.quantidade` | `item.quantidade` | String → Number para cálculos |
| `item.valor_unitario` | `item.valor_unitario` | String → Number |

### 5.4 Códigos de Erro e Tratamento

| Código/Mensagem | Significado | Tratamento Recomendado |
|-----------------|-------------|------------------------|
| "não retornou registros" | Busca vazia | Retornar array vazio, não é erro |
| "API Bloqueada temporariamente" | Rate limit | Aguardar 60s e tentar novamente |
| "Token inválido" | Auth falhou | Verificar token no .env |
| "Excedido o limite de requisições" | Limite diário | Aguardar próximo dia |
| "Erro na comunicação" | Timeout/rede | Retry com backoff exponencial |
| "Produto não encontrado" | ID inválido | Logar e pular produto |
| "Parâmetro obrigatório" | Faltou campo | Validar antes de enviar |
| Status 302 | Token expirado | Renovar token (manual) |
| Status 500 | Erro interno | Retry após 5 segundos |

### 5.5 Como Obter/Renovar Token

**1. Acessar o Painel do Tiny:**
```bash
# URL do painel
https://erp.tiny.com.br/

# Fazer login com suas credenciais
```

**2. Gerar Token de API:**
- Menu: Configurações → API
- Clicar em "Gerar Token"
- Copiar o token gerado (40 caracteres hexadecimais)

**3. Testar Token via CURL:**
```bash
# Teste básico - deve retornar seus dados da conta
curl -X POST https://api.tiny.com.br/api2/info.php \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=SEU_TOKEN_AQUI&formato=JSON"

# Resposta esperada:
{
  "retorno": {
    "status": "OK",
    "conta": {
      "nome": "Sua Empresa",
      "fantasia": "Nome Fantasia",
      "cnpj": "00.000.000/0001-00"
    }
  }
}
```

**4. Configurar no Sistema:**
```bash
# Arquivo .env na raiz do projeto
TINY_API_TOKEN=fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb

# Ou via Fly.io secrets
fly secrets set TINY_API_TOKEN=SEU_TOKEN_AQUI
```

### 5.6 Rate Limiting e Retry

```typescript
// lib/tiny-api.ts
const MAX_TENTATIVAS = 3
const DELAY_API_BLOQUEADA = 60000  // 60 segundos
const DELAY_ENTRE_TENTATIVAS = 5000 // 5 segundos

async function executarComRetry(fn: Function) {
  for (let tentativa = 1; tentativa <= MAX_TENTATIVAS; tentativa++) {
    try {
      return await fn()
    } catch (erro) {
      if (erro.message.includes('API Bloqueada')) {
        console.log('⚠️ API bloqueada, aguardando 60s...')
        await sleep(DELAY_API_BLOQUEADA)
      } else if (tentativa < MAX_TENTATIVAS) {
        await sleep(DELAY_ENTRE_TENTATIVAS * tentativa)
      } else {
        throw erro
      }
    }
  }
}
```

### 5.7 Peculiaridades da API Tiny

1. **Formato de Data**: Sempre `DD/MM/YYYY`
2. **Encoding especial**: Caracteres acentuados podem vir com problemas
3. **Paginação**: Não documentada, assume-se retorno completo
4. **Campos vazios**: Podem vir como string vazia `""` ao invés de `null`
5. **Estrutura de itens**: Pode vir como `itens[].item` ou `item` direto
6. **Limites diários**: ~10.000 requisições/dia (não oficial)

### 5.8 Worker de Sincronização

```typescript
// worker/notas-worker.ts
const CONFIG = {
  HORARIO_INICIO: 7,      // 7h São Paulo
  HORARIO_FIM: 18,        // 18h São Paulo
  INTERVALO_NORMAL: 60,   // 60 segundos
  INTERVALO_PICO: 30,     // 30 segundos (13h-15h)
  DIAS_RETROATIVOS: 3,    // Busca últimos 3 dias úteis
}

// Clientes prioritários (sincronizados primeiro)
const CLIENTES_PRIORITARIOS = [
  'ELECTROLUX DO BRASIL S/A',
  'VIBRACOUSTIC SOUTH AMERICA LTDA',
  'UNICOBA AMAZONIA INDUSTRIA DE COMPONENTES',
  'HBA HUTCHINSON BRAZIL AUTOMOTIVE LTDA',
  'ANAUGER SA',
  'BASF SA'
]
```

### 5.9 Exemplos de Payloads Completos

#### Payload Real de Nota Fiscal Detalhada
```json
{
  "retorno": {
    "status": "OK",
    "nota_fiscal": {
      "id": "751290583",
      "tipo_nota": "S",
      "numero": "005182",
      "serie": "1",
      "data_emissao": "19/06/2025",
      "data_saida": "19/06/2025",
      "hora_saida": "14:30:00",
      "situacao": "6",
      "chave_acesso": "35250612345678000190550010000051821123456789",
      "protocolo": "135250000123456",
      "natureza_operacao": "VENDA DE MERCADORIA",
      "regime_tributario": "1",
      "finalidade": "1",
      "presenca": "9",
      "cliente": {
        "codigo": "12345",
        "nome": "VIBRACOUSTIC SOUTH AMERICA LTDA",
        "tipoPessoa": "J",
        "cpf_cnpj": "01.234.567/0001-89",
        "ie": "123.456.789.012",
        "contribuinte": "1",
        "endereco": "RUA EXEMPLO INDUSTRIAL",
        "numero": "1000",
        "complemento": "GALPAO 5",
        "bairro": "DISTRITO INDUSTRIAL",
        "cep": "12345-678",
        "cidade": "SAO BERNARDO DO CAMPO",
        "uf": "SP",
        "pais": "Brasil",
        "fone": "(11) 1234-5678",
        "email": "nfe@vibracoustic.com"
      },
      "vendedor": {
        "codigo": "001",
        "nome": "VENDEDOR INTERNO"
      },
      "transporte": {
        "transportadora": "TRANSPORTADORA EXEMPLO LTDA",
        "cpf_cnpj": "98.765.432/0001-10",
        "ie": "987.654.321.098",
        "endereco": "RUA DOS TRANSPORTES, 500",
        "cidade": "SAO PAULO",
        "uf": "SP",
        "placa": "ABC-1234",
        "uf_veiculo": "SP",
        "tipo_frete": "1",
        "qtde_volumes": "10",
        "especie": "CAIXA",
        "peso_bruto": "150.000",
        "peso_liquido": "145.000"
      },
      "itens": [
        {
          "item": {
            "codigo": "PH-510",
            "descricao": "ARRUELA TRAVA EIXO DIANTEIRO",
            "unidade": "UN",
            "ncm": "73182300",
            "quantidade": "1000.0000",
            "valor_unitario": "1.2500",
            "valor_total": "1250.00",
            "tipo": "P",
            "origem": "0",
            "cfop": "5102",
            "csosn": "102",
            "valor_base_icms": "0.00",
            "aliquota_icms": "0.00",
            "valor_icms": "0.00",
            "cst_pis": "49",
            "aliquota_pis": "0.00",
            "valor_pis": "0.00",
            "cst_cofins": "49",
            "aliquota_cofins": "0.00",
            "valor_cofins": "0.00",
            "numero_pedido_compra": "4530123456",
            "numero_item_pedido_compra": "10"
          }
        },
        {
          "item": {
            "codigo": "PH-511",
            "descricao": "PARAFUSO CABECA SEXTAVADA M10X1.5X30",
            "unidade": "UN",
            "ncm": "73181500",
            "quantidade": "500.0000",
            "valor_unitario": "0.8500",
            "valor_total": "425.00",
            "tipo": "P",
            "origem": "0",
            "cfop": "5102",
            "csosn": "102",
            "numero_pedido_compra": "4530123456",
            "numero_item_pedido_compra": "20"
          }
        }
      ],
      "duplicatas": [
        {
          "duplicata": {
            "numero": "005182/1",
            "data_vencimento": "19/07/2025",
            "valor": "1675.00",
            "forma_pagamento": "BOLETO"
          }
        }
      ],
      "totais": {
        "base_icms": "0.00",
        "valor_icms": "0.00",
        "base_icms_st": "0.00",
        "valor_icms_st": "0.00",
        "valor_produtos": "1675.00",
        "valor_frete": "0.00",
        "valor_seguro": "0.00",
        "valor_desconto": "0.00",
        "valor_ipi": "0.00",
        "valor_pis": "0.00",
        "valor_cofins": "0.00",
        "valor_outras_despesas": "0.00",
        "valor_nota": "1675.00",
        "valor_aproximado_tributos": "251.25"
      },
      "informacoes_adicionais": "DOCUMENTO EMITIDO POR ME OU EPP OPTANTE PELO SIMPLES NACIONAL",
      "obs_internas": "PEDIDO VIBRA: 4530123456"
    }
  }
}
```

#### Criar/Atualizar Estoque (não implementado)
```http
POST /produto.alterar.estoque.php
Content-Type: application/x-www-form-urlencoded

token=TOKEN&formato=JSON&id=123456&tipo=E&deposito=1&quantidade=100&observacoes=Entrada+NF+005182
```

**Nota**: Sistema atual é **read-only** para estoque.

📝 **Revisar em futuras sprints**: Implementar atualização de estoque via Tiny.

---

## 6. Fluxos Críticos

### 6.1 Entrada de Mercadoria → Atualização de Estoque

```mermaid
sequenceDiagram
    participant NF as Nota Fiscal<br/>(Tiny)
    participant W as Worker
    participant R as Redis
    participant API as API Routes
    participant UI as Interface

    Note over NF: Nota emitida no Tiny
    W->>NF: Busca notas (polling 60s)
    NF-->>W: Lista de notas
    W->>NF: Busca detalhes de cada nota
    NF-->>W: Nota completa
    W->>W: Valida blacklist
    W->>W: Aplica filtro embalagens
    W->>R: Salva nota + índices
    W->>R: Atualiza produtos referenciados
    UI->>API: GET /api/notas
    API->>R: Busca notas
    R-->>API: Dados das notas
    API-->>UI: JSON formatado
    UI->>UI: Exibe com abatimento
```

### 6.2 Upload de Pedido → Cálculo de Backlog

```mermaid
sequenceDiagram
    participant U as Usuário
    participant UI as Interface
    participant API as API Upload
    participant PDF as Parser PDF
    participant R as Redis
    participant C as Calendário

    U->>UI: Arrasta PDF
    UI->>API: POST /api/pedidos/upload
    API->>PDF: Processa PDF
    PDF-->>API: Dados extraídos
    API->>API: Ajusta datas p/ sextas
    API->>R: Salva pedido + PDF
    API-->>UI: Sucesso
    UI->>C: Atualiza calendário
    C->>C: Calcula backlogs
    C->>C: Aplica cores
```

### 6.3 Sistema de Abatimento Automático

1. **Busca notas fiscais** do produto
2. **Ordena pedidos** por data (FIFO)
3. **Para cada nota**:
   - Deduz quantidade dos pedidos
   - Mais antigos primeiro
   - Registra referências
4. **Exibe badges** com quantidade abatida
5. **Popover** mostra detalhes das notas

### 6.4 Geração de Snapshots Históricos

1. **Trigger**: Manual ou agendado (sextas-feiras)
2. **Coleta**: Todos os pedidos ativos
3. **Formato**: `pedidos:snapshot:{semana}:{pedido_id}`
4. **Comparação**: Automática com semana anterior
5. **Análise**: Detecta atrasos e mudanças

📝 **Revisar em futuras sprints**: Automatizar geração de snapshots.

---

## 7. Implementação de Tabela Semanal Vibracoustic

Esta seção detalha como implementar uma tabela de pedidos semanais com a lógica de sextas-feiras e sistema de abatimento, especificamente para o cliente Vibracoustic.

### 7.1 Identificação de Cliente

#### 7.1.1 Campo de Vinculação
Os pedidos são vinculados ao cliente através de:
- **Durante upload**: Parser identifica "VIBRACOUSTIC" no PDF
- **Campo armazenado**: `pedido.cliente_nome` = "VIBRACOUSTIC"
- **Índice Redis**: `pedidos:cliente:vibracoustic` (Set com IDs)

```typescript
// Ao processar PDF
if (pdfText.includes('VIBRACOUSTIC')) {
  pedido.cliente_nome = 'VIBRACOUSTIC'
  await redis.sAdd('pedidos:cliente:vibracoustic', pedido.id)
}
```

#### 7.1.2 Exemplo de Chave Redis
```bash
# Set com todos os pedidos da Vibracoustic
pedidos:cliente:vibracoustic → ["ped_123", "ped_456", "ped_789"]

# Buscar pedidos
const pedidosVibra = await redis.sMembers('pedidos:cliente:vibracoustic')
```

### 7.1.3 Parser de PDF Vibracoustic

#### Expressões Regulares para Extração

```typescript
// Três regex principais para parsing de PDFs Vibracoustic
const REGEX_PEDIDO = /Pedido\s+No\.\s*:\s*(\d{8,10})/
const REGEX_CODIGO = /Código\s*:\s*([A-Z]{2}-\d{3})/
const REGEX_ENTREGA = /Entrega\s+(\d{2}\/\d{2}\/\d{4})\s+(\d+)/g
```

#### Código de População de Dados

```typescript
// api/pedidos/upload/route.ts - Parser Vibracoustic
async function parsePDFVibracoustic(pdfText: string) {
  const pedido = {
    id: `ped_${Date.now()}`,
    pedido_numero: '',
    cliente_nome: 'VIBRACOUSTIC',
    uploaded_at: new Date().toISOString(),
    itens: []
  }
  
  // 1. Extrair número do pedido
  const matchPedido = pdfText.match(REGEX_PEDIDO)
  if (matchPedido) {
    pedido.pedido_numero = matchPedido[1]
  }
  
  // 2. Extrair itens por código
  const codigosEncontrados = new Set<string>()
  let matchCodigo
  const regexCodigo = new RegExp(REGEX_CODIGO.source, 'g')
  
  while ((matchCodigo = regexCodigo.exec(pdfText)) !== null) {
    const codigo = matchCodigo[1]
    if (!codigosEncontrados.has(codigo)) {
      codigosEncontrados.add(codigo)
      
      // 3. Para cada código, buscar entregas
      const item = {
        codigo,
        descricao: `Produto ${codigo}`,
        entregas: []
      }
      
      // Buscar entregas deste código
      const secaoProduto = pdfText.substring(
        pdfText.indexOf(codigo),
        pdfText.indexOf(codigo, pdfText.indexOf(codigo) + 1) || pdfText.length
      )
      
      let matchEntrega
      while ((matchEntrega = REGEX_ENTREGA.exec(secaoProduto)) !== null) {
        item.entregas.push({
          data: matchEntrega[1],      // DD/MM/YYYY
          quantidade: parseInt(matchEntrega[2]),
          status: 'Firm'              // Calcular depois baseado na data
        })
      }
      
      if (item.entregas.length > 0) {
        pedido.itens.push(item)
      }
    }
  }
  
  // 4. Salvar índice para busca rápida
  await redis.set(`pedido:numero:${pedido.pedido_numero}`, pedido.id)
  
  return pedido
}
```

### 7.2 Filtro de Notas por Cliente

#### 7.2.1 Chamada Tiny para Notas Vibracoustic
```http
POST /notas.fiscais.pesquisa.php
Content-Type: application/x-www-form-urlencoded

token={TOKEN}&formato=JSON&tipoNota=S&situacao=6,7&cliente=VIBRACOUSTIC%20SOUTH%20AMERICA
```

Alternativa com wildcard (mais abrangente):
```http
POST /notas.fiscais.pesquisa.php
Content-Type: application/x-www-form-urlencoded

token={TOKEN}&formato=JSON&tipoNota=S&situacao=6,7&cliente=VIBRACOUSTIC%25
```

#### 7.2.2 Filtro no Worker
```typescript
// worker/notas-worker.ts
async function sincronizarNotasVibracoustic() {
  // Busca específica para Vibracoustic
  const notasVibra = await tiny.buscarNotasPorData(
    dataInicio,
    dataFim,
    'VIBRACOUSTIC SOUTH AMERICA LTDA'
  )
  
  for (const nota of notasVibra) {
    // Adiciona ao índice específico
    await redis.sAdd('notas:cliente:vibracoustic', nota.id)
    
    // Salva nota normalmente
    await salvarNota(nota)
  }
}
```

### 7.3 Ligação Pedido ↔ Nota

#### 7.3.1 Regra de Casamento
```typescript
// Campo na nota: item.numero_pedido_compra = "4530123456"
// Campo no pedido: pedido_numero = "4530123456"

function normalizarNumeroPedido(numero: string): string {
  return numero
    .toString()
    .replace(/^0+/, '')  // Remove zeros à esquerda
    .replace(/\s/g, '')  // Remove espaços
    .replace(/-/g, '')   // Remove hífens
    .trim()
}
```

#### 7.3.2 Normalização Completa
```typescript
interface MatchingResult {
  pedidoId?: string
  matched: boolean
  reason?: string
}

async function encontrarPedidoParaNota(
  item: ItemNota
): Promise<MatchingResult> {
  const numeroNormalizado = normalizarNumeroPedido(
    item.numero_pedido_compra || ''
  )
  
  if (!numeroNormalizado) {
    return { matched: false, reason: 'Sem número de pedido' }
  }
  
  // Busca no índice
  const pedidoId = await redis.get(`pedido:numero:${numeroNormalizado}`)
  
  if (!pedidoId) {
    console.warn(`⚠️ Nota órfã: pedido ${numeroNormalizado} não encontrado`)
    return { matched: false, reason: 'Pedido não encontrado' }
  }
  
  return { matched: true, pedidoId }
}
```

#### 7.3.3 Tratamento de Notas Órfãs
```typescript
// Registrar notas sem pedido correspondente
await redis.sAdd('notas:orfas', nota.id)
await redis.hSet(`nota:orfa:${nota.id}`, {
  numero: nota.numero,
  data: nota.data_emissao,
  cliente: nota.cliente.nome,
  valor: nota.valor,
  motivo: 'Pedido não encontrado no sistema'
})
```

### 7.4 Agregação Semanal

#### 7.4.1 Fórmula de Saldo
```typescript
// Para cada semana e código de produto:
saldo_semana = Σ(entregas_semana.quantidade) - Σ(quantidade_abatida_semana)
```

#### 7.4.2 Endpoint de Agregação Semanal
```typescript
// GET /api/pedidos/semanais?cliente=VIBRACOUSTIC&semana=2025-W30

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const cliente = searchParams.get('cliente')
  const semana = searchParams.get('semana')
  
  // Buscar pedidos do cliente
  const pedidosIds = await redis.sMembers(`pedidos:cliente:${cliente.toLowerCase()}`)
  const pedidos = await Promise.all(
    pedidosIds.map(id => redis.get(`pedido:${id}`))
  )
  
  // Buscar notas do cliente
  const notasIds = await redis.sMembers(`notas:cliente:${cliente}`)
  const notas = await Promise.all(
    notasIds.map(id => redis.get(`nota:${id}`))
  )
  
  // Calcular abatimentos
  const abatimentos = calcularAbatimento(pedidos, notas)
  
  // Agregar por semana e código
  const agregado = {}
  
  for (const pedido of pedidos) {
    for (const item of pedido.itens) {
      for (const entrega of item.entregas) {
        const semanaEntrega = getISOWeek(parseDate(entrega.data))
        
        if (semanaEntrega !== semana) continue
        
        const key = `${item.codigo}_${semanaEntrega}`
        
        if (!agregado[key]) {
          agregado[key] = {
            codigo: item.codigo,
            semana: semanaEntrega,
            quantidade_pedida: 0,
            quantidade_abatida: 0,
            saldo: 0,
            status: 'Firm',
            cor: getCorSemana(semanaEntrega)
          }
        }
        
        agregado[key].quantidade_pedida += entrega.quantidade
        agregado[key].quantidade_abatida += abatimentos[item.codigo] || 0
        agregado[key].saldo = agregado[key].quantidade_pedida - agregado[key].quantidade_abatida
      }
    }
  }
  
  return NextResponse.json({
    success: true,
    semana,
    cliente,
    resumo: Object.values(agregado)
  })
}
```

### 7.5 Enum de Status

```typescript
enum StatusEntrega {
  FIRM = 'Firm',        // Dentro de 30 dias da data do pedido
  FORECAST = 'Forecast', // Além de 30 dias
  BACKLOG = 'Backlog',   // Data já passou
  CANCELED = 'Canceled'  // Entrega cancelada (opcional)
}

// Transições automáticas
function getStatusEntrega(
  dataEntrega: Date,
  dataPedido: Date
): StatusEntrega {
  const hoje = new Date()
  
  // Se já passou
  if (dataEntrega < hoje) {
    return StatusEntrega.BACKLOG
  }
  
  // Calcula dias desde o pedido
  const diasDesdePedido = differenceInDays(dataEntrega, dataPedido)
  
  if (diasDesdePedido <= 30) {
    return StatusEntrega.FIRM
  }
  
  return StatusEntrega.FORECAST
}
```

### 7.6 Exemplo End-to-End

#### 7.6.1 Fixture de Pedido
```json
// fixtures/pedido_vibracoustic.json
{
  "id": "ped_vb_001",
  "pedido_numero": "4530789012",
  "cliente_nome": "VIBRACOUSTIC",
  "uploaded_at": "2025-07-01T10:00:00Z",
  "itens": [
    {
      "codigo": "PH-510",
      "descricao": "ARRUELA TRAVA",
      "entregas": [
        {
          "data": "25/07/2025",
          "quantidade": 1000,
          "status": "Firm"
        },
        {
          "data": "01/08/2025",
          "quantidade": 500,
          "status": "Firm"
        }
      ]
    },
    {
      "codigo": "PH-511",
      "descricao": "PARAFUSO M10",
      "entregas": [
        {
          "data": "25/07/2025",
          "quantidade": 2000,
          "status": "Firm"
        }
      ]
    }
  ]
}
```

#### 7.6.2 Fixture de Nota
```json
// fixtures/nota_vibracoustic.json
{
  "id": "nota_vb_001",
  "numero": "005182",
  "data_emissao": "20/07/2025",
  "cliente": {
    "nome": "VIBRACOUSTIC SOUTH AMERICA LTDA"
  },
  "itens": [
    {
      "item": {
        "codigo": "PH-510",
        "quantidade": "600",
        "numero_pedido_compra": "4530789012"
      }
    },
    {
      "item": {
        "codigo": "PH-511",
        "quantidade": "2000",
        "numero_pedido_compra": "4530789012"
      }
    }
  ]
}
```

#### 7.6.3 Tabela Esperada Após Abatimento

| Semana | Código | Qtd Pedida | Qtd Abatida | Saldo | Status | Cor |
|--------|--------|------------|-------------|-------|--------|-----|
| 2025-W30 (25/07) | PH-510 | 1000 | 600 | 400 | Firm | Amarelo |
| 2025-W30 (25/07) | PH-511 | 2000 | 2000 | 0 | Firm | Verde ✓ |
| 2025-W31 (01/08) | PH-510 | 500 | 0 | 500 | Firm | Azul |

### 7.7 Tokens de Cor no Tailwind

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        semana1: '#3B82F6',
        semana2: '#8B5CF6',
        semana3: '#10B981',
        semana4: '#F59E0B',
        semana5: '#F97316',
        backlog: '#EF4444',
        forecast: '#D97706',
        saldoZero: '#dcfce7',
        saldoNeg: '#991b1b'
      }
    }
  },
  // Importante: adicionar ao safelist se usar dinamicamente
  safelist: [
    'bg-semana1', 'bg-semana2', 'bg-semana3', 'bg-semana4', 'bg-semana5',
    'bg-backlog', 'bg-forecast', 'bg-saldoZero', 'bg-saldoNeg',
    'text-white', 'text-green-800'
  ]
}
```

### 7.8 Colunas TanStack Table

```typescript
// components/tabela-pedidos-vibracoustic/columns.ts
import { ColumnDef } from '@tanstack/react-table'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

interface PedidoSemanal {
  data: Date
  codigo: string
  descricao: string
  quantidade_pedida: number
  quantidade_abatida: number
  saldo: number
  status: 'Firm' | 'Forecast' | 'Backlog'
  semana: number  // 1-5 para aplicar cor
}

export const columns: ColumnDef<PedidoSemanal>[] = [
  {
    accessorKey: 'data',
    header: 'Semana',
    cell: ({ row }) => {
      const data = row.getValue('data') as Date
      return format(data, "dd/MM - 'Sem' w", { locale: ptBR })
    }
  },
  {
    accessorKey: 'codigo',
    header: 'Código',
    cell: ({ row }) => (
      <span className="font-mono">{row.getValue('codigo')}</span>
    )
  },
  {
    accessorKey: 'quantidade_pedida',
    header: 'Qtd Pedido',
    cell: ({ row }) => {
      const valor = row.getValue('quantidade_pedida') as number
      return valor.toLocaleString('pt-BR')
    }
  },
  {
    accessorKey: 'quantidade_abatida',
    header: 'Qtd Abatido',
    cell: ({ row }) => {
      const valor = row.getValue('quantidade_abatida') as number
      return (
        <span className="text-blue-600">
          {valor.toLocaleString('pt-BR')}
        </span>
      )
    }
  },
  {
    accessorKey: 'saldo',
    header: 'Saldo',
    cell: ({ row }) => {
      const saldo = row.getValue('saldo') as number
      const status = row.original.status
      const semana = row.original.semana
      
      // Política de cores usando tokens Tailwind
      let className = ''
      let icon = ''
      
      if (saldo === 0) {
        className = 'bg-saldoZero text-green-800 font-semibold'
        icon = ' ✓'
      } else if (saldo < 0) {
        className = 'bg-saldoNeg text-white font-bold'
        icon = ' ❗'
      } else if (status === 'Backlog') {
        className = 'bg-backlog text-white'
      } else if (status === 'Forecast') {
        className = 'bg-forecast text-white'
      } else {
        // Status Firm usa cor da semana
        className = `bg-semana${semana} text-white`
      }
      
      return (
        <div className={`px-2 py-1 rounded text-center ${className}`}>
          {saldo.toLocaleString('pt-BR')}{icon}
        </div>
      )
    }
  },
  {
    accessorKey: 'status',
    header: 'Status',
    cell: ({ row }) => {
      const status = row.getValue('status') as string
      const statusColors = {
        'Firm': 'text-orange-600',
        'Forecast': 'text-amber-600',
        'Backlog': 'text-red-600'
      }
      
      return (
        <span className={`font-medium ${statusColors[status]}`}>
          {status}
        </span>
      )
    }
  }
]
```

### 7.9 Ícones & Legenda

A tabela usa **Unicode puro** para ícones, sem dependências externas:
- **✓** (U+2713) - Saldo zerado (sucesso)
- **❗** (U+2757) - Saldo negativo (erro)

#### Tabela-Legenda de Cores e Ícones

| Situação | Cor (classe) | Hex | Ícone |
|----------|--------------|-----|-------|
| Saldo = 0 | `bg-saldoZero` | #dcfce7 | ✓ |
| Saldo < 0 | `bg-saldoNeg` | #991b1b | ❗ |
| Backlog | `bg-backlog` | #ef4444 | — |
| Forecast | `bg-forecast` | #d97706 | — |
| Firm Sem 1 | `bg-semana1` | #3b82f6 | — |
| Firm Sem 2 | `bg-semana2` | #8b5cf6 | — |
| Firm Sem 3 | `bg-semana3` | #10b981 | — |
| Firm Sem 4 | `bg-semana4` | #f59e0b | — |
| Firm Sem 5 | `bg-semana5` | #f97316 | — |

### 7.10 Política de Cores (Refinada)

```typescript
// lib/cores-saldo.ts
interface CorConfig {
  backgroundColor: string
  textColor: string
  borderColor?: string
  icon?: string
}

export function getCorSaldo(
  saldo: number,
  status: StatusEntrega,
  corSemana: string
): CorConfig {
  // Saldo zerado = sucesso
  if (saldo === 0) {
    return {
      backgroundColor: '#dcfce7', // green-100
      textColor: '#166534',       // green-800
      icon: '✓'
    }
  }
  
  // Saldo negativo = erro crítico
  if (saldo < 0) {
    return {
      backgroundColor: '#991b1b', // red-800
      textColor: '#ffffff',
      borderColor: '#dc2626',     // red-600
      icon: '❗'
    }
  }
  
  // Saldo positivo com status
  if (status === StatusEntrega.BACKLOG) {
    return {
      backgroundColor: '#ef4444', // red-500
      textColor: '#ffffff'
    }
  }
  
  if (status === StatusEntrega.FORECAST) {
    return {
      backgroundColor: '#d97706', // amber-600
      textColor: '#ffffff'
    }
  }
  
  // Status FIRM usa cor da semana
  return {
    backgroundColor: corSemana,
    textColor: '#ffffff'
  }
}
```

### 7.11 Seed Redis de Exemplo

#### Script de População

```typescript
// scripts/seed-vibra.ts
import { redis } from '@/lib/redis'
import { ensureRedisConnection } from '@/lib/redis'
import pedido from '@/fixtures/pedido_vibracoustic.json'
import nota from '@/fixtures/nota_vibracoustic.json'

async function seedVibracoustic() {
  await ensureRedisConnection()
  
  console.log('🌱 Populando dados Vibracoustic...')
  
  // 1. Salvar pedido
  await redis.set(`pedido:${pedido.id}`, JSON.stringify(pedido))
  await redis.sAdd('pedidos:all', pedido.id)
  await redis.sAdd('pedidos:cliente:vibracoustic', pedido.id)
  await redis.set(`pedido:numero:${pedido.pedido_numero}`, pedido.id)
  console.log(`✅ Pedido ${pedido.pedido_numero} salvo`)
  
  // 2. Salvar nota
  await redis.set(`nota:${nota.id}`, JSON.stringify(nota))
  await redis.sAdd('notas:all', nota.id)
  await redis.sAdd('notas:cliente:vibracoustic', nota.id)
  
  // 3. Adicionar ao índice por produto
  for (const item of nota.itens) {
    const codigo = item.item.codigo
    const timestamp = new Date('2025-07-20').getTime()
    await redis.zAdd(`notas:produto:${codigo}`, {
      score: timestamp,
      member: nota.id
    })
  }
  console.log(`✅ Nota ${nota.numero} salva`)
  
  // 4. Verificar dados
  const pedidoSalvo = await redis.get(`pedido:${pedido.id}`)
  const notaSalva = await redis.get(`nota:${nota.id}`)
  
  if (pedidoSalvo && notaSalva) {
    console.log('✅ Seed concluído com sucesso!')
    console.log('📊 Acesse /pedidos para ver a tabela Vibracoustic')
  } else {
    console.error('❌ Erro ao verificar dados salvos')
  }
  
  await redis.quit()
}

seedVibracoustic().catch(console.error)
```

#### Instruções de Uso

```bash
# Executar seed
npx tsx scripts/seed-vibra.ts

# Verificar dados no Redis
npx tsx -e "
import { redis } from './lib/redis'
await redis.ensureRedisConnection()
const pedidos = await redis.sMembers('pedidos:cliente:vibracoustic')
console.log('Pedidos Vibracoustic:', pedidos)
await redis.quit()
"
```

### 7.12 Fixture de Teste Automatizado

```typescript
// __tests__/abatimento-vibracoustic.test.ts
import { describe, it, expect } from 'vitest'
import { calcularAbatimento } from '@/lib/abatimento'
import pedidoFixture from '@/fixtures/pedido_vibracoustic.json'
import notaFixture from '@/fixtures/nota_vibracoustic.json'

describe('Abatimento Vibracoustic', () => {
  it('deve aplicar FIFO e calcular saldos corretos', () => {
    const abatimentos = calcularAbatimento(
      [pedidoFixture],
      [notaFixture]
    )
    
    // PH-510: 600 abatidos de 1000 da primeira entrega
    expect(abatimentos.get('PH-510')).toEqual({
      quantidade: 600,
      notaNumero: '005182',
      data: '20/07/2025',
      entregas: [
        { data: '25/07/2025', quantidade: 600 }
      ]
    })
    
    // PH-511: 2000 totalmente abatidos
    expect(abatimentos.get('PH-511')).toEqual({
      quantidade: 2000,
      notaNumero: '005182',
      data: '20/07/2025',
      entregas: [
        { data: '25/07/2025', quantidade: 2000 }
      ]
    })
    
    // Calcular saldos
    const saldoPH510Sem30 = 1000 - 600 // 400
    const saldoPH511Sem30 = 2000 - 2000 // 0
    const saldoPH510Sem31 = 500 - 0     // 500
    
    expect(saldoPH510Sem30).toBe(400)
    expect(saldoPH511Sem30).toBe(0)
    expect(saldoPH510Sem31).toBe(500)
  })
  
  it('deve respeitar ordem FIFO para múltiplas entregas', () => {
    const pedidoMultiplo = {
      ...pedidoFixture,
      itens: [{
        codigo: 'PH-520',
        entregas: [
          { data: '18/07/2025', quantidade: 100 }, // Mais antiga
          { data: '25/07/2025', quantidade: 200 },
          { data: '01/08/2025', quantidade: 300 }
        ]
      }]
    }
    
    const notaAbate = {
      ...notaFixture,
      itens: [{
        item: {
          codigo: 'PH-520',
          quantidade: '250' // Abate 100 + 150 da segunda
        }
      }]
    }
    
    const abatimentos = calcularAbatimento(
      [pedidoMultiplo],
      [notaAbate]
    )
    
    expect(abatimentos.get('PH-520')).toEqual({
      quantidade: 250,
      notaNumero: '005182',
      data: '20/07/2025',
      entregas: [
        { data: '18/07/2025', quantidade: 100 },
        { data: '25/07/2025', quantidade: 150 }
      ]
    })
  })
})
```

📝 **Revisar em futuras sprints**: Adicionar gráfico de evolução semanal de saldos.

---

## 8. Padrões de Código

### 8.1 Convenções de Nomes

| Tipo | Padrão | Exemplo |
|------|--------|---------|
| **Componentes** | PascalCase | `TabelaVisualPedidos.tsx` |
| **Funções** | camelCase | `calcularAbatimento()` |
| **Constantes** | UPPER_SNAKE | `MAX_TENTATIVAS` |
| **Tipos/Interfaces** | PascalCase | `interface NotaFiscal` |
| **Arquivos** | kebab-case | `tiny-api.ts` |
| **Rotas API** | kebab-case | `/api/pedidos/upload` |

### 7.2 Formato de Datas

```typescript
// Exibição para usuário
format(date, 'dd/MM/yyyy', { locale: ptBR })  // 21/07/2025

// Headers de tabela
format(date, "dd/MM - 'Sem' w")               // 25/07 - Sem 4

// Semanas ISO
format(date, "yyyy-'W'ww")                     // 2025-W28

// Timestamps internos
date.getTime()                                 // 1737456789000
```

### 7.3 Tratamento de Exceções

```typescript
// API Routes
try {
  await ensureRedisConnection()
  // lógica...
} catch (error) {
  console.error('Contexto:', { endpoint, params }, error)
  return NextResponse.json(
    { success: false, error: 'Mensagem amigável' },
    { status: 500 }
  )
}

// Componentes
try {
  const response = await fetch('/api/endpoint')
  if (!response.ok) throw new Error('Falha na requisição')
  // continua...
} catch (error) {
  toast.error('Erro ao carregar dados')
  console.error(error)
}
```

### 7.4 Política de Logs

```typescript
// Worker - Usa emojis para status
console.log('✅ Sincronização concluída')
console.log('⚠️ API bloqueada temporariamente')
console.log('❌ Erro crítico:', error)

// API - Logs estruturados
console.log({
  timestamp: new Date().toISOString(),
  level: 'error',
  endpoint: '/api/notas',
  error: error.message,
  context: { userId, params }
})

// Frontend - Apenas desenvolvimento
if (process.env.NODE_ENV === 'development') {
  console.log('Debug:', data)
}
```

### 7.5 Estrutura de Componentes

```tsx
'use client'  // apenas se necessário

// 1. Imports externos
import { useState, useEffect } from 'react'
import { format } from 'date-fns'

// 2. Imports internos
import { useToast } from '@/hooks/use-toast'
import { Button } from '@/components/ui/button'

// 3. Types/Interfaces
interface ComponentProps {
  data: any[]
  onUpdate?: (id: string) => void
}

// 4. Componente
export function Component({ data, onUpdate }: ComponentProps) {
  // 1. Hooks
  const { toast } = useToast()
  
  // 2. Estado
  const [loading, setLoading] = useState(false)
  
  // 3. Effects
  useEffect(() => {
    // efeitos...
  }, [])
  
  // 4. Handlers
  const handleClick = async () => {
    // lógica...
  }
  
  // 5. Render
  return (
    <div className="space-y-4">
      {/* JSX */}
    </div>
  )
}
```

📝 **Revisar em futuras sprints**: Adicionar ESLint rules customizadas.

---

## 8. FAQ & Pitfalls

### 8.1 Problemas Comuns

#### "Notas não aparecem na listagem"
1. **Verificar índice**: A nota deve estar em `notas:all`
2. **Checar blacklist**: Empresa pode estar bloqueada
3. **Filtro embalagens**: Nota pode ter apenas embalagens
4. **Worker parado**: Verificar logs do worker

```bash
# Debug
npx tsx -e "
import { redis } from './lib/redis'
const exists = await redis.sIsMember('notas:all', 'NOTA_ID')
console.log('Nota no índice:', exists)
"
```

#### "ERR too many keys to fetch" no Upstash
- **Causa**: Comando `keys()` com muitos resultados
- **Solução**: Usar `SCAN` com cursor
- **Exemplo**: Ver `/api/configuracoes/empresas/route.ts`

#### "Pedido não mostra abatimento"
1. **Códigos diferentes**: Produto na nota vs pedido
2. **Data posterior**: Nota depois do pedido
3. **Estrutura aninhada**: Verificar `item.item`

#### "Build falha com out of memory"
```bash
# Aumentar limite de memória
NODE_OPTIONS="--max-old-space-size=8192" npm run build
```

### 8.2 Armadilhas do Tiny ERP

1. **Campo `unidadeTributavel`**: Deve ser string, não number
2. **Token expirado**: API retorna 302 (redirect)
3. **Caracteres especiais**: Podem vir com encoding errado
4. **Rate limit**: Não documentado, ~10k/dia
5. **Campos opcionais**: Podem vir como `""` não `null`

### 8.3 Limitações do Upstash

| Comando | Limitação | Alternativa |
|---------|-----------|-------------|
| `KEYS pattern` | Falha com muitas chaves | Use `SCAN` |
| `FLUSHALL` | Não permitido | Delete individual |
| Pipelines grandes | Timeout | Lotes menores |
| `CONFIG` | Bloqueado | N/A |

### 8.4 Next.js 15 Gotchas

```typescript
// ❌ Errado - Next.js 15
export async function GET(request, { params }) {
  const id = params.id  // Erro!
}

// ✅ Correto - Next.js 15
export async function GET(request, { params }) {
  const resolvedParams = await params
  const id = resolvedParams.id
}
```

📝 **Revisar em futuras sprints**: Criar troubleshooting guide completo.

---

## 9. TODO & Gaps

### 9.1 Bugs Identificados

| ID | Descrição | Severidade | Arquivo |
|----|-----------|------------|---------|
| BUG:001 | Entregas de final de mês agrupadas no mês seguinte | Alta | `/lib/semanas-por-sexta.ts` |
| BUG:002 | Cálculo firm/forecast usa data ajustada, não original | Média | `/components/pedidos-table.tsx` |
| BUG:003 | Upload falha silenciosamente com PDFs > 10MB | Baixa | `/api/pedidos/upload/route.ts` |

### 9.2 Features Pendentes

1. **Sistema de notificações** para pedidos atrasados
2. **Histórico de movimentações** de estoque
3. **API write** para atualizar estoque no Tiny
4. **Dashboard mobile** responsivo
5. **Exportação automatizada** de relatórios
6. **Integração com WhatsApp** para alertas

### 9.3 Melhorias Técnicas

- [ ] Migrar para **JWT** com refresh tokens
- [ ] Implementar **cache layer** com Redis
- [ ] Adicionar **testes E2E** com Playwright  
- [ ] Configurar **CI/CD** com GitHub Actions
- [ ] Implementar **observability** com OpenTelemetry
- [ ] Adicionar **rate limiting** nas APIs
- [ ] Criar **API documentation** com OpenAPI

### 9.4 Débito Técnico

```typescript
// TODO: Remover após migração para novo formato
const legacyProductKey = `produto:${id}`  // Obsoleto, usar produto:codigo:

// FIXME: Timeout hardcoded
await sleep(5000)  // Deveria ser configurável

// HACK: Workaround para bug do Upstash
if (keys.length > 100) {
  // Processa em lotes...
}
```

### 9.5 Pontos de Atenção

1. **Performance**: Tabela visual carrega todos os dados (sem paginação)
2. **Segurança**: Tokens hardcoded no código (mover para vault)
3. **Escalabilidade**: Worker single-threaded pode ser gargalo
4. **Manutenibilidade**: Lógica de negócio misturada com UI
5. **Monitoramento**: Falta alerting para falhas críticas

---

## 10. Ambiente de Desenvolvimento

### 10.1 Setup Local Rápido

**1. Clonar o repositório:**
```bash
git clone https://github.com/seu-usuario/DashboardNext.git
cd DashboardNext
```

**2. Instalar dependências:**
```bash
npm install
# ou
yarn install
```

**3. Configurar variáveis de ambiente:**
```bash
# Criar arquivo .env.local na raiz
cat > .env.local << EOF
# Tiny API
TINY_API_TOKEN=fe8abfe8be5255938b70cb7f671c723ab21af6e1102f6cd730a93228d78bc5bb

# Redis (usar Upstash público para dev)
VALKEY_URL=redis://default:senha@servidor.upstash.io:6379
VALKEY_PUBLIC_URL=redis://default:senha@servidor.upstash.io:6379

# Auth (opcional para dev)
AUTH_SECRET=desenvolvimento-local-secret
EOF
```

**4. Iniciar servidor de desenvolvimento:**
```bash
# Com script otimizado (inicia Redis + Turbopack)
./dev.sh

# Ou apenas o Next.js
npm run dev
```

**5. Seed de dados mínimo (opcional):**
```bash
# Popular com dados de teste
npx tsx scripts/seed-desenvolvimento.ts

# Ou sincronizar dados reais
npm run sync:hoje
```

**Portas padrão:**
- Frontend: http://localhost:3000
- Redis local: localhost:6379

### 10.2 Workflow de Build e Deploy (Fly.io)

**1. Build local para teste:**
```bash
# Build completo com validações
npm run verificar

# Apenas build de produção
npm run build

# Build do worker
npm run build:worker
```

**2. Dockerfile otimizado:**
```dockerfile
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
RUN npm run build:worker

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
RUN addgroup --system nodejs && adduser --system nextjs

COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
COPY --from=builder /app/worker/dist ./worker/dist

USER nextjs
EXPOSE 3000
ENV PORT 3000

CMD ["node", "server.js"]
```

**3. Secrets necessários no Fly.io:**
```bash
# Configurar secrets
fly secrets set TINY_API_TOKEN=seu_token_aqui
fly secrets set VALKEY_URL=redis://interno.fly.dev:6379
fly secrets set VALKEY_PUBLIC_URL=redis://publico.upstash.io:6379

# Verificar secrets
fly secrets list
```

**4. Deploy via CLI:**
```bash
# Deploy apenas do app
fly deploy

# Deploy forçado com nova build
fly deploy --no-cache

# Via aliases configurados
uf    # Deploy rápido app
uff   # Deploy completo app + worker
df    # Deploy com Depot (cache remoto)
```

### 10.3 Checklist de CI/CD

**GitHub Actions Workflow (.github/workflows/deploy.yml):**

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
  
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run TypeScript check
        run: npm run type-check
      
      - name: Run ESLint
        run: npm run lint
      
      - name: Build application
        run: npm run build
        env:
          NEXT_TELEMETRY_DISABLED: 1
      
      - name: Build worker
        run: npm run build:worker

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: superfly/flyctl-actions/setup-flyctl@master
      
      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**Checklist de pré-deploy:**

- [ ] ✅ TypeScript sem erros (`npm run type-check`)
- [ ] ✅ ESLint passou (`npm run lint`)
- [ ] ✅ Build de produção OK (`npm run build`)
- [ ] ✅ Worker compila (`npm run build:worker`)
- [ ] ✅ Testes passando (quando implementados)
- [ ] ✅ Secrets configurados no Fly.io
- [ ] ✅ Redis/Upstash acessível
- [ ] ✅ Token Tiny válido
- [ ] ✅ Versão incrementada no package.json

**Monitoramento pós-deploy:**

```bash
# Logs em tempo real
fly logs

# Status da aplicação
fly status

# Métricas
fly dashboard

# SSH para debug
fly ssh console
```

📝 **Revisar em futuras sprints**: Adicionar testes automatizados e coverage mínimo.

---

## 📝 Revisão e Manutenção

Esta documentação deve ser atualizada a cada:
- Nova feature implementada
- Bug crítico corrigido  
- Mudança na integração Tiny
- Alteração em fluxos de negócio
- Refatoração significativa

**Última atualização**: 21/07/2025  
**Versão do sistema**: 1.1.196  
**Mantido por**: Sub-Agente de Documentação Técnica

---

*Para dúvidas ou sugestões, abra uma issue no repositório.*