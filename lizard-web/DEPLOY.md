# Deploy — Lizard Web

Instruções para instalar o Lizard Web como serviço systemd na esteira de produção.

---

## Pré-requisitos

| Requisito | Versão mínima |
|-----------|--------------|
| Sistema operacional | Linux com systemd (Ubuntu 20.04+ / Debian 11+) |
| Python | 3.10+ |
| Node.js | 18+ |
| Acesso | `sudo` na esteira |

---

## Estrutura esperada em produção

```
/opt/lizard-web/
├── api/
│   ├── .venv/          ← virtualenv Python
│   ├── main.py
│   ├── requirements.txt
│   └── routers/
├── frontend/
│   └── dist/           ← build gerado por `npm run build`
└── lizard-web.service  ← copiado para /etc/systemd/system/
```

O banco SQLite e o diretório de resultados ficam **fora** do projeto:

```
/opt/lizard/
├── data/
│   └── results.db      ← SQLITE_PATH
└── results/            ← RESULTS_DIR
```

> Ajuste os caminhos acima conforme a instalação real na esteira.

---

## Usuário do serviço

O unit file usa `User=lizard`. Você pode:

**Opção A — criar usuário dedicado (recomendado):**
```bash
sudo useradd --system --no-create-home --shell /bin/false lizard
sudo chown -R lizard:lizard /opt/lizard-web /opt/lizard
```

**Opção B — usar o usuário existente da esteira:**
Edite `lizard-web.service` e substitua `User=lizard` pelo usuário real antes de instalar.

---

## Passos de instalação

### 1. Copiar o código para a esteira

```bash
sudo mkdir -p /opt/lizard-web
sudo cp -r lizard-web/. /opt/lizard-web/
```

### 2. Configurar variáveis de ambiente no unit file

Edite `/opt/lizard-web/lizard-web.service` e ajuste:

```ini
User=lizard                              # usuário que executará o serviço
WorkingDirectory=/opt/lizard-web         # caminho do projeto na esteira
Environment="SQLITE_PATH=/opt/lizard/data/results.db"
Environment="RESULTS_DIR=/opt/lizard/results"
ExecStart=/opt/lizard-web/api/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 3. Instalar dependências da API

```bash
cd /opt/lizard-web/api
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
```

### 4. Build do frontend

```bash
cd /opt/lizard-web/frontend
npm install
npm run build
# Gera frontend/dist/ — servido automaticamente pela API
```

### 5. Instalar e ativar o serviço

```bash
sudo cp /opt/lizard-web/lizard-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable lizard-web
sudo systemctl start lizard-web
```

### 6. Verificar

```bash
systemctl status lizard-web
# Esperado: Active: active (running)

# Testar localmente:
curl http://localhost:8000/health
# Esperado: {"status":"ok","db_ok":true}
```

O portal estará acessível em qualquer máquina da rede local via:
```
http://<ip-da-esteira>:8000
```

---

## Atualização do sistema

```bash
# 1. Parar o serviço
sudo systemctl stop lizard-web

# 2. Atualizar o código
cd /opt/lizard-web
sudo git pull   # ou copiar arquivos manualmente

# 3. Atualizar dependências (se requirements.txt mudou)
cd api && .venv/bin/pip install -r requirements.txt && cd ..

# 4. Rebuild do frontend (se o frontend mudou)
cd frontend && npm install && npm run build && cd ..

# 5. Reiniciar o serviço
sudo systemctl start lizard-web
systemctl status lizard-web
```

---

## Comandos úteis

```bash
# Ver logs em tempo real
sudo journalctl -u lizard-web -f

# Ver últimas 100 linhas de log
sudo journalctl -u lizard-web -n 100

# Reiniciar manualmente
sudo systemctl restart lizard-web

# Desativar inicialização automática
sudo systemctl disable lizard-web
```

---

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---------|---------------|---------|
| `Active: failed` | Erro no ExecStart | Ver `journalctl -u lizard-web -n 50` |
| `db_ok: false` | SQLITE_PATH incorreto | Verificar path e permissões |
| Frontend não carrega | `npm run build` não executado | Rodar passo 4 novamente |
| Porta 8000 em uso | Outro processo na porta | `sudo ss -tlnp \| grep 8000` |
| `Permission denied` | Usuário sem acesso aos arquivos | Verificar `chown` do passo de usuário |
