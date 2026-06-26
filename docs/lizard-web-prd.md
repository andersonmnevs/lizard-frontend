# Lizard Web — PRD: Portal de Consulta Histórica de Classificação de Couros

**Projeto:** Lizard Web  
**Owner:** Viposa SA  
**Data:** 2026-06-22  
**Versão:** 1.0 — Rascunho  
**Status:** Draft

---

## 1. Visão Geral

### 1.1 Objetivo

Criar um portal web de consulta histórica que permita a operadores, supervisores e gerentes visualizar os resultados de classificação de couros gerados pelo sistema Lizard, acessando dados agregados por ordem de produção, registros individuais por couro e imagens processadas com sobreposição de defeitos.

### 1.2 Contexto

O sistema Lizard opera na máquina da esteira industrial (Linux, GPU) e já persiste todos os resultados de classificação em dois locais:

- **SQLite** (`GrdResPat`, `GrdOp`, `GrdHidNum`, `GrdAre`, `GrdCla`, `GrdUsaPer`, `GrdDat`) — banco de dados local em `lizard/data/`
- **Disco** — imagens do couro processadas com sobreposição de defeitos em `results/{date}/{op}/` e máscaras por classe em `results/{date}/{op}/detections/`

O Lizard Web não interage com o pipeline de inferência. É uma camada de leitura sobre dados já produzidos.

### 1.3 O que está fora do escopo desta versão

- Atualização em tempo real (sem polling, sem WebSocket)
- Autenticação e controle de acesso por perfil
- Edição ou correção de registros
- Integração com sistemas externos (ERP, API de OP)
- Imagens brutas das câmeras (somente imagem processada com defeitos)

---

## 2. Perfis de Usuário

Todos os perfis acessam a mesma interface sem distinção de login. As diferenças são de frequência e foco de uso, não de permissão.

| Perfil | Objetivo principal | Frequência de uso |
|--------|--------------------|-------------------|
| **Operador** | Verificar se a classificação de um couro específico está correta | Contínua (durante o turno) |
| **Supervisor** | Acompanhar o desempenho da linha por turno ou por OP | Horária |
| **Gerente / Analista** | Analisar tendências de qualidade por período, classe e aproveitamento | Diária / semanal |

---

## 3. Funcionalidades

### 3.1 Dashboard (Página Inicial)

Visão consolidada do estado recente da produção.

**Dados exibidos:**
- Total de couros classificados no dia atual e na semana
- Aproveitamento médio do dia e da semana
- Distribuição de classes do dia (gráfico de barras ou pizza)
- Últimas OPs processadas (lista com link para detalhe)

**Regras:**
- "Dia atual" = registros com `GrdDat` na data de hoje (localtime)
- "Semana" = últimos 7 dias corridos
- Sem filtros na página — é uma visão fixa e rápida
- Nenhuma imagem é exibida no dashboard

---

### 3.2 Lista de OPs

Listagem paginada de todas as ordens de produção com suporte a busca e filtros.

**Colunas exibidas:**
- Número da OP
- Data da última atualização
- Total de couros classificados
- Aproveitamento médio
- Classe predominante

**Filtros disponíveis:**
- Período (data início / data fim) — baseado em `GrdDat`
- Classe predominante (select com todas as classes disponíveis)
- Busca por número de OP (campo de texto)

**Regras:**
- Ordenação padrão: data decrescente (mais recente primeiro)
- Paginação: 20 OPs por página
- Clicar em uma OP navega para o Detalhe da OP
- Nenhuma imagem é exibida nesta tela

---

### 3.3 Detalhe da OP

Visão completa de uma ordem de produção específica.

**Seção superior — Resumo agregado:**
- Número da OP
- Total de couros processados
- Área média (m²)
- Aproveitamento médio (%)
- Distribuição de classes em percentual (tabela e gráfico)

**Seção inferior — Lista de couros:**
- Número do couro (`GrdHidNum`)
- Data e hora do processamento (`GrdDat`)
- Classe atribuída (`GrdCla`)
- Aproveitamento (`GrdUsaPer`)
- Área (`GrdAre`)
- Link para o Detalhe do Couro

**Regras:**
- Ordenação padrão: número do couro crescente
- Nenhuma imagem é exibida nesta tela
- Botão de exportação: gera relatório da OP em PDF e Excel (ver seção 3.5)

---

### 3.4 Detalhe do Couro

Visão individual de um couro classificado.

**Dados exibidos:**
- Número do couro e OP de origem
- Data e hora do processamento
- Classe atribuída
- Aproveitamento (%)
- Área (m²)
- Imagem processada com sobreposição de defeitos

**Regras de exibição da imagem:**
- A imagem é localizada a partir do campo `GrdResPat` no SQLite, que armazena o diretório de resultado da OP (`results/{date}/{op}/`)
- O arquivo de imagem segue o padrão `{date}-{hour}-{op}-{hide_num}-{area}.jpg`
- Se o arquivo não for encontrado no disco, exibe mensagem "Imagem não disponível" — sem erro
- A imagem é servida pela API da esteira via endpoint dedicado
- A imagem é exibida em tamanho original com opção de zoom

**Navegação:**
- Botão "Couro anterior" / "Próximo couro" dentro da mesma OP
- Botão "Voltar para a OP"

---

### 3.5 Exportação de Relatórios

Disponível na tela de Detalhe da OP.

**Relatório PDF:**
- Cabeçalho com número da OP e período
- Tabela com todos os couros (número, data, classe, aproveitamento, área)
- Seção de resumo: totais, médias, distribuição de classes
- Logo Viposa SA

