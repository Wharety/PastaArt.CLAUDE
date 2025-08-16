from flask import Flask, url_for, request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from models import db, Admin, Configuracao
from blueprints.admin import admin_bp
from blueprints.loja import loja_bp
from blueprints.configuracoes import configuracoes_bp
from blueprints.usuarios import usuarios_bp
from werkzeug.security import generate_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os
import pymysql
from colorama import Fore, Style
# from init_config import init_config
from datetime import datetime
from dotenv import load_dotenv

# Instalar PyMySQL como substituto do MySQLdb
pymysql.install_as_MySQLdb()

# Carregar variáveis de ambiente
load_dotenv()

csrf = CSRFProtect()

def debug_log(message, level="INFO"):
    """Log colorido para debug"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "ADMIN": Fore.MAGENTA
    }
    color = colors.get(level, Fore.WHITE)
    print(f"{Fore.WHITE}[{timestamp}]{color} {level}: {message}{Style.RESET_ALL}")

def create_app():
    """Criar e configurar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'pasta-art-encanto-secret-key-2025')
    # Versão de assets para cache busting (definível por variável de ambiente)
    # Inclui microsegundos para garantir mudança a cada restart em dev
    asset_version = (
        os.getenv('ASSET_VERSION')
        or os.getenv('RELEASE')
        or datetime.now().strftime('%Y%m%d%H%M%S%f')[:16]  # YYYYMMDDHHMMSSFF
    )
    app.config['ASSET_VERSION'] = asset_version
    debug_log(f"🔄 Cache busting ativo: ASSET_VERSION={asset_version}", "INFO")
    # Cache padrão de arquivos estáticos (1 ano)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000
    
    # Detectar ambiente de produção (LocalWeb/hospedagem compartilhada)
    is_production = os.getenv('FLASK_ENV') == 'production' or 'public_html' in os.getcwd()
    
    # Configuração do banco de dados
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '3306')
    db_name = os.getenv('DB_NAME', 'pasta_art')
    db_user = os.getenv('DB_USER', 'pasta_art_user')
    db_password = os.getenv('DB_PASSWORD', '')
    
    # Verificar se as variáveis do MySQL estão configuradas
    if not db_password:
        # Em desenvolvimento/teste, usar SQLite
        debug_log("⚠️ Usando SQLite para desenvolvimento/teste", "WARNING")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pasta_art.db'
    else:
        if is_production:
            debug_log(f"🚀 PRODUÇÃO: Conectando ao MySQL: {db_host}:{db_port}/{db_name}", "SUCCESS")
        else:
            debug_log(f"🔗 Conectando ao MySQL: {db_host}:{db_port}/{db_name}", "INFO")
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configurações específicas para produção
    if is_production:
        app.config['DEBUG'] = False
        app.config['TESTING'] = False
        # Configurações de upload para hospedagem compartilhada
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
    # Configurações de autenticação social
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID', '')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    # Inicializar extensões
    db.init_app(app)
    csrf.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(loja_bp)
    app.register_blueprint(configuracoes_bp, url_prefix='/admin')
    app.register_blueprint(usuarios_bp, url_prefix='/usuario')
    
    # Migração leve: garantir colunas de endereço no MySQL
    def ensure_usuario_address_columns():
        try:
            engine_name = db.engine.url.get_backend_name()
        except Exception:
            engine_name = ''
        # Apenas para MySQL/MariaDB
        if engine_name not in ('mysql', 'mariadb', 'mysql+pymysql'):
            return
        # Tenta adicionar colunas individualmente. Usa IF NOT EXISTS quando suportado.
        ddls = [
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS cep VARCHAR(9) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS logradouro VARCHAR(150) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS bairro VARCHAR(100) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS cidade VARCHAR(100) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS estado VARCHAR(2) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS numero_endereco VARCHAR(20) NULL",
            "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS complemento_endereco VARCHAR(100) NULL",
        ]
        for ddl in ddls:
            try:
                db.session.execute(text(ddl))
                db.session.commit()
            except SQLAlchemyError as e:
                # Se a variante IF NOT EXISTS não for suportada, tenta sem ela e ignora duplicatas
                msg = str(e).lower()
                if 'syntax' in msg or 'if not exists' in msg:
                    try:
                        fallback = ddl.replace(' IF NOT EXISTS', '')
                        db.session.execute(text(fallback))
                        db.session.commit()
                    except SQLAlchemyError as e2:
                        # Ignora erro de coluna duplicada
                        if 'duplicate column' in str(e2).lower() or '1060' in str(e2):
                            db.session.rollback()
                            continue
                        db.session.rollback()
                        raise
                else:
                    # Ignora erro de coluna duplicada
                    if 'duplicate column' in msg or '1060' in msg:
                        db.session.rollback()
                        continue
                    db.session.rollback()
                    raise
    
    # Executar migração leve dentro do app context
    try:
        with app.app_context():
            ensure_usuario_address_columns()
            # Migração leve para schema de KIT
            try:
                engine_name = db.engine.url.get_backend_name()
            except Exception:
                engine_name = ''
            if engine_name in ('mysql', 'mariadb', 'mysql+pymysql'):
                kit_ddls = [
                    "ALTER TABLE doces ADD COLUMN IF NOT EXISTS desconto_percentual DECIMAL(5,2) NULL",
                    "ALTER TABLE doces ADD COLUMN IF NOT EXISTS mais_pedido TINYINT(1) NULL DEFAULT 0",
                    "CREATE TABLE IF NOT EXISTS kit_itens (\n"
                    "  id INT AUTO_INCREMENT PRIMARY KEY,\n"
                    "  kit_id INT NOT NULL,\n"
                    "  produto_id INT NOT NULL,\n"
                    "  quantidade INT NOT NULL DEFAULT 1,\n"
                    "  INDEX (kit_id), INDEX (produto_id),\n"
                    "  CONSTRAINT fk_kit_itens_kit FOREIGN KEY (kit_id) REFERENCES doces(id) ON DELETE CASCADE,\n"
                    "  CONSTRAINT fk_kit_itens_prod FOREIGN KEY (produto_id) REFERENCES doces(id)\n"
                    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"
                ]
                for ddl in kit_ddls:
                    try:
                        db.session.execute(text(ddl))
                        db.session.commit()
                    except SQLAlchemyError as e:
                        msg = str(e).lower()
                        if 'if not exists' in msg or 'syntax' in msg:
                            try:
                                fallback = ddl.replace(' IF NOT EXISTS', '')
                                db.session.execute(text(fallback))
                                db.session.commit()
                            except SQLAlchemyError:
                                db.session.rollback()
                                continue
                        else:
                            db.session.rollback()
                            if 'duplicate' in msg or 'exists' in msg:
                                continue
                            raise
    except Exception as e:
        debug_log(f"Falha ao aplicar migração leve de endereço: {e}", "WARNING")

    # Helper para gerar URLs de assets com versão (cache busting)
    def asset_url(filename: str) -> str:
        return url_for('static', filename=filename, v=app.config.get('ASSET_VERSION', '1'))
    app.jinja_env.globals['asset_url'] = asset_url

    # Cabeçalhos de cache: HTML não é cacheado; estáticos são fortemente cacheados
    @app.after_request
    def add_cache_headers(response):
        try:
            request_path = request.path
        except Exception:
            request_path = ''
        if request_path.startswith('/static/'):
            # Regras específicas por tipo de arquivo
            _, ext = os.path.splitext(request_path.lower())
            if ext in {'.css', '.js'}:
                response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            elif ext in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.ico'}:
                response.headers['Cache-Control'] = 'public, max-age=2592000'
            elif ext in {'.json', '.webmanifest'}:
                response.headers['Cache-Control'] = 'public, max-age=604800'
            else:
                response.headers['Cache-Control'] = 'public, max-age=604800'
        else:
            # Conteúdo HTML sempre revalida - forçar navegador a sempre verificar mudanças
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            # ETag único para cada resposta HTML garante detecção de mudanças
            response.headers['ETag'] = f'"{asset_version}-{datetime.now().timestamp()}"'
        return response

    # Context processor para configurações globais
    @app.context_processor
    def inject_configuracoes():
        """Injetar configurações globais em todos os templates"""
        configs = {}
        try:
            # Buscar configurações do banco
            configuracoes = Configuracao.query.all()
            for config in configuracoes:
                configs[config.chave] = config.valor
        except Exception:
            # Se não conseguir buscar, usar valores padrão
            configs = {
                'site_nome': 'PastaArt Encanto',
                'site_descricao': 'Doces artesanais feitos com muito carinho',
                'telefone': '(11) 99999-9999',
                'email': 'contato@pastaart.com.br',
                'endereco': 'Rua das Flores, 123 - Centro',
                'whatsapp': '5511999999999',
                'facebook_url': '',
                'instagram_url': '',
                'whatsapp_url': '',
                'tiktok_url': '',
                'youtube_url': '',
                'linkedin_url': '',
                'rodape_texto': '© 2025 PastaArt Encanto. Todos os direitos reservados.',
                'site_logo': 'images/logo.svg',
                'site_banner': 'images/banner.webp',
                'card_tradicional_image': 'images/doces_tradicionais.png',
                'card_personalizado_image': 'images/doces_personalizados.png',
                'tradicional_title': 'Doces Tradicionais',
                'tradicional_description': 'Nossos doces clássicos, feitos com receitas tradicionais e ingredientes selecionados.',
                'personalizado_title': 'Doces Personalizados',
                'personalizado_description': 'Doces únicos e personalizados para seus eventos especiais.',
                'about_title': 'Sobre a PastaArt Encanto',
                'about_description': 'Somos especialistas em criar doces únicos e personalizados que transformam seus momentos especiais em memórias inesquecíveis.',

                'produtos_titulo': 'Nossos Doces',
                'produtos_subtitulo': 'Escolha a categoria que melhor atende suas necessidades',
                'checkout_titulo': 'Finalizar Pedido',
                'checkout_descricao': 'Seus dados serão utilizados para contato via WhatsApp',
                'checkout_botao_texto': 'Confirmar Pedido',
                'checkout_telefone_obrigatorio': 'Telefone necessário! Precisamos do seu telefone para entrar em contato via WhatsApp.',
                'pedido_sucesso_titulo': 'Pedido Enviado com Sucesso!',
                'pedido_sucesso_subtitulo': 'Olá {nome}, seu pedido foi enviado para nosso WhatsApp',
                'pedido_tempo_resposta': '1 hora',
                'pedido_whatsapp_texto': 'Abrir WhatsApp',
                'dashboard_titulo': 'Dashboard',
                'dashboard_subtitulo': 'Visão geral da sua loja',
                'dashboard_total_produtos': 'Total de Produtos',
                'dashboard_produtos_ativos': 'Produtos Ativos',
                'dashboard_produtos_inativos': 'Produtos Inativos',
                'dashboard_pedidos_hoje': 'Pedidos Hoje',
                'dashboard_pedidos_pendentes': 'pendentes',
                'dashboard_novo_produto_titulo': 'Novo Produto',
                'dashboard_novo_produto_descricao': 'Adicionar um novo doce ao catálogo',
                'dashboard_gerenciar_produtos_titulo': 'Gerenciar Produtos',
                'dashboard_gerenciar_produtos_descricao': 'Ver e editar produtos existentes',
                'dashboard_ver_pedidos_titulo': 'Ver Pedidos',
                'dashboard_ver_pedidos_descricao': 'Gerenciar todos os pedidos da loja',
                'dashboard_ver_loja_titulo': 'Ver Loja',
                'dashboard_ver_loja_descricao': 'Visualizar como os clientes veem sua loja',
                'dashboard_pedidos_recentes_titulo': 'Pedidos Recentes',
                'dashboard_produtos_recentes_titulo': 'Produtos Recentes',
                'dashboard_ver_todos': 'Ver Todos',
                'dashboard_ver_detalhes': 'Ver Detalhes',
                'dashboard_editar': 'Editar',
                'dashboard_mais': 'mais',
                'admin_produtos_titulo': 'Produtos',
                'admin_produtos_subtitulo': 'Gerencie todos os doces da sua loja',
                'admin_novo_produto': 'Novo Produto',
                'admin_lista_produtos': 'Lista de Produtos',
                'admin_todos_status': 'Todos os Status',
                'admin_apenas_ativos': 'Apenas Ativos',
                'admin_apenas_inativos': 'Apenas Inativos',
                'admin_coluna_imagem': 'Imagem',
                'admin_coluna_nome': 'Nome',
                'admin_coluna_preco': 'Preço',
                'admin_coluna_sabores': 'Sabores',
                'admin_coluna_qtd_min': 'Qtd. Mín.',
                'admin_coluna_estoque': 'Estoque',
                'admin_coluna_status': 'Status',
                'admin_coluna_data': 'Data',
                'admin_coluna_acoes': 'Ações',
                'admin_editar': 'Editar',
                'admin_excluir': 'Excluir',
                'admin_confirmar_exclusao': 'Tem certeza que deseja excluir o produto',
                'admin_nao_pode_excluir': 'Não é possível excluir este produto',
                'admin_form_info_basicas': 'Informações Básicas',
                'admin_form_nome_produto': 'Nome do Produto',
                'admin_form_descricao': 'Descrição',
                'admin_form_placeholder_nome': 'Ex: Brigadeiro Gourmet de Chocolate',
                'admin_form_placeholder_descricao': 'Descreva os sabores, ingredientes e ocasiões especiais...',
                'admin_form_hint_nome': 'Escolha um nome atrativo e descritivo',
                'admin_form_hint_descricao': 'Descreva detalhes que atraiam os clientes'
            }
        
        return {'config': configs}
    
    # Helper function para obter configuração
    def get_config(chave, valor_padrao=''):
        """Obter valor de uma configuração"""
        try:
            config = Configuracao.query.filter_by(chave=chave).first()
            return config.valor if config else valor_padrao
        except Exception:
            return valor_padrao
    
    app.jinja_env.globals['get_config'] = get_config
    
    # Context processor para contagem do carrinho
    @app.context_processor
    def inject_cart_count():
        """Injetar contagem do carrinho em todos os templates"""
        from flask import session
        cart = session.get('cart', {})
        cart_count = sum(item['quantidade'] for item in cart.values())
        return {'cart_count': cart_count}
    
    # Context processor para CSRF token
    @app.context_processor
    def inject_csrf_token():
        """Injetar CSRF token em todos os templates"""
        return dict(csrf_token=generate_csrf)
    
    
    # Rotas SEO: robots.txt e sitemap.xml
    @app.route('/robots.txt')
    def robots_txt():
        lines = [
            'User-agent: *',
            'Allow: /',
            'Disallow: /admin',
            f'Sitemap: {request.url_root.rstrip('/')}/sitemap.xml'
        ]
        from flask import Response
        return Response('\n'.join(lines), mimetype='text/plain; charset=utf-8')

    @app.route('/sitemap.xml')
    def sitemap_xml():
        from flask import Response
        from models import Doce
        import xml.etree.ElementTree as ET
        from urllib.parse import urljoin

        urlset = ET.Element('urlset', attrib={
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'
        })

        def add_url(loc: str, changefreq: str = 'weekly'):
            url = ET.SubElement(urlset, 'url')
            ET.SubElement(url, 'loc').text = loc
            ET.SubElement(url, 'changefreq').text = changefreq

        base = request.url_root
        # Rotas estáticas principais
        add_url(urljoin(base, url_for('loja.index')))
        add_url(urljoin(base, url_for('loja.doces_tradicionais')))
        add_url(urljoin(base, url_for('loja.doces_personalizados')))

        # Produtos ativos
        try:
            with app.app_context():
                produtos = Doce.query.filter_by(ativo=True).all()
                for p in produtos:
                    add_url(urljoin(base, url_for('loja.detalhes_doce', doce_id=p.id)), 'weekly')
        except Exception:
            pass

        xml_bytes = ET.tostring(urlset, encoding='utf-8', method='xml')
        return Response(xml_bytes, mimetype='application/xml; charset=utf-8')

    return app

