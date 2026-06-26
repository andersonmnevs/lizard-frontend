# Lizard Web — Arquitetura do Sistema

**Agent:** @architect (Aria)
**Data:** 2026-06-26
**Versão:** 1.0
**Status:** Aprovado — pronto para stories

---

## 1. Visão Geral

O Lizard Web é um portal web de consulta histórica de classificação de couros. Opera como uma **camada de leitura** sobre dados já produzidos pelo sistema Lizard (pipeline de inferência existente). Não interage com o pipeline em nenhum momento.

### Topologia de Deploy

```
Máquina da esteira (Linux, rede local)         Qualquer PC na rede
┌────────────────────────────────────────┐      ┌─────────────────┐
│  lizard/  (pipeline — INTOCADO)        │      │                 │
│                                        │      │  Browser        │
│  lizard-web/                           │◄────►│  Chrome/Firefox │
│    api/        FastAPI  :8000          │ HTTP │                 │
│    frontend/   React SPA (estática)    │      └─────────────────┘
│                                        │
│  SQLite  lizard/data/*.db  (existente) │
│  Imagens results/{date}/{op}/  (exist.)│
└────────────────────────────────────────┘
```

**Princípio central:** `lizard-web/` não importa nenhum módulo de `lizard/`. São projetos independentes que compartilham apenas o mesmo SQLite e sistema de arquivos.

---

## 2. Stack Tecnológica

| Camada | Tecnologia | Versão mínima | Justificativa |
|--------|-----------|---------------|---------------|
| Backend | Python + FastAPI | Python 3.10 / FastAPI 0.110 | Mesma linguagem do projeto; lê SQLite diretamente |
| Frontend | React + Vite | React 18 / Vite 5 | SPA leve, sem SSR necessário |
| Banco | SQLite (existente) | — | Leitura direta, sem migração |
| Servir imagens | FastAPI endpoint `/images` | — | Controle de path traversal |
| Exportação PDF | WeasyPrint | ≥ 60 | Geração server-side com CSS |
| Exportação Excel | openpyxl | ≥ 3.1 | Biblioteca Python consolidada |
| HTTP Client (FE) | Axios ou fetch nativo | — | Chamadas à API local |
| Gráficos | Recharts | ≥ 2.x | Leve, declarativo, React-first |
| Deploy | systemd service | — | Simples, sem Docker adicional |

---

## 3. Estrutura de Pastas

```
lizard-web/
├── api/
│   ├── main.py              ← FastAPI app entry point
│   ├── config.py            ← Configurações (caminhos SQLite, results dir)
│   ├── db.py                ← Conexão e queries SQLite (READ ONLY)
│   ├── routers/
│   │   ├── ops.py           ← /ops, /ops/{id}, /ops/{id}/hides
│   │   ├── hides.py         ← /hides/{id}
│   │   ├── images.py        ← /images/{path}
│   │   └── exports.py       ← /ops/{id}/export/pdf, /ops/{id}/export/xlsx
│   └── models/
│       ├── op.py            ← Pydantic models para OP
│       └── hide.py          ← Pydantic models para couro
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/
│       │   └── client.ts    ← Wrapper Axios/fetch com base URL
│       ├── pages/
│       │   ├── Dashboard.tsx
│       │   ├── OpList.tsx
│       │   ├── OpDetail.tsx
│       │   └── HideDetail.tsx
│       ├── components/
│       │   ├── charts/
│       │   │   └── ClassDistributionChart.tsx
│       │   ├── tables/
│       │   │   ├── OpTable.tsx
│       │   │   └── HideTable.tsx
│       │   └── ui/
│       │       ├── ImageViewer.tsx
│       │       ├── Pagination.tsx
│       │       └── ExportButtons.tsx
│       └── types/
│           ├── op.ts
│           └── hide.ts
│
└── lizard-web.service       ← systemd unit file
```

---

## 4. API — Contratos de Endpoints

### 4.1 Dashboard

```
GET /dashboard
```