**Relatório Excel (.xlsx):**
- Aba "Couros": uma linha por couro com todas as colunas disponíveis
- Aba "Resumo": métricas agregadas da OP (mesmas do resumo do detalhe da OP)

**Regras:**
- Exportação é gerada sob demanda (não pré-gerada)
- Não inclui imagens nos relatórios desta versão
- O arquivo é baixado diretamente pelo browser

---

## 4. Regras de Negócio

### 4.1 Fonte de dados

| Dado | Origem | Campo |
|------|--------|-------|
| Número da OP | SQLite | `GrdOp` |
| Número do couro | SQLite | `GrdHidNum` |
| Área (m²) | SQLite | `GrdAre` |
| Classe | SQLite | `GrdCla` |
| Aproveitamento (%) | SQLite | `GrdUsaPer` |
| Data/hora | SQLite | `GrdDat` |
| Caminho do resultado | SQLite | `GrdResPat` |
| Imagem do couro | Disco | `{GrdResPat}{basename}.jpg` |

### 4.2 Cálculos agregados

Todos os cálculos são realizados pela API — o frontend apenas exibe.

| Métrica | Cálculo |
|---------|---------|
| Total de couros | `COUNT(GrdHidNum)` por OP |
| Área média | `AVG(GrdAre)` por OP, excluindo NULL |
| Aproveitamento médio | `AVG(GrdUsaPer)` por OP, excluindo NULL |
| Distribuição de classes | `COUNT` por `GrdCla` / total * 100 |
| Classe predominante | `GrdCla` com maior contagem na OP |

### 4.3 Localização de imagens

O campo `GrdResPat` armazena o diretório base da OP (ex: `results/01.01.2026/12345/`).

A API reconstrói o caminho completo da imagem com base no padrão de nomenclatura:
```
{GrdResPat}{GrdDat_date}-{GrdDat_time}-{GrdOp}-{GrdHidNum}-{GrdAre}.jpg
```

Se o arquivo não existir no caminho calculado, a API retorna 404 e o frontend exibe "Imagem não disponível".

---

## 5. Arquitetura Técnica (Alto Nível)

### 5.1 Topologia de deploy

```
Máquina da esteira (Linux, rede local)     Qualquer PC na rede
┌──────────────────────────────────┐       ┌──────────────────┐
│  grading.py (pipeline, intocado) │       │                  │
│                                  │       │  Browser         │
│  lizard-web/                     │◄─────►│  (Chrome/Firefox)│
│    api/   (FastAPI, porta 8000)  │  HTTP │                  │
│      ├── /ops                    │       └──────────────────┘
│      ├── /ops/{id}               │
│      ├── /ops/{id}/hides         │
│      ├── /hides/{id}             │
│      └── /images/{path}          │
│    frontend/ (SPA estática)      │
│                                  │
│  SQLite (existente)              │
│  Imagens em disco (existentes)   │
└──────────────────────────────────┘
```

### 5.2 Stack tecnológica proposta

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| Backend | Python / FastAPI | Mesma linguagem do projeto, lê SQLite diretamente |
| Frontend | React + Vite | SPA leve, boa DX, sem necessidade de SSR |
| Banco | SQLite (existente) | Leitura direta, sem migração |
| Servir imagens | FastAPI `/images` endpoint | Controle de path traversal, sem expor disco diretamente |
| Exportação PDF | `reportlab` ou `weasyprint` | Geração server-side |
| Exportação Excel | `openpyxl` | Biblioteca Python consolidada |
| Deploy | Processo systemd ou `nohup` na esteira | Simples, sem Docker adicional |

### 5.3 Segurança mínima

- O endpoint `/images` valida que o path solicitado está dentro do diretório `results/` configurado — sem path traversal
- A API roda somente na rede local — sem exposição à internet
- Sem autenticação nesta versão (decisão de escopo consciente)

### 5.4 Localização do código

```
lizard/                  ← pipeline existente (intocado)
lizard-web/              ← nova solução
  api/                   ← FastAPI
    main.py
    routers/
      ops.py
      hides.py
      images.py
      exports.py
    db.py                ← leitura do SQLite (separado do db.py do pipeline)
    config.py
  frontend/              ← SPA React
    src/
      pages/
      components/
      api/
```

O `lizard-web/` vive no mesmo repositório mas é completamente independente do pipeline — não importa nenhum módulo de `lizard/`.

---

## 6. Critérios de Aceite (MVP)

| # | Critério |
|---|----------|
| AC-01 | Dashboard exibe total de couros, aproveitamento médio e distribuição de classes do dia |
| AC-02 | Lista de OPs é paginada e filtrável por período e classe |
| AC-03 | Detalhe da OP exibe resumo agregado e lista de todos os couros |
| AC-04 | Detalhe do Couro exibe métricas e imagem processada quando disponível |
| AC-05 | Quando imagem não existe no disco, exibe "Imagem não disponível" sem erro |
| AC-06 | Exportação PDF da OP é gerada com tabela de couros e resumo |
| AC-07 | Exportação Excel da OP contém abas "Couros" e "Resumo" |
| AC-08 | Navegação entre couros de uma mesma OP (anterior / próximo) funciona |
| AC-09 | API não expõe arquivos fora do diretório `results/` configurado |
| AC-10 | Frontend é acessível de qualquer máquina na rede local via browser |

---

## 7. Fora do Escopo (v1)

- Atualização automática / tempo real
- Autenticação e controle de acesso por perfil
- Imagens brutas das 4 câmeras separadas
- Edição ou correção de registros classificados
- Integração com API de ordens de produção (ERP / `get_po.py`)
- Imagens nos relatórios PDF/Excel
- Notificações ou alertas

---

*Lizard Web PRD v1.0 — Viposa SA — 2026-06-22*
