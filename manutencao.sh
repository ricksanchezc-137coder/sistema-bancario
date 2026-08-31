#!/bin/bash
# manutencao.sh - Script de manutenção do sistema-bancario
# Currículo 13 - Módulo 15 (Encerramento)

# --- Configuração (Módulo 1: variáveis com valor padrão) ---
PROJETO_DIR="$(pwd)"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backup}"
LOG_FILE="$PROJETO_DIR/manutencao.log"
DATA=$(date +%Y%m%d-%H%M%S)

# Lista de exclusões (Módulo 7: arrays)
EXCLUSOES=(".venv" "__pycache__" ".pytest_cache" "htmlcov" ".git")

# --- Trava contra execução duplicada (Módulo 4: processos) ---
if pgrep -f "bash.*manutencao.sh" | grep -vw "$$" > /dev/null; then
    echo "Já existe uma instância rodando. Abortando." | tee -a "$LOG_FILE"
    exit 1
fi

# --- Funções (Módulo 7: scripting em bash) ---
fazer_backup() {
    echo "== Backup ==" | tee -a "$LOG_FILE"
    mkdir -p "$BACKUP_DIR"
    local args=()
    for item in "${EXCLUSOES[@]}"; do
        args+=(--exclude="$item")
    done
    if tar -czf "$BACKUP_DIR/sistema-bancario-$DATA.tar.gz" "${args[@]}" -C "$PROJETO_DIR" . >> "$LOG_FILE" 2>&1; then
        echo "Backup OK: $BACKUP_DIR/sistema-bancario-$DATA.tar.gz" | tee -a "$LOG_FILE"
    else
        echo "Backup FALHOU, veja $LOG_FILE" | tee -a "$LOG_FILE"
    fi
}

limpar_cache() {
    echo "== Limpeza de cache ==" | tee -a "$LOG_FILE"
    find "$PROJETO_DIR" -type d -name "__pycache__" -not -path "*/.venv/*" -print0 \
        | xargs -0 -r rm -rf
    echo "Cache limpo." | tee -a "$LOG_FILE"
}

rodar_testes() {
    echo "== Testes ==" | tee -a "$LOG_FILE"
    source "$PROJETO_DIR/.venv/bin/activate"
    resultado=$(pytest 2>&1)
    echo "$resultado" >> "$LOG_FILE"
    # Módulo 5: grep pra extrair só a linha-resumo do pytest
    resumo=$(echo "$resultado" | grep -E "passed|failed|error" | tail -1)
    echo "Resumo dos testes: $resumo" | tee -a "$LOG_FILE"
    deactivate
}

# --- Execução ---
echo "Manutenção iniciada em $(date)" | tee -a "$LOG_FILE"
fazer_backup
limpar_cache
rodar_testes
echo "Manutenção concluída." | tee -a "$LOG_FILE"
