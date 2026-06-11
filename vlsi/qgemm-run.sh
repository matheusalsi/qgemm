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
TECH="asap7"

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

# Configura os arquivos YML baseados na tecnologia escolhida
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

# -----------------------------------------------------------------------------
# Memórias do Gemmini que devem ir para flip-flops via --force-synflops.
# O accumulator (mem_0_ext) é 1R1W (multiport) e o sky130/sram22 só tem macros
# single-port, então ele NÃO mapeia e precisa ser flopado. Se o MacroCompiler
# reclamar de outra memória (ex.: "mem_1_ext"), é só adicionar aqui:
#   FORCE_SYNFLOPS_MEMS="mem_0_ext mem_1_ext" ./script.sh syn
FORCE_SYNFLOPS_MEMS="${FORCE_SYNFLOPS_MEMS:-mem_0_ext}"

# Monta os flags "--force-synflops <mem>" para cada memória listada
FORCE_FLAGS=""
for m in $FORCE_SYNFLOPS_MEMS; do
  FORCE_FLAGS+=" --force-synflops $m"
done

# Só sobrescreve o modo do MacroCompiler se o usuário não tiver passado o seu
USER_SET_MACRO_MODE=0
if [ ${#MAKE_ARGS[@]} -gt 0 ]; then
  for a in "${MAKE_ARGS[@]}"; do
    [[ "$a" == TOP_MACROCOMPILER_MODE=* ]] && USER_SET_MACRO_MODE=1
  done
fi

# No sky130, força o accumulator para flops e mantém o resto mapeando em SRAM real.
# Os $(SMEMS_CACHE)/$(SMEMS_HAMMER) são expandidos pelo PRÓPRIO make (variáveis de
# linha de comando são expandidas recursivamente), então reaproveitamos os paths
# corretos sem hardcodar nada. As barras invertidas impedem o bash de tocá-los.
if [[ "$TECH" == "sky130" && "$USER_SET_MACRO_MODE" -eq 0 ]]; then
  MAKE_ARGS+=("TOP_MACROCOMPILER_MODE=-l \$(SMEMS_CACHE) -hir \$(SMEMS_HAMMER) --mode strict${FORCE_FLAGS}")
fi

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