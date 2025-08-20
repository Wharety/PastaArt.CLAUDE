from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
from models import Admin, Doce, Pedido, db, KitItem
import os
from PIL import Image, ImageOps
from datetime import datetime, date, timedelta

admin_bp = Blueprint('admin', __name__)

class LoginForm(FlaskForm):
    """Formulário de login administrativo"""
    usuario = StringField('Usuário', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

def login_required(f):
    """Decorator para proteger rotas administrativas"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Verificar se arquivo é uma imagem válida"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """Ajustar orientação EXIF (iPhone) e redimensionar para otimizar carregamento."""
    try:
        with Image.open(image_path) as img:
            # Corrigir orientação baseada no EXIF (iPhone)
            try:
                img = ImageOps.exif_transpose(img)
            except Exception:
                pass

            # Redimensionar mantendo proporção
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Salvar preservando formato quando possível
            lower = image_path.lower()
            if lower.endswith(('.jpg', '.jpeg')):
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                img.save(image_path, format='JPEG', optimize=True, quality=85)
            elif lower.endswith('.webp'):
                img.save(image_path, format='WEBP', quality=85, method=6)
            elif lower.endswith('.png'):
                img.save(image_path, format='PNG', optimize=True)
            else:
                img.save(image_path, optimize=True)
    except Exception as e:
        print(f"Erro ao processar imagem (orientação/redimensionamento): {e}")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login administrativo"""
    form = LoginForm()
    
    if form.validate_on_submit():
        usuario = form.usuario.data
        senha = form.senha.data
        
        admin = Admin.query.filter_by(usuario=usuario).first()
        
        if admin and check_password_hash(admin.senha_hash, senha):
            session['admin_logged_in'] = True
            session['admin_id'] = admin.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
    
    return render_template('admin/login.html', form=form)

@admin_bp.route('/logout')
def logout():
    """Logout administrativo"""
    session.pop('admin_logged_in', None)
    session.pop('admin_id', None)
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('loja.index'))

@admin_bp.route('/')
@login_required
def dashboard():
    """Dashboard administrativo"""
    
    # Estatísticas de produtos
    doces = Doce.query.all()
    total_doces = len(doces)
    doces_ativos = len([d for d in doces if d.ativo])
    
    # Estatísticas de pedidos
    hoje = date.today()
    pedidos_hoje = Pedido.query.filter(
        db.func.date(Pedido.data_pedido) == hoje
    ).count()
    
    # Pedidos por status hoje
    pedidos_pendentes_hoje = Pedido.query.filter(
        db.func.date(Pedido.data_pedido) == hoje,
        Pedido.status == 'pendente'
    ).count()
    
    # Total de pedidos (todos os tempos, excluindo removidos)
    total_pedidos = Pedido.query.filter_by(removido=False).count()
    
    # Pedidos recentes (últimos 5)
    pedidos_recentes = Pedido.query.filter_by(removido=False).order_by(Pedido.data_pedido.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', 
                         doces=doces, 
                         total_doces=total_doces,
                         doces_ativos=doces_ativos,
                         pedidos_hoje=pedidos_hoje,
                         pedidos_pendentes_hoje=pedidos_pendentes_hoje,
                         total_pedidos=total_pedidos,
                         pedidos_recentes=pedidos_recentes)

@admin_bp.route('/doces')
@login_required
def listar_doces():
    """Listar todos os doces"""
    doces = Doce.query.order_by(Doce.data_criacao.desc()).all()
    return render_template('admin/listar_doces.html', doces=doces)

