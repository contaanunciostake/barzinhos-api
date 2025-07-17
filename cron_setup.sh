#!/bin/bash

# Script para configurar tarefas cron para manutenção das assinaturas
# Execute este script para configurar a automação

echo "Configurando tarefas cron para manutenção das assinaturas..."

# Obter o diretório atual
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAINTENANCE_SCRIPT="$SCRIPT_DIR/maintenance.py"

# Verificar se o script de manutenção existe
if [ ! -f "$MAINTENANCE_SCRIPT" ]; then
    echo "Erro: Script de manutenção não encontrado em $MAINTENANCE_SCRIPT"
    exit 1
fi

# Tornar o script executável
chmod +x "$MAINTENANCE_SCRIPT"

# Criar arquivo temporário com as tarefas cron
TEMP_CRON=$(mktemp)

# Adicionar tarefas cron existentes (se houver)
crontab -l 2>/dev/null > "$TEMP_CRON"

# Remover tarefas antigas do barzinhos (se existirem)
sed -i '/# Barzinhos Maintenance/d' "$TEMP_CRON"
sed -i '/maintenance.py/d' "$TEMP_CRON"

# Adicionar novas tarefas cron
cat >> "$TEMP_CRON" << EOF

# Barzinhos Maintenance - Verificar assinaturas expiradas a cada hora
0 * * * * cd $SCRIPT_DIR && python3 maintenance.py check-expired >> maintenance.log 2>&1

# Barzinhos Maintenance - Enviar notificações de expiração diariamente às 9h
0 9 * * * cd $SCRIPT_DIR && python3 maintenance.py notify-expiring >> maintenance.log 2>&1

# Barzinhos Maintenance - Manutenção completa diariamente às 2h
0 2 * * * cd $SCRIPT_DIR && python3 maintenance.py full-maintenance >> maintenance.log 2>&1

EOF

# Instalar o novo crontab
crontab "$TEMP_CRON"

# Limpar arquivo temporário
rm "$TEMP_CRON"

echo "✓ Tarefas cron configuradas com sucesso!"
echo ""
echo "Tarefas configuradas:"
echo "  - Verificação de assinaturas expiradas: a cada hora"
echo "  - Notificações de expiração: diariamente às 9h"
echo "  - Manutenção completa: diariamente às 2h"
echo ""
echo "Para verificar as tarefas instaladas, execute: crontab -l"
echo "Para remover as tarefas, execute: crontab -e e remova as linhas do Barzinhos"
echo ""
echo "Logs serão salvos em: $SCRIPT_DIR/maintenance.log"

