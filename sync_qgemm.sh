#!/bin/bash

# Certifique-se de executar este script de dentro do diretório pai que contenha chipyard/ e qgemm/
# Para rodar: bash sync_qgemm.sh

echo "Iniciando a transferência de arquivos do qgemm para o chipyard..."

# 1. Copiando arquivos do VLSI
echo ">> Sincronizando YAMLs, scripts e hooks do VLSI..."
cp -v qgemm/vlsi/*.yml chipyard/vlsi/
cp -v qgemm/vlsi/*.sh chipyard/vlsi/
cp -rv qgemm/vlsi/qgemm-hooks chipyard/vlsi/

# 2. Copiando arquivos do Gemmini (Códigos Scala)
echo ">> Sincronizando códigos fonte do Gemmini..."
cp -rv qgemm/generators/gemmini/src/main/scala/gemmini chipyard/generators/gemmini/src/main/scala/
cp -rv qgemm/generators/gemmini/chipyard chipyard/generators/gemmini/

echo "----------------------------------------"
echo "Transferência concluída com sucesso!"