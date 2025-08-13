#!/bin/bash

# Script de deploy para o VPS
# Execute este script no VPS para atualizar a aplicação

set -e  # Para em caso de erro

echo "🚀 Iniciando deploy da Pasta Art Encanto..."

# Configurações
PROJECT_DIR="/home/pasta_art/PastaArt.CLAUDE"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="$PROJECT_DIR/backups"

# Criar backup do banco atual
echo "📦 Criando backup do banco de dados..."
mkdir -p "$BACKUP_DIR"
if [ -f "$PROJECT_DIR/instance/pasta_art.db" ]; then
    cp "$PROJECT_DIR/instance/pasta_art.db" "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).db"
fi

# Navegar para o diretório do projeto
cd "$PROJECT_DIR"

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source "$VENV_DIR/bin/activate"

# Fazer pull das últimas alterações
echo "📥 Atualizando código do GitHub..."
git pull origin main

# Instalar/atualizar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verificar se há migrações de banco
echo "🗄️ Verificando banco de dados..."
python3 -c "
from app import create_app
from models import db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Banco de dados atualizado!')
"

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
sudo systemctl restart pasta-art
sudo systemctl status pasta-art --no-pager

# Verificar se os serviços estão rodando
echo "✅ Verificando status dos serviços..."
if sudo systemctl is-active --quiet pasta-art; then
    echo "✅ Serviço pasta-art está rodando!"
else
    echo "❌ Erro: Serviço pasta-art não está rodando!"
    exit 1
fi

if sudo systemctl is-active --quiet nginx; then
    echo "✅ Serviço nginx está rodando!"
else
    echo "❌ Erro: Serviço nginx não está rodando!"
    exit 1
fi

# Testar aplicação
echo "🧪 Testando aplicação..."
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Aplicação respondendo corretamente!"
else
    echo "❌ Erro: Aplicação não está respondendo!"
    exit 1
fi

echo "🎉 Deploy concluído com sucesso!"
echo "🌐 Site disponível em: https://pastaart.com.br"
echo "📊 Admin disponível em: https://pastaart.com.br/admin"
