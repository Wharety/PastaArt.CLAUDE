import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from models import Configuracao, db
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import uuid

configuracoes_bp = Blueprint('configuracoes', __name__)

def admin_required(f):
    """Decorator para proteger rotas administrativas"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename, allowed_extensions):
    """Verifica se o arquivo tem uma extensão permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder, allowed_extensions):
    """Salva um arquivo enviado e retorna o nome do arquivo"""
    if file and file.filename:
        if allowed_file(file.filename, allowed_extensions):
            # Gerar nome único para o arquivo
            filename = secure_filename(file.filename)
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
            
            # Criar diretório se não existir
            upload_path = os.path.join(current_app.static_folder, 'images', folder)
            os.makedirs(upload_path, exist_ok=True)
            
            # Salvar arquivo
            file_path = os.path.join(upload_path, unique_filename)
            file.save(file_path)
            
            return f"images/{folder}/{unique_filename}"
    return None

@configuracoes_bp.route('/configuracoes', methods=['GET', 'POST'])
@admin_required
def listar_configuracoes():
    """Listar e editar todas as configurações"""
    
    if request.method == 'POST':
        try:
            # Processar uploads de imagens
            image_uploads = {
                'logo': request.files.get('logo'),
                'banner': request.files.get('banner'),
                'tradicional_image': request.files.get('tradicional_image'),
                'personalizado_image': request.files.get('personalizado_image')
            }
            
            # Salvar imagens enviadas
            for field_name, file in image_uploads.items():
                if file and file.filename:
                    if field_name == 'logo':
                        file_path = save_uploaded_file(file, 'uploads', {'svg', 'png', 'jpg', 'jpeg'})
                        if file_path:
                            # Salvar configuração da logo
                            config = Configuracao.query.filter_by(chave='site_logo').first()
                            if not config:
                                config = Configuracao(
                                    chave='site_logo',
                                    valor=file_path,
                                    descricao='Logo do site',
                                    tipo='texto',
                                    categoria='visual'
                                )
                                db.session.add(config)
                            else:
                                config.valor = file_path
                    
                    elif field_name == 'banner':
                        file_path = save_uploaded_file(file, 'uploads', {'webp', 'png', 'jpg', 'jpeg'})
                        if file_path:
                            # Salvar configuração do banner
                            config = Configuracao.query.filter_by(chave='site_banner').first()
                            if not config:
                                config = Configuracao(
                                    chave='site_banner',
                                    valor=file_path,
                                    descricao='Banner principal do site',
                                    tipo='texto',
                                    categoria='visual'
                                )
                                db.session.add(config)
                            else:
                                config.valor = file_path
                    
                    elif field_name == 'tradicional_image':
                        file_path = save_uploaded_file(file, 'uploads', {'webp', 'png', 'jpg', 'jpeg'})
                        if file_path:
                            # Salvar configuração da imagem do card tradicional
                            config = Configuracao.query.filter_by(chave='card_tradicional_image').first()
                            if not config:
                                config = Configuracao(
                                    chave='card_tradicional_image',
                                    valor=file_path,
                                    descricao='Imagem do card de doces tradicionais',
                                    tipo='texto',
                                    categoria='visual'
                                )
                                db.session.add(config)
                            else:
                                config.valor = file_path
                    
                    elif field_name == 'personalizado_image':
                        file_path = save_uploaded_file(file, 'uploads', {'webp', 'png', 'jpg', 'jpeg'})
                        if file_path:
                            # Salvar configuração da imagem do card personalizado
                            config = Configuracao.query.filter_by(chave='card_personalizado_image').first()
                            if not config:
                                config = Configuracao(
                                    chave='card_personalizado_image',
                                    valor=file_path,
                                    descricao='Imagem do card de doces personalizados',
                                    tipo='texto',
                                    categoria='visual'
                                )
                                db.session.add(config)
                            else:
                                config.valor = file_path
            
            # Processar campos de texto
            text_fields = [
                'tradicional_title', 'tradicional_description',
                'personalizado_title', 'personalizado_description',
                'about_title', 'about_description',
                'telefone', 'email', 'endereco',
                'site_nome', 'site_descricao', 'rodape_texto',
                'produtos_titulo', 'produtos_subtitulo',
                'tradicional_feature_1', 'tradicional_feature_2', 'tradicional_feature_3',
                'personalizado_feature_1', 'personalizado_feature_2', 'personalizado_feature_3',
                'about_feature_1', 'about_feature_2', 'about_feature_3',
                'checkout_titulo', 'checkout_descricao', 'checkout_botao_texto', 'checkout_telefone_obrigatorio',
                'pedido_sucesso_titulo', 'pedido_sucesso_subtitulo', 'pedido_tempo_resposta', 'pedido_whatsapp_texto',
                'dashboard_titulo', 'dashboard_subtitulo', 'dashboard_total_produtos', 'dashboard_produtos_ativos',
                'dashboard_produtos_inativos', 'dashboard_pedidos_hoje', 'dashboard_pedidos_pendentes',
                'dashboard_novo_produto_titulo', 'dashboard_novo_produto_descricao',
                'dashboard_gerenciar_produtos_titulo', 'dashboard_gerenciar_produtos_descricao',
                'dashboard_ver_pedidos_titulo', 'dashboard_ver_pedidos_descricao',
                'dashboard_ver_loja_titulo', 'dashboard_ver_loja_descricao',
                'dashboard_pedidos_recentes_titulo', 'dashboard_produtos_recentes_titulo',
                'dashboard_ver_todos', 'dashboard_ver_detalhes', 'dashboard_editar', 'dashboard_mais',
                'admin_produtos_titulo', 'admin_produtos_subtitulo', 'admin_novo_produto', 'admin_lista_produtos',
                'admin_todos_status', 'admin_apenas_ativos', 'admin_apenas_inativos',
                'admin_coluna_imagem', 'admin_coluna_nome', 'admin_coluna_preco', 'admin_coluna_sabores',
                'admin_coluna_qtd_min', 'admin_coluna_estoque', 'admin_coluna_status', 'admin_coluna_data',
                'admin_coluna_acoes', 'admin_editar', 'admin_excluir', 'admin_confirmar_exclusao',
                'admin_nao_pode_excluir', 'admin_form_info_basicas', 'admin_form_nome_produto',
                'admin_form_descricao', 'admin_form_placeholder_nome', 'admin_form_placeholder_descricao',
                'admin_form_hint_nome', 'admin_form_hint_descricao',
                'facebook_url', 'instagram_url', 'whatsapp_url', 'tiktok_url', 'youtube_url', 'linkedin_url',
                # Campos de configuração de email
                'email_host', 'email_port', 'email_user', 'email_password', 'email_from', 'email_site', 'email_use_tls'
            ]
            
            current_app.logger.info(f"Campos de texto a serem processados: {text_fields}")
            current_app.logger.info(f"Campos de contato na lista: {[f for f in text_fields if f in ['telefone', 'email', 'endereco']]}")
            
            # Log de todos os campos no request.form
            current_app.logger.info("Todos os campos no request.form:")
            for key, value in request.form.items():
                current_app.logger.info(f"  {key} = '{value}'")
            
            for field in text_fields:
                value = request.form.get(field, '').strip()
                # Processar todos os campos, mesmo se estiverem vazios
                current_app.logger.info(f"Processando campo: {field} = '{value}' (presente no form: {field in request.form})")
                
                # Log específico para campos de contato
                if field in ['telefone', 'email', 'endereco']:
                    current_app.logger.info(f"Campo de contato detectado: {field} = '{value}'")
                    current_app.logger.info(f"Valor do campo {field} no request.form: '{request.form.get(field, 'NÃO ENCONTRADO')}'")
                    current_app.logger.info(f"Campo {field} presente no request.form: {field in request.form}")
                    current_app.logger.info(f"Todos os campos no request.form: {list(request.form.keys())}")
                
                config = Configuracao.query.filter_by(chave=field).first()
                current_app.logger.info(f"Campo {field} existe no banco: {config is not None}")
                if config:
                    current_app.logger.info(f"Valor atual no banco para {field}: '{config.valor}'")
                if not config:
                    # Determinar categoria baseada no nome do campo
                    if field.startswith('tradicional_') or field.startswith('personalizado_'):
                        categoria = 'category_cards'
                    elif field.startswith('about_'):
                        categoria = 'about_content'
                    elif field in ['telefone', 'email', 'endereco']:
                        categoria = 'contato'
                        current_app.logger.info(f"Campo de contato categorizado: {field} -> {categoria}")
                    elif field.startswith('email_'):
                        categoria = 'email_config'
                        current_app.logger.info(f"Campo de email categorizado: {field} -> {categoria}")
                    elif field in ['facebook_url', 'instagram_url', 'whatsapp_url', 'tiktok_url', 'youtube_url', 'linkedin_url']:
                        categoria = 'redes_sociais'
                    elif field.startswith('site_') or field.startswith('rodape_'):
                        categoria = 'site_info'
                    elif field.startswith('produtos_'):
                        categoria = 'pagina_inicial'
                    elif field.startswith('checkout_') or field.startswith('pedido_'):
                        categoria = 'checkout'
                    elif field.startswith('dashboard_'):
                        categoria = 'dashboard'
                    elif field.startswith('admin_'):
                        categoria = 'admin'
                    else:
                        categoria = 'geral'
                    
                    config = Configuracao(
                        chave=field,
                        valor=value,
                        descricao=f'Configuração: {field}',
                        tipo='texto',
                        categoria=categoria
                    )
                    db.session.add(config)
                    current_app.logger.info(f"Criando novo campo: {field} = '{value}' (categoria: {categoria})")
                    
                    # Log específico para campos de contato
                    if field in ['telefone', 'email', 'endereco']:
                        current_app.logger.info(f"Novo campo de contato criado: {field} = '{value}' (categoria: {categoria})")
                        current_app.logger.info(f"Campo {field} adicionado à sessão do banco")
                else:
                    old_value = config.valor
                    config.valor = value
                    current_app.logger.info(f"Atualizando campo existente: {field} = '{old_value}' -> '{value}'")
                    
                    # Log específico para campos de contato
                    if field in ['telefone', 'email', 'endereco']:
                        current_app.logger.info(f"Campo de contato atualizado: {field} = '{old_value}' -> '{value}'")
                        current_app.logger.info(f"Campo {field} modificado na sessão do banco")
            
            current_app.logger.info("Fazendo commit das alterações...")
            try:
                db.session.commit()
                current_app.logger.info("Commit realizado com sucesso!")
            except Exception as commit_error:
                current_app.logger.error(f"Erro no commit: {commit_error}")
                raise
            
            # Verificar se os campos de contato foram salvos
            current_app.logger.info("Verificando campos de contato após commit...")
            for field in ['telefone', 'email', 'endereco']:
                config = Configuracao.query.filter_by(chave=field).first()
                if config:
                    current_app.logger.info(f"Campo de contato salvo no banco: {field} = '{config.valor}'")
                else:
                    current_app.logger.warning(f"Campo de contato não encontrado no banco: {field}")
                    
            # Verificar todos os campos salvos
            current_app.logger.info("Todos os campos salvos no banco:")
            for config in Configuracao.query.all():
                current_app.logger.info(f"  {config.chave} = '{config.valor}' (categoria: {config.categoria})")
            flash('Configurações salvas com sucesso!', 'success')
            
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar configurações: {str(e)}")
            current_app.logger.error(f"Tipo do erro: {type(e)}")
            current_app.logger.error(f"Detalhes do erro: {e}")
            db.session.rollback()
            current_app.logger.info("Rollback realizado devido ao erro")
            flash(f'Erro ao salvar configurações: {str(e)}', 'error')
            current_app.logger.error(f'Erro ao salvar configurações: {str(e)}')
        
        current_app.logger.info("Redirecionando após processamento")
        return redirect(url_for('configuracoes.listar_configuracoes'))

    # Buscar configurações existentes
    configs = {}
    configuracoes = Configuracao.query.all()
    
    current_app.logger.info(f"Carregando {len(configuracoes)} configurações do banco de dados")
    
    for config in configuracoes:
        configs[config.chave] = config.valor
        current_app.logger.info(f"Configuração carregada: {config.chave} = '{config.valor}' (categoria: {config.categoria})")
        
        # Log específico para campos de contato
        if config.chave in ['telefone', 'email', 'endereco']:
            current_app.logger.info(f"Campo de contato carregado: {config.chave} = '{config.valor}' (categoria: {config.categoria})")
    
    current_app.logger.info(f"Renderizando template com {len(configs)} configurações")
    
    # Log específico para campos de contato
    for field in ['telefone', 'email', 'endereco']:
        if field in configs:
            current_app.logger.info(f"Campo de contato disponível no template: {field} = '{configs[field]}'")
        else:
            current_app.logger.warning(f"Campo de contato não disponível no template: {field}")
            
    # Log de todos os campos disponíveis no template
    current_app.logger.info("Todos os campos disponíveis no template:")
    for key, value in configs.items():
        current_app.logger.info(f"  {key} = '{value}'")
    
    return render_template('admin/configuracoes.html', configs=configs)

@configuracoes_bp.route('/configuracoes/<categoria>', methods=['GET', 'POST'])
@admin_required
def editar_categoria_config(categoria):
    """Editar configurações de uma categoria específica"""
    configs = Configuracao.query.filter_by(categoria=categoria).all()
    
    if not configs:
        flash(f'Categoria de configuração "{categoria}" não encontrada.', 'error')
        return redirect(url_for('configuracoes.listar_configuracoes'))

    if request.method == 'POST':
        for config in configs:
            valor = request.form.get(config.chave)
            if valor is not None:
                config.valor = valor.strip()
        
        db.session.commit()
        flash(f'Configurações de "{categoria}" salvas com sucesso!', 'success')
        return redirect(url_for('configuracoes.listar_configuracoes'))
        
    categoria_titulo = configs[0].categoria.replace('_', ' ').title()
    return render_template('admin/form_config_categoria.html', configs=configs, categoria=categoria, categoria_titulo=categoria_titulo)


