#!/bin/bash
# Script para restaurar a versão v1 funcional do SoulNutri
# Usar em caso de problemas após alterações

CHECKPOINT_DIR="/app/checkpoints/v1_funcional_20260128_113435"

echo "🔄 Restaurando SoulNutri para versão v1 funcional..."

# Restaurar índice de embeddings
cp "$CHECKPOINT_DIR/dish_index.json" /app/datasets/
cp "$CHECKPOINT_DIR/dish_index_embeddings.npy" /app/datasets/
echo "✅ Índice de embeddings restaurado (492 pratos)"

# Restaurar backend
cp "$CHECKPOINT_DIR/local_dish_updater.py" /app/backend/services/
cp "$CHECKPOINT_DIR/server.py" /app/backend/
echo "✅ Backend restaurado"

# Restaurar frontend
cp "$CHECKPOINT_DIR/Admin.js" /app/frontend/src/
cp "$CHECKPOINT_DIR/Admin.css" /app/frontend/src/
cp "$CHECKPOINT_DIR/App.js" /app/frontend/src/
echo "✅ Frontend restaurado"

# Reiniciar serviços
sudo supervisorctl restart backend frontend
echo "✅ Serviços reiniciados"

echo ""
echo "🎉 Restauração completa! Sistema voltou para estado funcional."
echo "   - 492 pratos indexados"
echo "   - 85.9% saúde dos dados"
echo "   - Reconhecimento visual funcionando"