@admin_bp.route('/doces/novo', methods=['GET', 'POST'])
@login_required
def novo_doce():
    """Criar novo doce"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        descricao = request.form.get('descricao')
        preco = request.form.get('preco', type=float)
        ativo = bool(request.form.get('ativo'))
        
        # Novos campos
        categoria = request.form.get('categoria', 'tradicional')
        sabores = request.form.get('sabores', '').strip()
        quantidade_minima = request.form.get('quantidade_minima', type=int) or 1
        unidade_venda = request.form.get('unidade_venda', 'unidade')
        estoque_disponivel = request.form.get('estoque_disponivel', type=int)
        destaque = bool(request.form.get('destaque'))
        mais_pedido = bool(request.form.get('mais_pedido'))

        
        # Upload da imagem
        imagem_url = None
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Adicionar timestamp para evitar conflitos
                import time
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                
                file_path = os.path.join('static/uploads', filename)
                file.save(file_path)
                resize_image(file_path)
                imagem_url = f'uploads/{filename}'
        
        # Se for kit, ignorar preço informado e calcular com base nos itens
        desconto_percentual = request.form.get('desconto_percentual', type=float)
        doce = Doce(
            nome=nome,
            descricao=descricao,
            preco=preco or 0,
            imagem_url=imagem_url,
            ativo=ativo,
            categoria=categoria,
            sabores=sabores,
            quantidade_minima=quantidade_minima,
            unidade_venda=unidade_venda,
            estoque_disponivel=estoque_disponivel,
            destaque=destaque,
            mais_pedido=mais_pedido,
            desconto_percentual=desconto_percentual if unidade_venda == 'kit' else None,
        )
        
        db.session.add(doce)
        db.session.flush()

        # Processar itens do kit
        if unidade_venda == 'kit':
            produto_ids = request.form.getlist('kit_produto_id[]')
            quantidades = request.form.getlist('kit_quantidade[]')
            total_bruto = 0.0
            for i, prod_id in enumerate(produto_ids):
                try:
                    prod_id_int = int(prod_id)
                    qtd_int = int(quantidades[i]) if i < len(quantidades) else 1
                except Exception:
                    continue
                if qtd_int <= 0:
                    continue
                # Buscar produto e impedir kit-dentro-de-kit
                produto = Doce.query.get(prod_id_int)
                if not produto or produto.unidade_venda == 'kit':
                    continue
                db.session.add(KitItem(kit_id=doce.id, produto_id=produto.id, quantidade=qtd_int))
                total_bruto += float(produto.preco) * qtd_int
            # Aplicar desconto
            total_final = total_bruto
            if desconto_percentual is not None and desconto_percentual >= 0:
                total_final = total_bruto * (1 - (float(desconto_percentual) / 100.0))
            doce.preco = round(total_final, 2)
        
        db.session.commit()
        
        flash('Doce criado com sucesso!', 'success')
        return redirect(url_for('admin.listar_doces'))
    
    # Produtos disponíveis para compor kits (excluir kits)
    produtos_disponiveis = Doce.query.filter(Doce.ativo == True, Doce.unidade_venda != 'kit').order_by(Doce.nome.asc()).all()
    return render_template('admin/form_doce.html', doce=None, produtos_disponiveis=produtos_disponiveis)

@admin_bp.route('/doces/<int:doce_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_doce(doce_id):
    """Editar doce existente"""
    doce = Doce.query.get_or_404(doce_id)
    
    if request.method == 'POST':
        doce.nome = request.form.get('nome')
        doce.descricao = request.form.get('descricao')
        preco_informado = request.form.get('preco', type=float)
        doce.ativo = bool(request.form.get('ativo'))
        
        # Novos campos
        doce.categoria = request.form.get('categoria', 'tradicional')
        doce.sabores = request.form.get('sabores', '').strip()
        doce.quantidade_minima = request.form.get('quantidade_minima', type=int) or 1
        doce.unidade_venda = request.form.get('unidade_venda', 'unidade')
        doce.estoque_disponivel = request.form.get('estoque_disponivel', type=int)
        doce.destaque = bool(request.form.get('destaque'))
        doce.mais_pedido = bool(request.form.get('mais_pedido'))

        # Se for kit, recalcular preço e itens
        if doce.unidade_venda == 'kit':
            desconto_percentual = request.form.get('desconto_percentual', type=float)
            doce.desconto_percentual = desconto_percentual if desconto_percentual is not None else None
            # Limpar itens anteriores
            KitItem.query.filter_by(kit_id=doce.id).delete()
            produto_ids = request.form.getlist('kit_produto_id[]')
            quantidades = request.form.getlist('kit_quantidade[]')
            total_bruto = 0.0
            for i, prod_id in enumerate(produto_ids):
                try:
                    prod_id_int = int(prod_id)
                    qtd_int = int(quantidades[i]) if i < len(quantidades) else 1
                except Exception:
                    continue
                if qtd_int <= 0:
                    continue
                produto = Doce.query.get(prod_id_int)
                if not produto or produto.unidade_venda == 'kit':
                    continue
                db.session.add(KitItem(kit_id=doce.id, produto_id=produto.id, quantidade=qtd_int))
                total_bruto += float(produto.preco) * qtd_int
            total_final = total_bruto
            if desconto_percentual is not None and desconto_percentual >= 0:
                total_final = total_bruto * (1 - (float(desconto_percentual) / 100.0))
            doce.preco = round(total_final, 2)
        else:
            # Se não é kit, garantir remoção de itens e desconto
            KitItem.query.filter_by(kit_id=doce.id).delete()
            doce.desconto_percentual = None
            doce.preco = preco_informado

        # Upload de nova imagem
        if 'imagem' in request.files:
            file = request.files['imagem']
            if file and file.filename and allowed_file(file.filename):
                # Remover imagem antiga se existir
                if doce.imagem_url:
                    old_path = os.path.join('static', doce.imagem_url)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(file.filename)
                import time
                timestamp = str(int(time.time()))
                filename = f"{timestamp}_{filename}"
                
                file_path = os.path.join('static/uploads', filename)
                file.save(file_path)
                resize_image(file_path)
                doce.imagem_url = f'uploads/{filename}'
        
        db.session.commit()
        flash('Doce atualizado com sucesso!', 'success')
        return redirect(url_for('admin.listar_doces'))
    
    produtos_disponiveis = Doce.query.filter(Doce.ativo == True, Doce.unidade_venda != 'kit', Doce.id != doce.id).order_by(Doce.nome.asc()).all()
    return render_template('admin/form_doce.html', doce=doce, produtos_disponiveis=produtos_disponiveis)

@admin_bp.route('/doces/<int:doce_id>/excluir', methods=['POST'])
@login_required
def excluir_doce(doce_id):
    """Excluir doce"""
    try:
        doce = Doce.query.get_or_404(doce_id)
        
        # Log para debug
        print(f"Tentando excluir doce ID: {doce_id}, Nome: {doce.nome}")
        
        # Remover imagem do disco
        if doce.imagem_url:
            image_path = os.path.join('static', doce.imagem_url)
            if os.path.exists(image_path):
                os.remove(image_path)
                print(f"Imagem removida: {image_path}")
        
        # Verificar se há pedidos relacionados
        from models import ItemPedido
        pedidos_relacionados = ItemPedido.query.filter_by(doce_id=doce_id).first()
        if pedidos_relacionados:
            flash('Não é possível excluir este produto pois existem pedidos relacionados a ele.', 'error')
            return redirect(url_for('admin.listar_doces'))
        
        db.session.delete(doce)
        db.session.commit()
        
        print(f"Doce {doce.nome} excluído com sucesso")
        flash('Doce excluído com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao excluir doce: {e}")
        db.session.rollback()
        flash('Erro ao excluir o doce. Tente novamente.', 'error')
    
    return redirect(url_for('admin.listar_doces'))

@admin_bp.route('/doces/<int:doce_id>/toggle-status')
@login_required
def toggle_status_doce(doce_id):
    """Alternar status ativo/inativo do doce"""
    doce = Doce.query.get_or_404(doce_id)
    doce.ativo = not doce.ativo
    db.session.commit()
    
    status = "ativado" if doce.ativo else "desativado"
    flash(f'Doce {status} com sucesso!', 'success')
    return redirect(url_for('admin.listar_doces'))

@admin_bp.route('/pedidos')
@login_required
def listar_pedidos():
    """Listar todos os pedidos"""
    
    # Filtros
    status_filter = request.args.get('status', '')
    data_filter = request.args.get('data', '')
    cliente_nome_filter = request.args.get('cliente_nome', '')
    
    # Query base (excluindo pedidos removidos)
    query = Pedido.query.filter_by(removido=False)
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Pedido.status == status_filter)
    
    if data_filter == 'hoje':
        hoje = date.today()
        query = query.filter(db.func.date(Pedido.data_pedido) == hoje)
    elif data_filter == 'semana':
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=7)
        query = query.filter(Pedido.data_pedido >= inicio_semana)
    
    # Filtro por nome do cliente
    if cliente_nome_filter:
        from models import Usuario
        query = query.join(Usuario).filter(
            db.func.lower(Usuario.nome).contains(db.func.lower(cliente_nome_filter))
        )
    
    # Ordenar por data mais recente
    pedidos = query.order_by(Pedido.data_pedido.desc()).all()
    
    # Estatísticas (excluindo removidos)
    total_pedidos = Pedido.query.filter_by(removido=False).count()
    total_pedidos_removidos = Pedido.query.filter_by(removido=True).count()
    pedidos_hoje = Pedido.query.filter(
        Pedido.removido == False,
        db.func.date(Pedido.data_pedido) == date.today()
    ).count()
    
    return render_template('admin/listar_pedidos.html', 
                         pedidos=pedidos,
                         total_pedidos=total_pedidos,
                         total_pedidos_removidos=total_pedidos_removidos,
                         pedidos_hoje=pedidos_hoje,
                         status_filter=status_filter,
                         data_filter=data_filter,
                         cliente_nome_filter=cliente_nome_filter)

@admin_bp.route('/pedidos/<int:pedido_id>')
@login_required
def detalhes_pedido(pedido_id):
    """Ver detalhes de um pedido específico"""
    pedido = Pedido.query.get_or_404(pedido_id)
    return render_template('admin/detalhes_pedido.html', pedido=pedido)

@admin_bp.route('/pedidos/<int:pedido_id>/atualizar-status', methods=['POST'])
@login_required
def atualizar_status_pedido(pedido_id):
    """Atualizar status de um pedido"""
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.form.get('status')
    
    if novo_status in ['pendente', 'preparando', 'pronto', 'entregando', 'concluido', 'cancelado']:
        pedido.status = novo_status
        db.session.commit()
        flash(f'Status do pedido #{pedido.numero_pedido} atualizado para {novo_status.title()}', 'success')
    else:
        flash('Status inválido', 'error')
    
    return redirect(url_for('admin.detalhes_pedido', pedido_id=pedido_id))

@admin_bp.route('/pedidos/<int:pedido_id>/excluir', methods=['POST'])
@login_required
def excluir_pedido(pedido_id):
    """Excluir um pedido"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        # Log para debug
        print(f"Tentando excluir pedido ID: {pedido_id}, Número: {pedido.numero_pedido}")
        
        # Verificar se o pedido pode ser excluído (apenas se estiver pendente ou cancelado)
        if pedido.status not in ['pendente', 'cancelado']:
            flash('Só é possível excluir pedidos pendentes ou cancelados.', 'error')
            return redirect(url_for('admin.listar_pedidos'))
        
        # Excluir itens do pedido primeiro (cascade)
        for item in pedido.itens:
            db.session.delete(item)
        
        # Excluir o pedido
        db.session.delete(pedido)
        db.session.commit()
        
        print(f"Pedido {pedido.numero_pedido} excluído com sucesso")
        flash(f'Pedido #{pedido.numero_pedido} excluído com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao excluir pedido: {e}")
        db.session.rollback()
        flash('Erro ao excluir o pedido. Tente novamente.', 'error')
    
    return redirect(url_for('admin.listar_pedidos'))

@admin_bp.route('/pedidos/<int:pedido_id>/check-delete')
@login_required
def check_delete_pedido_possibility(pedido_id):
    """Verificar se um pedido pode ser excluído"""
    from flask import jsonify
    
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        can_delete = pedido.status in ['pendente', 'cancelado']
        message = f'Pedido pode ser excluído.' if can_delete else f'Não é possível excluir pedidos com status "{pedido.status}". Apenas pedidos pendentes ou cancelados podem ser excluídos.'
        
        return jsonify({
            'can_delete': can_delete,
            'status': pedido.status,
            'message': message
        })
        
    except Exception as e:
        return jsonify({
            'can_delete': False,
            'error': str(e)
        }), 500

@admin_bp.route('/pedidos/bulk-delete', methods=['POST'])
@login_required
def excluir_pedidos_multiplos():
    """Excluir múltiplos pedidos de uma vez"""
    try:
        pedido_ids = request.form.getlist('pedido_ids')
        
        if not pedido_ids:
            flash('Nenhum pedido selecionado para exclusão.', 'error')
            return redirect(url_for('admin.listar_pedidos'))
        
        # Verificar se todos os pedidos podem ser excluídos
        pedidos_para_excluir = []
        pedidos_nao_excluiveis = []
        
        for pedido_id in pedido_ids:
            try:
                pedido = Pedido.query.get(int(pedido_id))
                if pedido:
                    if pedido.status in ['pendente', 'cancelado']:
                        pedidos_para_excluir.append(pedido)
                    else:
                        pedidos_nao_excluiveis.append(pedido)
            except ValueError:
                continue
        
        # Excluir pedidos que podem ser excluídos
        excluidos_count = 0
        for pedido in pedidos_para_excluir:
            try:
                # Excluir itens do pedido primeiro
                for item in pedido.itens:
                    db.session.delete(item)
                
                # Excluir o pedido
                db.session.delete(pedido)
                excluidos_count += 1
                
                print(f"Pedido {pedido.numero_pedido} excluído com sucesso")
                
            except Exception as e:
                print(f"Erro ao excluir pedido {pedido.numero_pedido}: {e}")
                continue
        
        # Commit das exclusões
        if excluidos_count > 0:
            db.session.commit()
            flash(f'{excluidos_count} pedido(s) excluído(s) com sucesso!', 'success')
        
        # Mensagem sobre pedidos que não puderam ser excluídos
        if pedidos_nao_excluiveis:
            nao_excluiveis_numeros = [p.numero_pedido for p in pedidos_nao_excluiveis]
            flash(f'{len(pedidos_nao_excluiveis)} pedido(s) não puderam ser excluídos (status não permitido): {", ".join(nao_excluiveis_numeros)}', 'warning')
        
    except Exception as e:
        print(f"Erro ao excluir múltiplos pedidos: {e}")
        db.session.rollback()
        flash('Erro ao excluir os pedidos. Tente novamente.', 'error')
    
    return redirect(url_for('admin.listar_pedidos'))

@admin_bp.route('/pedidos/bulk-remove', methods=['POST'])
@login_required
def remover_pedidos_multiplos():
    """Remover múltiplos pedidos (mover para lixeira)"""
    try:
        pedido_ids = request.form.getlist('pedido_ids')
        
        if not pedido_ids:
            flash('Nenhum pedido selecionado para remoção.', 'error')
            return redirect(url_for('admin.listar_pedidos'))
        
        # Verificar se todos os pedidos podem ser removidos
        pedidos_para_remover = []
        pedidos_nao_removiveis = []
        
        for pedido_id in pedido_ids:
            try:
                pedido = Pedido.query.get(int(pedido_id))
                if pedido:
                    if pedido.status in ['pendente', 'cancelado']:
                        pedidos_para_remover.append(pedido)
                    else:
                        pedidos_nao_removiveis.append(pedido)
            except ValueError:
                continue
        
        # Remover pedidos que podem ser removidos
        removidos_count = 0
        for pedido in pedidos_para_remover:
            try:
                # Marcar como removido (soft delete)
                pedido.removido = True
                pedido.data_remocao = datetime.now()
                removidos_count += 1
                
                print(f"Pedido {pedido.numero_pedido} removido com sucesso")
                
            except Exception as e:
                print(f"Erro ao remover pedido {pedido.numero_pedido}: {e}")
                continue
        
        # Commit das remoções
        if removidos_count > 0:
            db.session.commit()
            flash(f'{removidos_count} pedido(s) removido(s) com sucesso!', 'success')
        
        # Mensagem sobre pedidos que não puderam ser removidos
        if pedidos_nao_removiveis:
            nao_removiveis_numeros = [p.numero_pedido for p in pedidos_nao_removiveis]
            flash(f'{len(pedidos_nao_removiveis)} pedido(s) não puderam ser removidos (status não permitido): {", ".join(nao_removiveis_numeros)}', 'warning')
        
    except Exception as e:
        print(f"Erro ao remover múltiplos pedidos: {e}")
        db.session.rollback()
        flash('Erro ao remover os pedidos. Tente novamente.', 'error')
    
    return redirect(url_for('admin.listar_pedidos'))

@admin_bp.route('/pedidos/lixeira')
@login_required
def lixeira_pedidos():
    """Visualizar pedidos removidos (lixeira)"""
    
    # Filtros
    status_filter = request.args.get('status', '')
    data_filter = request.args.get('data', '')
    cliente_nome_filter = request.args.get('cliente_nome', '')
    
    # Query base (apenas pedidos removidos)
    query = Pedido.query.filter_by(removido=True)
    
    # Aplicar filtros
    if status_filter:
        query = query.filter(Pedido.status == status_filter)
    
    if data_filter == 'hoje':
        hoje = date.today()
        query = query.filter(db.func.date(Pedido.data_pedido) == hoje)
    elif data_filter == 'semana':
        hoje = date.today()
        inicio_semana = hoje - timedelta(days=7)
        query = query.filter(Pedido.data_pedido >= inicio_semana)
    
    # Filtro por nome do cliente
    if cliente_nome_filter:
        from models import Usuario
        query = query.join(Usuario).filter(
            db.func.lower(Usuario.nome).contains(db.func.lower(cliente_nome_filter))
        )
    
    # Ordenar por data de remoção mais recente
    pedidos = query.order_by(Pedido.data_remocao.desc()).all()
    
    # Estatísticas
    total_pedidos_removidos = Pedido.query.filter_by(removido=True).count()
    total_pedidos_ativos = Pedido.query.filter_by(removido=False).count()
    
    return render_template('admin/lixeira_pedidos.html', 
                         pedidos=pedidos,
                         total_pedidos_removidos=total_pedidos_removidos,
                         total_pedidos_ativos=total_pedidos_ativos,
                         status_filter=status_filter,
                         data_filter=data_filter,
                         cliente_nome_filter=cliente_nome_filter)

@admin_bp.route('/pedidos/<int:pedido_id>/restaurar', methods=['POST'])
@login_required
def restaurar_pedido(pedido_id):
    """Restaurar um pedido da lixeira"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        if not pedido.removido:
            flash('Este pedido não está na lixeira.', 'error')
            return redirect(url_for('admin.lixeira_pedidos'))
        
        # Restaurar pedido
        pedido.removido = False
        pedido.data_remocao = None
        db.session.commit()
        
        flash(f'Pedido #{pedido.numero_pedido} restaurado com sucesso!', 'success')
        
    except Exception as e:
        print(f"Erro ao restaurar pedido: {e}")
        db.session.rollback()
        flash('Erro ao restaurar o pedido. Tente novamente.', 'error')
    
    return redirect(url_for('admin.lixeira_pedidos'))

@admin_bp.route('/pedidos/<int:pedido_id>/excluir-permanente', methods=['POST'])
@login_required
def excluir_pedido_permanente(pedido_id):
    """Excluir permanentemente um pedido da lixeira"""
    try:
        pedido = Pedido.query.get_or_404(pedido_id)
        
        if not pedido.removido:
            flash('Este pedido não está na lixeira.', 'error')
            return redirect(url_for('admin.lixeira_pedidos'))
        
        # Excluir itens do pedido primeiro
        for item in pedido.itens:
            db.session.delete(item)
        
        # Excluir o pedido permanentemente
        db.session.delete(pedido)
        db.session.commit()
        
        flash(f'Pedido #{pedido.numero_pedido} excluído permanentemente!', 'success')
        
    except Exception as e:
        print(f"Erro ao excluir pedido permanentemente: {e}")
        db.session.rollback()
        flash('Erro ao excluir o pedido. Tente novamente.', 'error')
    
    return redirect(url_for('admin.lixeira_pedidos'))

@admin_bp.route('/doces/<int:doce_id>/check-delete')
@login_required
def check_delete_possibility(doce_id):
    """Verificar se um doce pode ser excluído"""
    from flask import jsonify
    
    try:
        doce = Doce.query.get_or_404(doce_id)
        
        # Verificar se há pedidos relacionados
        from models import ItemPedido
        itens_relacionados = ItemPedido.query.filter_by(doce_id=doce_id).count()
        
        return jsonify({
            'can_delete': itens_relacionados == 0,
            'related_orders': itens_relacionados,
            'message': f'Existem {itens_relacionados} pedidos relacionados a este produto.' if itens_relacionados > 0 else 'Produto pode ser excluído com segurança.'
        })
        
    except Exception as e:
        return jsonify({
            'can_delete': False,
            'error': str(e)
        }), 500
