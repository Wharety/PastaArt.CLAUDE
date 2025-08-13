# 🍰 Pasta Art Encanto

Sistema de e-commerce para confeitaria especializada em doces personalizados.

## 🚀 Características

- **Loja Online**: Catálogo de produtos com carrinho de compras
- **Doces Tradicionais**: Produtos prontos para consumo
- **Doces Personalizados**: Encomendas sob medida para eventos
- **Painel Administrativo**: Gerenciamento completo de produtos e pedidos
- **Sistema de Usuários**: Cadastro e login de clientes
- **Design Responsivo**: Funciona em desktop e mobile

## 🛠️ Tecnologias

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Banco de Dados**: SQLite/MySQL
- **Servidor**: Gunicorn + Nginx
- **Deploy**: VPS Linux

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- pip
- virtualenv

### Passos

1. **Clonar o repositório**
   ```bash
   git clone https://github.com/seu-usuario/PastaArt.CLAUDE.git
   cd PastaArt.CLAUDE
   ```

2. **Criar ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar banco de dados**
   ```bash
   python init_db.py
   ```

5. **Executar aplicação**
   ```bash
   python app.py
   ```

## 🌐 Deploy

### VPS Setup

1. **Configurar servidor**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip nginx
   ```

2. **Clonar projeto**
   ```bash
   git clone https://github.com/seu-usuario/PastaArt.CLAUDE.git
   cd PastaArt.CLAUDE
   ```

3. **Instalar dependências**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Configurar serviços**
   ```bash
   sudo systemctl enable pasta-art
   sudo systemctl start pasta-art
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

## 📁 Estrutura do Projeto

```
PastaArt.CLAUDE/
├── app.py                 # Aplicação principal
├── models.py              # Modelos do banco de dados
├── requirements.txt       # Dependências Python
├── blueprints/           # Módulos da aplicação
│   ├── admin.py         # Painel administrativo
│   ├── loja.py          # Loja online
│   └── usuarios.py      # Sistema de usuários
├── templates/           # Templates HTML
│   ├── admin/          # Templates do admin
│   ├── loja/           # Templates da loja
│   └── usuarios/       # Templates de usuários
├── static/             # Arquivos estáticos
│   ├── css/           # Estilos CSS
│   ├── js/            # JavaScript
│   └── images/        # Imagens
└── instance/          # Configurações locais
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
FLASK_ENV=production
SECRET_KEY=sua-chave-secreta-aqui
DATABASE_URL=sqlite:///pasta_art.db
```

### Banco de Dados

O sistema suporta SQLite (desenvolvimento) e MySQL (produção).

## 📊 Funcionalidades

### Para Clientes
- ✅ Navegação por categorias
- ✅ Carrinho de compras
- ✅ Sistema de pedidos
- ✅ Cadastro e login
- ✅ Acompanhamento de pedidos

### Para Administradores
- ✅ Gestão de produtos
- ✅ Controle de pedidos
- ✅ Configurações do site
- ✅ Relatórios básicos

## 🚀 Deploy Automático

### GitHub Actions

O projeto inclui workflow para deploy automático:

1. Push para `main` branch
2. GitHub Actions executa testes
3. Deploy automático no VPS
4. Reinicialização dos serviços

## 📞 Suporte

- **Email**: contato@pastaart.com.br
- **WhatsApp**: (66) 99934-8738
- **Site**: https://pastaart.com.br

## 📄 Licença

Este projeto é privado e proprietário da Pasta Art Encanto.

---

**Desenvolvido com ❤️ para a Pasta Art Encanto**