def init_db():
    """Inicializar banco de dados"""
    debug_log("Verificando banco de dados...")
    
    with app.app_context():
        # Criar tabelas apenas se não existirem
        db.create_all()
        
        # Criar admin padrão se não existir
        admin = Admin.query.filter_by(usuario='admin').first()
        if not admin:
            admin = Admin(
                usuario='admin',
                senha_hash=generate_password_hash('pasta123')
            )
            db.session.add(admin)
            db.session.commit()
            debug_log("✅ Admin padrão criado (admin/pasta123)", "SUCCESS")
        
        # Popular com configurações iniciais
        # init_config()  # Comentado pois agora usamos init_config.py separado
        debug_log("✅ Configurações iniciais populadas", "SUCCESS")

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("🍰 PASTAART ENCANTO - Iniciando Aplicação")
    print("=" * 60)
    
    # Inicializar banco
    init_db()
    
    debug_log("✅ Aplicação iniciada com debug colorido!", "SUCCESS")
    debug_log("📱 Loja: http://localhost:5000", "INFO")
    debug_log("🛠️ Admin: http://localhost:5000/admin (admin/pasta123)", "ADMIN")
    debug_log("🔍 Debug mode: ON - Logs coloridos ativados", "INFO")
    print("=" * 60)
    
    app.run(debug=True)
