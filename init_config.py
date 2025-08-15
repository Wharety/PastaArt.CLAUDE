#!/usr/bin/env python3
"""
Script para inicializar as configurações padrão do site
"""

from app import app, db
from models import Configuracao
from datetime import datetime

def init_configuracoes():
    """Inicializa as configurações padrão do site"""
    
    configs_padrao = [
        # Configurações Básicas do Site
        {
            'chave': 'site_nome',
            'valor': 'PastaArt Encanto',
            'descricao': 'Nome do site',
            'tipo': 'texto',
            'categoria': 'site_basico'
        },
        {
            'chave': 'site_descricao',
            'valor': 'Doces personalizados feitos com muito carinho e qualidade para tornar seus momentos ainda mais especiais.',
            'descricao': 'Descrição do site (usada em meta tags)',
            'tipo': 'textarea',
            'categoria': 'site_basico'
        },
        {
            'chave': 'rodape_texto',
            'valor': '© 2024 PastaArt Encanto. Todos os direitos reservados.',
            'descricao': 'Texto do rodapé',
            'tipo': 'texto',
            'categoria': 'site_basico'
        },
        
        # Configurações de Contato
        {
            'chave': 'telefone',
            'valor': '(11) 99999-9999',
            'descricao': 'Telefone principal',
            'tipo': 'texto',
            'categoria': 'contato'
        },
        {
            'chave': 'email',
            'valor': 'contato@pastaartencanto.com',
            'descricao': 'Email de contato',
            'tipo': 'email',
            'categoria': 'contato'
        },
        {
            'chave': 'endereco',
            'valor': 'Rua das Flores, 123 - Centro, São Paulo - SP',
            'descricao': 'Endereço da empresa',
            'tipo': 'textarea',
            'categoria': 'contato'
        },
        
        # Configurações da Página Inicial
        {
            'chave': 'produtos_titulo',
            'valor': 'Nossos Doces',
            'descricao': 'Título da seção de produtos na página inicial',
            'tipo': 'texto',
            'categoria': 'pagina_inicial'
        },
        {
            'chave': 'produtos_subtitulo',
            'valor': 'Escolha a categoria que melhor atende suas necessidades',
            'descricao': 'Subtítulo da seção de produtos na página inicial',
            'tipo': 'texto',
            'categoria': 'pagina_inicial'
        },
        
        # Features dos Cards de Categoria
        {
            'chave': 'tradicional_feature_1',
            'valor': 'Receitas tradicionais',
            'descricao': 'Primeira feature do card de doces tradicionais',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        {
            'chave': 'tradicional_feature_2',
            'valor': 'Ingredientes naturais',
            'descricao': 'Segunda feature do card de doces tradicionais',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        {
            'chave': 'tradicional_feature_3',
            'valor': 'Pronto para consumo',
            'descricao': 'Terceira feature do card de doces tradicionais',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        {
            'chave': 'personalizado_feature_1',
            'valor': 'Design personalizado',
            'descricao': 'Primeira feature do card de doces personalizados',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        {
            'chave': 'personalizado_feature_2',
            'valor': 'Para eventos especiais',
            'descricao': 'Segunda feature do card de doces personalizados',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        {
            'chave': 'personalizado_feature_3',
            'valor': 'Consultoria gratuita',
            'descricao': 'Terceira feature do card de doces personalizados',
            'tipo': 'texto',
            'categoria': 'category_features'
        },
        
        # Features da Seção Sobre Nós
        {
            'chave': 'about_feature_1',
            'valor': 'Feito com amor',
            'descricao': 'Primeira feature da seção sobre nós',
            'tipo': 'texto',
            'categoria': 'about_features'
        },
        {
            'chave': 'about_feature_2',
            'valor': 'Ingredientes naturais',
            'descricao': 'Segunda feature da seção sobre nós',
            'tipo': 'texto',
            'categoria': 'about_features'
        },
        {
            'chave': 'about_feature_3',
            'valor': 'Personalização total',
            'descricao': 'Terceira feature da seção sobre nós',
            'tipo': 'texto',
            'categoria': 'about_features'
        },
        
        # Configurações do Checkout
        {
            'chave': 'checkout_titulo',
            'valor': 'Finalizar Pedido',
            'descricao': 'Título da página de checkout',
            'tipo': 'texto',
            'categoria': 'checkout'
        },
        {
            'chave': 'checkout_descricao',
            'valor': 'Seus dados serão utilizados para contato via WhatsApp',
            'descricao': 'Descrição da página de checkout',
            'tipo': 'texto',
            'categoria': 'checkout'
        },
        {
            'chave': 'checkout_botao_texto',
            'valor': 'Confirmar Pedido',
            'descricao': 'Texto do botão de finalização do pedido',
            'tipo': 'texto',
            'categoria': 'checkout'
        },
        {
            'chave': 'checkout_telefone_obrigatorio',
            'valor': 'Telefone necessário! Precisamos do seu telefone para entrar em contato via WhatsApp.',
            'descricao': 'Mensagem quando telefone é obrigatório',
            'tipo': 'texto',
            'categoria': 'checkout'
        },
        
        # Configurações da Página de Pedido Finalizado
        {
            'chave': 'pedido_sucesso_titulo',
            'valor': 'Pedido Enviado com Sucesso!',
            'descricao': 'Título da página de pedido finalizado',
            'tipo': 'texto',
            'categoria': 'pedido_finalizado'
        },
        {
            'chave': 'pedido_sucesso_subtitulo',
            'valor': 'Olá {nome}, seu pedido foi enviado para nosso WhatsApp',
            'descricao': 'Subtítulo da página de pedido finalizado',
            'tipo': 'texto',
            'categoria': 'pedido_finalizado'
        },
        {
            'chave': 'pedido_tempo_resposta',
            'valor': '1 hora',
            'descricao': 'Tempo de resposta informado ao cliente',
            'tipo': 'texto',
            'categoria': 'pedido_finalizado'
        },
        {
            'chave': 'pedido_whatsapp_texto',
            'valor': 'Abrir WhatsApp',
            'descricao': 'Texto do botão para abrir WhatsApp',
            'tipo': 'texto',
            'categoria': 'pedido_finalizado'
        },
        
        # Configurações dos Cards de Categoria
        {
            'chave': 'tradicional_title',
            'valor': 'Doces Tradicionais',
            'descricao': 'Título do card de doces tradicionais',
            'tipo': 'texto',
            'categoria': 'category_cards'
        },
        {
            'chave': 'tradicional_description',
            'valor': 'Nossos doces clássicos, feitos com receitas tradicionais e ingredientes selecionados.',
            'descricao': 'Descrição do card de doces tradicionais',
            'tipo': 'textarea',
            'categoria': 'category_cards'
        },
        {
            'chave': 'personalizado_title',
            'valor': 'Doces Personalizados',
            'descricao': 'Título do card de doces personalizados',
            'tipo': 'texto',
            'categoria': 'category_cards'
        },
        {
            'chave': 'personalizado_description',
            'valor': 'Doces únicos e personalizados para seus eventos especiais.',
            'descricao': 'Descrição do card de doces personalizados',
            'tipo': 'textarea',
            'categoria': 'category_cards'
        },
        
        # Configurações do About Content
        {
            'chave': 'about_title',
            'valor': 'Sobre a PastaArt Encanto',
            'descricao': 'Título da seção sobre nós',
            'tipo': 'texto',
            'categoria': 'about_content'
        },
        {
            'chave': 'about_description',
            'valor': 'Somos especialistas em criar doces únicos e personalizados que transformam seus momentos especiais em memórias inesquecíveis.',
            'descricao': 'Descrição da seção sobre nós',
            'tipo': 'textarea',
            'categoria': 'about_content'
        },
        

        
        # Configurações de Redes Sociais
        {
            'chave': 'facebook_url',
            'valor': '',
            'descricao': 'URL do Facebook',
            'tipo': 'url',
            'categoria': 'redes_sociais'
        },
        {
            'chave': 'instagram_url',
            'valor': '',
            'descricao': 'URL do Instagram',
            'tipo': 'url',
            'categoria': 'redes_sociais'
        },
        {
            'chave': 'whatsapp_url',
            'valor': '',
            'descricao': 'Número do WhatsApp',
            'tipo': 'texto',
            'categoria': 'redes_sociais'
        },
        {
            'chave': 'tiktok_url',
            'valor': '',
            'descricao': 'URL do TikTok',
            'tipo': 'url',
            'categoria': 'redes_sociais'
        },
        {
            'chave': 'youtube_url',
            'valor': '',
            'descricao': 'URL do YouTube',
            'tipo': 'url',
            'categoria': 'redes_sociais'
        },
        {
            'chave': 'linkedin_url',
            'valor': '',
            'descricao': 'URL do LinkedIn',
            'tipo': 'url',
            'categoria': 'redes_sociais'
        },
        
        # Configurações Visuais (imagens)
        {
            'chave': 'site_logo',
            'valor': 'images/logo.svg',
            'descricao': 'Logo do site',
            'tipo': 'texto',
            'categoria': 'visual'
        },
        {
            'chave': 'site_banner',
            'valor': 'images/banner.webp',
            'descricao': 'Banner principal do site',
            'tipo': 'texto',
            'categoria': 'visual'
        },
        {
            'chave': 'card_tradicional_image',
            'valor': 'images/doces_tradicionais.png',
            'descricao': 'Imagem do card de doces tradicionais',
            'tipo': 'texto',
            'categoria': 'visual'
        },
                 {
             'chave': 'card_personalizado_image',
             'valor': 'images/doces_personalizados.png',
             'descricao': 'Imagem do card de doces personalizados',
             'tipo': 'texto',
             'categoria': 'visual'
         },
         
         # Configurações do Dashboard
         {
             'chave': 'dashboard_titulo',
             'valor': 'Dashboard',
             'descricao': 'Título da página do dashboard',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_subtitulo',
             'valor': 'Visão geral da sua loja',
             'descricao': 'Subtítulo da página do dashboard',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_total_produtos',
             'valor': 'Total de Produtos',
             'descricao': 'Texto do card de total de produtos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_produtos_ativos',
             'valor': 'Produtos Ativos',
             'descricao': 'Texto do card de produtos ativos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_produtos_inativos',
             'valor': 'Produtos Inativos',
             'descricao': 'Texto do card de produtos inativos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_pedidos_hoje',
             'valor': 'Pedidos Hoje',
             'descricao': 'Texto do card de pedidos hoje',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_pedidos_pendentes',
             'valor': 'pendentes',
             'descricao': 'Texto para pedidos pendentes',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_novo_produto_titulo',
             'valor': 'Novo Produto',
             'descricao': 'Título do card de novo produto',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_novo_produto_descricao',
             'valor': 'Adicionar um novo doce ao catálogo',
             'descricao': 'Descrição do card de novo produto',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_gerenciar_produtos_titulo',
             'valor': 'Gerenciar Produtos',
             'descricao': 'Título do card de gerenciar produtos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_gerenciar_produtos_descricao',
             'valor': 'Ver e editar produtos existentes',
             'descricao': 'Descrição do card de gerenciar produtos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_pedidos_titulo',
             'valor': 'Ver Pedidos',
             'descricao': 'Título do card de ver pedidos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_pedidos_descricao',
             'valor': 'Gerenciar todos os pedidos da loja',
             'descricao': 'Descrição do card de ver pedidos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_loja_titulo',
             'valor': 'Ver Loja',
             'descricao': 'Título do card de ver loja',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_loja_descricao',
             'valor': 'Visualizar como os clientes veem sua loja',
             'descricao': 'Descrição do card de ver loja',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_pedidos_recentes_titulo',
             'valor': 'Pedidos Recentes',
             'descricao': 'Título da seção de pedidos recentes',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_produtos_recentes_titulo',
             'valor': 'Produtos Recentes',
             'descricao': 'Título da seção de produtos recentes',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_todos',
             'valor': 'Ver Todos',
             'descricao': 'Texto do botão ver todos',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_ver_detalhes',
             'valor': 'Ver Detalhes',
             'descricao': 'Texto do botão ver detalhes',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_editar',
             'valor': 'Editar',
             'descricao': 'Texto do botão editar',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         {
             'chave': 'dashboard_mais',
             'valor': 'mais',
             'descricao': 'Texto para indicar mais itens',
             'tipo': 'texto',
             'categoria': 'dashboard'
         },
         
         # Configurações do Admin
         {
             'chave': 'admin_produtos_titulo',
             'valor': 'Produtos',
             'descricao': 'Título da página de produtos',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_produtos_subtitulo',
             'valor': 'Gerencie todos os doces da sua loja',
             'descricao': 'Subtítulo da página de produtos',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_novo_produto',
             'valor': 'Novo Produto',
             'descricao': 'Texto do botão novo produto',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_lista_produtos',
             'valor': 'Lista de Produtos',
             'descricao': 'Título da lista de produtos',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_todos_status',
             'valor': 'Todos os Status',
             'descricao': 'Texto do filtro todos os status',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_apenas_ativos',
             'valor': 'Apenas Ativos',
             'descricao': 'Texto do filtro apenas ativos',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_apenas_inativos',
             'valor': 'Apenas Inativos',
             'descricao': 'Texto do filtro apenas inativos',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_imagem',
             'valor': 'Imagem',
             'descricao': 'Título da coluna imagem',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_nome',
             'valor': 'Nome',
             'descricao': 'Título da coluna nome',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_preco',
             'valor': 'Preço',
             'descricao': 'Título da coluna preço',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_sabores',
             'valor': 'Sabores',
             'descricao': 'Título da coluna sabores',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_qtd_min',
             'valor': 'Qtd. Mín.',
             'descricao': 'Título da coluna quantidade mínima',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_estoque',
             'valor': 'Estoque',
             'descricao': 'Título da coluna estoque',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_status',
             'valor': 'Status',
             'descricao': 'Título da coluna status',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_data',
             'valor': 'Data',
             'descricao': 'Título da coluna data',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_coluna_acoes',
             'valor': 'Ações',
             'descricao': 'Título da coluna ações',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_editar',
             'valor': 'Editar',
             'descricao': 'Texto do botão editar',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_excluir',
             'valor': 'Excluir',
             'descricao': 'Texto do botão excluir',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_confirmar_exclusao',
             'valor': 'Tem certeza que deseja excluir o produto',
             'descricao': 'Texto de confirmação de exclusão',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_nao_pode_excluir',
             'valor': 'Não é possível excluir este produto',
             'descricao': 'Texto de erro quando não pode excluir',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_info_basicas',
             'valor': 'Informações Básicas',
             'descricao': 'Título da seção de informações básicas',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_nome_produto',
             'valor': 'Nome do Produto',
             'descricao': 'Label do campo nome do produto',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_descricao',
             'valor': 'Descrição',
             'descricao': 'Label do campo descrição',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_placeholder_nome',
             'valor': 'Ex: Brigadeiro Gourmet de Chocolate',
             'descricao': 'Placeholder do campo nome',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_placeholder_descricao',
             'valor': 'Descreva os sabores, ingredientes e ocasiões especiais...',
             'descricao': 'Placeholder do campo descrição',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_hint_nome',
             'valor': 'Escolha um nome atrativo e descritivo',
             'descricao': 'Dica do campo nome',
             'tipo': 'texto',
             'categoria': 'admin'
         },
         {
             'chave': 'admin_form_hint_descricao',
             'valor': 'Descreva detalhes que atraiam os clientes',
             'descricao': 'Dica do campo descrição',
             'tipo': 'texto',
             'categoria': 'admin'
         }
    ]
    
    with app.app_context():
        print("🔧 Inicializando configurações do site...")
        
        for config_data in configs_padrao:
            # Verificar se a configuração já existe
            existing = Configuracao.query.filter_by(chave=config_data['chave']).first()
            
            if not existing:
                config = Configuracao(**config_data)
                db.session.add(config)
                print(f"✅ Adicionada configuração: {config_data['chave']}")
            else:
                print(f"⏭️  Configuração já existe: {config_data['chave']}")
        
        try:
            db.session.commit()
            print("🎉 Configurações inicializadas com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar configurações: {e}")

if __name__ == '__main__':
    init_configuracoes()
