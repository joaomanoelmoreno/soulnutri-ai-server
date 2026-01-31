#!/bin/bash
# SoulNutri - Atualização automática do dataset a cada 10 minutos
# Para parar: kill $(cat /tmp/soulnutri_reindex.pid)

API_URL="https://nutrivision-41.preview.emergentagent.com"
LOG_FILE="/tmp/soulnutri_reindex.log"

echo "$$" > /tmp/soulnutri_reindex.pid
echo "[$(date)] Iniciando atualização automática a cada 10 min..." >> $LOG_FILE

while true; do
    echo "[$(date)] Executando reindex..." >> $LOG_FILE
    
    RESULT=$(curl -s -X POST "$API_URL/api/ai/reindex?max_per_dish=10" --max-time 300 2>/dev/null)
    
    DISHES=$(echo $RESULT | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_dishes',0))" 2>/dev/null)
    IMAGES=$(echo $RESULT | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_images',0))" 2>/dev/null)
    
    echo "[$(date)] ✅ Atualizado: $DISHES pratos, $IMAGES imagens" >> $LOG_FILE
    
    sleep 600  # 10 minutos
done
