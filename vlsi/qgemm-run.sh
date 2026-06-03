#!/usr/bin/env bash
set -euo pipefail

# Ação padrão
ACTION="syn"

# Pega a ação se o primeiro argumento não tiver '='
if [ $# -gt 0 ] && [[ "$1" != *"="* ]]; then
  ACTION="$1"
  shift
fi

# Define a tecnologia padrão
TECH="sky130"

# Array para guardar os argumentos que vão ser repassados para o make
MAKE_ARGS=()

# Vasculha os argumentos restantes
for arg in "$@"; do
  if [[ "$arg" == TECH=* ]]; then
    TECH="${arg#*=}"
  else
    MAKE_ARGS+=("$arg")
  fi
done

# Configura os arquivos YML e o executável baseados na tecnologia escolhida
if [[ "$TECH" == "asap7" ]]; then
  CONFS_DEFAULT="qgemm-tools.yml qgemm-asap7.yml"
elif [[ "$TECH" == "sky130" ]]; then
  CONFS_DEFAULT="qgemm-tools.yml qgemm-sky130.yml"
else
  echo "Erro: Tecnologia '$TECH' não suportada. Use 'sky130' ou 'asap7'."
  exit 1
fi

# Valores padrão (podem ser sobrescritos por variáveis de ambiente antes do script)
CONFIG="${CONFIG:-GemminiRocketConfig}"
CONFS="${CONFS:-$CONFS_DEFAULT}"
EXEC_NAME="./qgemm-hooks"

# Define o nome da pasta com a tecnologia correta
VLSI_DIR="build-qgemm-${TECH}"

# O "${MAKE_ARGS[@]}" no final repassa os argumentos extras
# A linha HAMMER_EXEC="$EXEC_NAME" sobrescreve o Makefile
make "$ACTION" \
  tech_name="$TECH" \
  CONFIG="$CONFIG" \
  VLSI_TOP=Gemmini \
  VLSI_OBJ_DIR="$VLSI_DIR" \
  INPUT_CONFS="$CONFS" \
  HAMMER_EXEC="$EXEC_NAME" \
  "${MAKE_ARGS[@]}"