**Response:**
```json
{
  "today": {
    "total_hides": 342,
    "avg_yield": 78.4
  },
  "week": {
    "total_hides": 2104,
    "avg_yield": 76.9
  },
  "today_class_distribution": [
    { "class": "A", "count": 120, "pct": 35.1 },
    { "class": "B", "count": 98,  "pct": 28.7 }
  ],
  "recent_ops": [
    { "op": "12345", "date": "2026-06-26", "total_hides": 48 }
  ]
}
```

---

### 4.2 Lista de OPs

```
GET /ops?page=1&limit=20&date_from=2026-06-01&date_to=2026-06-26&class=A&search=12345
```

**Response:**
```json
{
  "items": [
    {
      "op": "12345",
      "last_updated": "2026-06-26T14:32:00",
      "total_hides": 48,
      "avg_yield": 79.2,
      "predominant_class": "A"
    }
  ],
  "total": 142,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

---

### 4.3 Detalhe da OP

```
GET /ops/{op_id}
```

**Response:**
```json
{
  "op": "12345",
  "total_hides": 48,
  "avg_area": 4.32,
  "avg_yield": 79.2,
  "class_distribution": [
    { "class": "A", "count": 28, "pct": 58.3 },
    { "class": "B", "count": 20, "pct": 41.7 }
  ]
}
```

---

### 4.4 Couros de uma OP

```
GET /ops/{op_id}/hides?page=1&limit=50
```

**Response:**
```json
{
  "items": [
    {
      "id": 1001,
      "hide_num": "H001",
      "processed_at": "2026-06-26T14:32:00",
      "class": "A",
      "yield_pct": 81.2,
      "area": 4.5,
      "op": "12345"
    }
  ],
  "total": 48,
  "page": 1,
  "limit": 50
}
```

---

### 4.5 Detalhe do Couro

```
GET /hides/{hide_id}
```

**Response:**
```json
{
  "id": 1001,
  "hide_num": "H001",
  "op": "12345",
  "processed_at": "2026-06-26T14:32:00",
  "class": "A",
  "yield_pct": 81.2,
  "area": 4.5,
  "image_available": true,
  "prev_hide_id": 1000,
  "next_hide_id": 1002
}
```

---

### 4.6 Imagens

```
GET /images/{encoded_path}
```

- `encoded_path`: path relativo ao diretório `results/`, URL-encoded
- A API valida que o path resolvido está **dentro** do diretório configurado (sem path traversal)
- Retorna `404` com body `{"detail": "Imagem não disponível"}` se arquivo não existir
- Retorna `400` se path traversal detectado

---

### 4.7 Exportações

```
GET /ops/{op_id}/export/pdf
GET /ops/{op_id}/export/xlsx
```

- Geração sob demanda
- Headers: `Content-Disposition: attachment; filename="op-{op_id}.pdf"`
- Sem imagens nos relatórios (v1)

---

## 5. Mapeamento de Dados SQLite → API

| Campo API | Tabela SQLite | Coluna |
|-----------|--------------|--------|
| `op` | — | `GrdOp` |
| `hide_num` | — | `GrdHidNum` |
| `area` | — | `GrdAre` |
| `class` | — | `GrdCla` |
| `yield_pct` | — | `GrdUsaPer` |
| `processed_at` | — | `GrdDat` |
| `result_path` (interno) | — | `GrdResPat` |

**Query base para imagem:**
```sql
SELECT GrdResPat, GrdDat, GrdOp, GrdHidNum, GrdAre
FROM grading_results
WHERE id = ?
```
Path reconstruído: `{GrdResPat}{GrdDat_date}-{GrdDat_time}-{GrdOp}-{GrdHidNum}-{GrdAre}.jpg`

---

## 6. Segurança

| Risco | Mitigação |
|-------|-----------|
| Path traversal em `/images` | Validar que `os.path.realpath(path)` começa com `RESULTS_DIR` configurado |
| Exposição de SQLite | API lê somente; SQLite não é exposto diretamente |
| Acesso externo | Bind na rede local (`0.0.0.0:8000`); sem autenticação v1 (decisão de escopo) |
| Queries injetadas | Uso exclusivo de parameterized queries via `sqlite3` Python |

---

## 7. Epics e Dependências

### Epic 1 — Infraestrutura Base
Objetivo: projeto inicializado, API rodando, SQLite legível, frontend acessível.

**Dependências:** nenhuma — deve ser o primeiro epic.

### Epic 2 — Backend API
Objetivo: todos os endpoints implementados e testados.

**Dependências:** Epic 1 concluído.

### Epic 3 — Frontend (Telas)
Objetivo: Dashboard, Lista de OPs, Detalhe da OP, Detalhe do Couro funcionando.

**Dependências:** Epic 2 (endpoints disponíveis).

### Epic 4 — Exportação
Objetivo: PDF e Excel gerados corretamente.

**Dependências:** Epic 2 (dados da OP disponíveis via API).

### Epic 5 — Deploy & Systemd
Objetivo: serviço rodando como daemon na esteira, acessível na rede local.

**Dependências:** Epics 1–4 concluídos.

---

## 8. Stories por Epic (referência para @sm)

### Epic 1 — Infraestrutura Base
| Story | Título |
|-------|--------|
| 1.1 | Setup do projeto lizard-web (estrutura de pastas, venv, package.json) |
| 1.2 | Configuração FastAPI com CORS e leitura do SQLite |
| 1.3 | Setup React + Vite com roteamento e layout base |

### Epic 2 — Backend API
| Story | Título |
|-------|--------|
| 2.1 | Endpoint GET /dashboard |
| 2.2 | Endpoint GET /ops (lista paginada com filtros) |
| 2.3 | Endpoint GET /ops/{id} e GET /ops/{id}/hides |
| 2.4 | Endpoint GET /hides/{id} com navegação prev/next |
| 2.5 | Endpoint GET /images/{path} com validação de path |

### Epic 3 — Frontend (Telas)
| Story | Título |
|-------|--------|
| 3.1 | Página Dashboard |
| 3.2 | Página Lista de OPs com filtros e paginação |
| 3.3 | Página Detalhe da OP |
| 3.4 | Página Detalhe do Couro com visualizador de imagem |

### Epic 4 — Exportação
| Story | Título |
|-------|--------|
| 4.1 | Exportação PDF da OP |
| 4.2 | Exportação Excel da OP |

### Epic 5 — Deploy
| Story | Título |
|-------|--------|
| 5.1 | Configuração systemd service para API e frontend estático |

---

## 9. Critérios de Aceite Arquiteturais

| # | Critério |
|---|----------|
| A-01 | `lizard-web/` não importa nenhum módulo de `lizard/` |
| A-02 | Toda query ao SQLite usa parameterized statements |
| A-03 | Endpoint `/images` rejeita qualquer path fora de `RESULTS_DIR` |
| A-04 | API responde em < 500ms para qualquer endpoint de lista (rede local) |
| A-05 | Frontend funciona em Chrome e Firefox sem dependências externas (CDN) |
| A-06 | Build do frontend gera arquivos estáticos servidos pela própria API |

---

## 10. Decisões Arquiteturais

| # | Decisão | Alternativa Considerada | Motivo da Escolha |
|---|---------|------------------------|-------------------|
| D-01 | FastAPI para backend | Flask, Django | Async nativo, tipagem, OpenAPI automático |
| D-02 | React + Vite para frontend | Vue, Svelte | Ecossistema consolidado, Recharts disponível |
| D-03 | SQLite direto (sem ORM) | SQLAlchemy | Leitura simples, sem migrations, overhead mínimo |
| D-04 | WeasyPrint para PDF | reportlab | CSS-based, mais simples de estilizar |
| D-05 | Systemd para deploy | Docker, PM2 | Sem dependência adicional na esteira |
| D-06 | Frontend servido pela FastAPI | Nginx separado | Instalação única, menos configuração |

---

*Lizard Web System Architecture v1.0 — @architect (Aria) — 2026-06-26*
