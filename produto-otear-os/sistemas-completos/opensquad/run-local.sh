#!/bin/bash
# ============================================================
# run-local.sh — Roda o pipeline de carrossel direto do terminal
# Uso: ./run-local.sh "tema do carrossel" [periodo] [modelo]
#
# Exemplos:
#   ./run-local.sh "IA e Agentes"
#   ./run-local.sh "Automacao" "Ultimos 3 dias" claude-haiku-4-5-20251001
#   ./run-local.sh "Empreendedorismo" "Ultimas 24h" claude-opus-4-6
# ============================================================

TOPIC="${1:-IA e Agentes}"
PERIOD_RAW="${2:-Ultimas 24h}"
MODEL="${3:-claude-haiku-4-5-20251001}"

# Normaliza periodo
case "$PERIOD_RAW" in
  *"3 dias"*|*"3dias"*|B) PERIOD="Últimos 3 dias" ;;
  *"semana"*|C)           PERIOD="Última semana" ;;
  *)                      PERIOD="Últimas 24 horas" ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║     O Tear Carrosseis — Local Run      ║"
echo "╠════════════════════════════════════════╣"
printf "║  Tema:    %-30s║\n" "$TOPIC"
printf "║  Período: %-30s║\n" "$PERIOD"
printf "║  Modelo:  %-30s║\n" "$MODEL"
echo "╚════════════════════════════════════════╝"
echo ""

PROMPT="Execute /opensquad run noticias-carrossel-ia

RESPOSTAS PRE-DEFINIDAS PARA OS CHECKPOINTS (responda automaticamente sem pedir confirmacao ao usuario):

Checkpoint 1 - \"Foco do Dia\":
- Tema: opção 4 (Notícia específica) — o tema é: \"${TOPIC}\"
- Período: ${PERIOD}

Checkpoint 2 - \"Estrategia de Imagens\":
- Imagens: opção 1 (Sem imagens, apenas texto por enquanto)

Checkpoint 3 - \"Aprovação Final\":
- Escolha: opção 3 (Salvar sem publicar)

Execute o pipeline completo do início ao fim usando essas respostas. Nao pause para pedir confirmação."

claude \
  -p "$PROMPT" \
  --model "$MODEL" \
  --dangerously-skip-permissions \
  --output-format text \
  --verbose

echo ""
echo "✓ Pipeline concluído. Slides em: squads/noticias-carrossel-ia/output/"
