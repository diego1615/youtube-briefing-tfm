#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DISPLAY_NAME="youtube-briefing-local"
USER_SLUG="$(whoami | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9-' | cut -c1-8)"
DEFAULT_PROJECT_ID="ytbrief-${USER_SLUG}-$(date +%m%d%H%M%S)"
PROJECT_ID="${1:-$DEFAULT_PROJECT_ID}"

if ! command -v gcloud >/dev/null 2>&1; then
  echo "No encontre gcloud."
  echo "Instalalo con: brew install --cask google-cloud-sdk"
  echo "Despues ejecuta: scripts/configure_youtube_cloud.sh"
  exit 1
fi

if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
  echo "No hay una cuenta activa de Google Cloud. Abriendo login..."
  gcloud auth login
fi

if ! gcloud projects describe "$PROJECT_ID" >/dev/null 2>&1; then
  echo "Creando proyecto: $PROJECT_ID"
  gcloud projects create "$PROJECT_ID" --name="YouTube Briefing"
fi

gcloud config set project "$PROJECT_ID" >/dev/null

echo "Habilitando APIs necesarias..."
gcloud services enable \
  serviceusage.googleapis.com \
  apikeys.googleapis.com \
  youtube.googleapis.com \
  --project "$PROJECT_ID"

echo "Creando API key restringida a YouTube Data API..."
gcloud services api-keys create \
  --display-name="$DISPLAY_NAME" \
  --api-target=service=youtube.googleapis.com \
  --project="$PROJECT_ID" \
  --quiet \
  >/dev/null 2>&1

KEY_NAME="$(
  gcloud services api-keys list \
    --project="$PROJECT_ID" \
    --filter="displayName=$DISPLAY_NAME" \
    --sort-by="~createTime" \
    --limit=1 \
    --format="value(name)"
)"

if [ -z "$KEY_NAME" ]; then
  echo "No pude obtener el nombre de la key creada."
  exit 1
fi

KEY_STRING="$(
  gcloud services api-keys get-key-string "$KEY_NAME" \
    --project="$PROJECT_ID" \
    --format="value(keyString)"
)"

if [ -z "$KEY_STRING" ]; then
  echo "No pude obtener el valor de la API key."
  exit 1
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

if grep -q "^YOUTUBE_API_KEY=" ".env"; then
  tmp_file="$(mktemp)"
  sed "s/^YOUTUBE_API_KEY=.*/YOUTUBE_API_KEY=$KEY_STRING/" ".env" > "$tmp_file"
  mv "$tmp_file" ".env"
else
  printf "\nYOUTUBE_API_KEY=%s\n" "$KEY_STRING" >> ".env"
fi

echo "Listo. Proyecto: $PROJECT_ID"
echo "La key quedo guardada en .env."
echo "Ejecuta: .venv/bin/streamlit run app.py"
