#!/usr/bin/env bash
# install.sh — Instalação automatizada do Lizard Web como serviço systemd
#
# Uso: sudo bash install.sh [--user <usuario>] [--sqlite-path <path>] [--results-dir <path>]
#
# Padrões:
#   --user         lizard
#   --sqlite-path  /opt/lizard/data/results.db
#   --results-dir  /opt/lizard/results
#   --install-dir  /opt/lizard-web (diretório de origem = diretório deste script)

set -euo pipefail

# ── Defaults ──────────────────────────────────────────────────────────────────
INSTALL_DIR="/opt/lizard-web"
SERVICE_USER="lizard"
SQLITE_PATH="/opt/lizard/data/results.db"
RESULTS_DIR="/opt/lizard/results"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Parse args ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --user)        SERVICE_USER="$2"; shift 2 ;;
    --sqlite-path) SQLITE_PATH="$2";  shift 2 ;;
    --results-dir) RESULTS_DIR="$2";  shift 2 ;;
    --install-dir) INSTALL_DIR="$2";  shift 2 ;;
    *) echo "Opção desconhecida: $1"; exit 1 ;;
  esac
done

# ── Verificações ──────────────────────────────────────────────────────────────
if [[ "$EUID" -ne 0 ]]; then
  echo "Erro: execute com sudo." >&2
  exit 1
fi

command -v python3 >/dev/null || { echo "Erro: python3 não encontrado."; exit 1; }
command -v node   >/dev/null || { echo "Erro: node não encontrado.";    exit 1; }
command -v npm    >/dev/null || { echo "Erro: npm não encontrado.";     exit 1; }

echo "=== Lizard Web — Instalação ==="
echo "Diretório de instalação : $INSTALL_DIR"
echo "Usuário do serviço      : $SERVICE_USER"
echo "SQLITE_PATH             : $SQLITE_PATH"
echo "RESULTS_DIR             : $RESULTS_DIR"
echo ""

# ── Usuário do serviço ────────────────────────────────────────────────────────
if ! id "$SERVICE_USER" &>/dev/null; then
  echo "[1/7] Criando usuário $SERVICE_USER..."
  useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
else
  echo "[1/7] Usuário $SERVICE_USER já existe."
fi

# ── Copiar arquivos ───────────────────────────────────────────────────────────
echo "[2/7] Copiando arquivos para $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/." "$INSTALL_DIR/"

# ── Dependências Python ───────────────────────────────────────────────────────
echo "[3/7] Instalando dependências Python..."
cd "$INSTALL_DIR/api"
python3 -m venv .venv
.venv/bin/pip install --quiet --upgrade pip
.venv/bin/pip install --quiet -r requirements.txt

# ── Build do frontend ─────────────────────────────────────────────────────────
echo "[4/7] Executando build do frontend..."
cd "$INSTALL_DIR/frontend"
npm install --silent
npm run build

# ── Permissões ────────────────────────────────────────────────────────────────
echo "[5/7] Ajustando permissões..."
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# ── Unit file ─────────────────────────────────────────────────────────────────
echo "[6/7] Configurando serviço systemd..."
SERVICE_FILE="/etc/systemd/system/lizard-web.service"

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Lizard Web — Portal de Consulta de Couros
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment="SQLITE_PATH=$SQLITE_PATH"
Environment="RESULTS_DIR=$RESULTS_DIR"
ExecStart=$INSTALL_DIR/api/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lizard-web
systemctl restart lizard-web

# ── Verificação ───────────────────────────────────────────────────────────────
echo "[7/7] Verificando serviço..."
sleep 3
systemctl is-active --quiet lizard-web \
  && echo "" \
  && echo "✓ Serviço lizard-web ativo e rodando." \
  && echo "  Acesse: http://$(hostname -I | awk '{print $1}'):8000" \
  || { echo "✗ Falha ao iniciar. Ver: journalctl -u lizard-web -n 50"; exit 1; }
