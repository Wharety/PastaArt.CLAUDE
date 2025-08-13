from flask import Blueprint, render_template, session, request, redirect, url_for, flash, jsonify
from models import Doce, db
from urllib.parse import quote
import json
from colorama import Fore, Style
from datetime import datetime

def debug_log(message, level="INFO"):
    """Log colorido para debug - cópia local"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": Fore.CYAN,
        "SUCCESS": Fore.GREEN,
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "CART": Fore.MAGENTA
    }
    color = colors.get(level, Fore.WHITE)
    print(f"{Fore.WHITE}[{timestamp}]{color} LOJA {level}: {message}{Style.RESET_ALL}")

loja_bp = Blueprint('loja', __name__)

@loja_bp.route('/')
def index():
    """Página inicial da loja"""
    return render_template('loja/index.html')

@loja_bp.route('/doces-tradicionais')
def doces_tradicionais():
    """Página de doces tradicionais"""
    doces = Doce.query.filter_by(ativo=True, categoria='tradicional').order_by(Doce.data_criacao.desc()).all()
    return render_template('loja/doces_tradicionais.html', doces=doces, categoria='tradicional')

@loja_bp.route('/doces-personalizados')
def doces_personalizados():
    """Página de doces personalizados"""
    doces = Doce.query.filter_by(ativo=True, categoria='personalizado').order_by(Doce.data_criacao.desc()).all()
    return render_template('loja/doces_personalizados.html', doces=doces, categoria='personalizado')

@loja_bp.route('/doce/<int:doce_id>')
def detalhes_doce(doce_id):
    """Página de detalhes do doce"""
    doce = Doce.query.get_or_404(doce_id)
    return render_template('loja/detalhes_doce.html', doce=doce)

@loja_bp.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    """Adicionar item ao carrinho"""
    debug_log("🛒 Iniciando adição ao carrinho", "CART")
    
    # Verificar CSRF primeiro
    if 'csrf_token' not in request.form:
        debug_log("❌ Token CSRF não encontrado no formulário", "ERROR")
        debug_log(f"Form keys: {list(request.form.keys())}", "ERROR")
        flash('Erro de segurança. Tente novamente.', 'error')
        return redirect(request.referrer or url_for('loja.index'))
    
    doce_id = request.form.get('doce_id', type=int)
    quantidade = request.form.get('quantidade', 1, type=int)
    sabor_selecionado = request.form.get('sabor_selecionado', '')
    
    debug_log(f"Produto ID: {doce_id}, Quantidade: {quantidade}, Sabor: {sabor_selecionado}", "CART")
    
    doce = Doce.query.get_or_404(doce_id)
    debug_log(f"Produto encontrado: {doce.nome} - R$ {doce.preco}", "SUCCESS")
    
    # Inicializar carrinho se não existir
    if 'cart' not in session:
        session['cart'] = {}
        debug_log("Carrinho inicializado", "CART")
    
    cart = session['cart']
    
    # Criar chave composta: doce_id + sabor_selecionado
    # Se não há sabor selecionado, usar apenas o doce_id
    if sabor_selecionado:
        cart_key = f"{doce_id}_{sabor_selecionado}"
        debug_log(f"Usando chave composta: {cart_key}", "CART")
    else:
        cart_key = str(doce_id)
        debug_log(f"Usando chave simples: {cart_key}", "CART")
    
    if cart_key in cart:
        quantidade_anterior = cart[cart_key]['quantidade']
        cart[cart_key]['quantidade'] += quantidade
        debug_log(f"Produto com mesmo sabor já no carrinho. Quantidade: {quantidade_anterior} → {cart[cart_key]['quantidade']}", "CART")
    else:
        cart[cart_key] = {
            'id': doce.id,
            'nome': doce.nome,
            'preco': float(doce.preco),  # Converter Decimal para float
            'imagem_url': doce.imagem_url,
            'quantidade': quantidade,
            'sabor_selecionado': sabor_selecionado
        }
        debug_log(f"Novo produto/sabor adicionado ao carrinho: {doce.nome} - {sabor_selecionado}", "SUCCESS")
    
    session['cart'] = cart
    session.modified = True
    
    total_itens = sum(item['quantidade'] for item in cart.values())
    debug_log(f"Carrinho atualizado. Total de itens: {total_itens}", "CART")
    
    # Mensagem personalizada baseada no sabor
    if sabor_selecionado:
        flash(f'{doce.nome} (Sabor: {sabor_selecionado}) adicionado ao carrinho!', 'success')
    else:
        flash(f'{doce.nome} adicionado ao carrinho!', 'success')
    
    return redirect(request.referrer or url_for('loja.index'))

@loja_bp.route('/carrinho')
def carrinho():
    """Página do carrinho de compras"""
    cart = session.get('cart', {})
    # Garantir que preço e quantidade sejam números
    total = sum(float(item['preco']) * int(item['quantidade']) for item in cart.values())
    return render_template('loja/carrinho.html', cart=cart, total=total)

@loja_bp.route('/atualizar_carrinho', methods=['POST'])
def atualizar_carrinho():
    """Atualizar quantidade de item no carrinho"""
    cart_key = request.form.get('cart_key')  # Agora recebe a chave composta
    quantidade = request.form.get('quantidade', type=int)
    
    if 'cart' in session and cart_key in session['cart']:
        if quantidade > 0:
            session['cart'][cart_key]['quantidade'] = quantidade
        else:
            del session['cart'][cart_key]
        session.modified = True
    
    return redirect(url_for('loja.carrinho'))

@loja_bp.route('/atualizar_quantidade_ajax', methods=['POST'])
def atualizar_quantidade_ajax():
    """Atualizar quantidade via AJAX sem recarregar a página"""
    try:
        data = request.get_json()
        cart_key = str(data.get('cart_key'))  # Agora recebe a chave composta
        quantidade = int(data.get('quantidade'))
        
        debug_log(f"AJAX: Atualizando quantidade - Chave {cart_key}, Quantidade: {quantidade}", "CART")
        
        if 'cart' not in session:
            return jsonify({'success': False, 'error': 'Carrinho não encontrado'})
        
        cart = session['cart']
        
        if cart_key not in cart:
            return jsonify({'success': False, 'error': 'Item não encontrado no carrinho'})
        
        if quantidade <= 0:
            # Remover item se quantidade for 0 ou negativa
            del cart[cart_key]
            debug_log(f"AJAX: Item {cart_key} removido do carrinho", "CART")
        else:
            # Atualizar quantidade
            cart[cart_key]['quantidade'] = quantidade
            debug_log(f"AJAX: Quantidade do item {cart_key} atualizada para {quantidade}", "CART")
        
        session['cart'] = cart
        session.modified = True
        
        # Calcular novos totais
        item_total = 0
        if cart_key in cart:
            item_total = float(cart[cart_key]['preco']) * int(cart[cart_key]['quantidade'])
        
        cart_total = sum(float(item['preco']) * int(item['quantidade']) for item in cart.values())
        cart_count = sum(item['quantidade'] for item in cart.values())
        
        debug_log(f"AJAX: Novos totais - Item: R$ {item_total:.2f}, Carrinho: R$ {cart_total:.2f}, Itens: {cart_count}", "SUCCESS")
        
        return jsonify({
            'success': True,
            'item_total': f"{item_total:.2f}",
            'cart_total': f"{cart_total:.2f}",
            'cart_count': cart_count,
            'item_removed': quantidade <= 0
        })
        
    except Exception as e:
        debug_log(f"AJAX: Erro ao atualizar quantidade: {str(e)}", "ERROR")
        return jsonify({'success': False, 'error': 'Erro interno do servidor'})

@loja_bp.route('/remover_carrinho/<cart_key>')
def remover_carrinho(cart_key):
    """Remover item do carrinho"""
    if 'cart' in session and cart_key in session['cart']:
        del session['cart'][cart_key]
        session.modified = True
        flash('Item removido do carrinho.', 'info')
    
    return redirect(url_for('loja.carrinho'))

@loja_bp.route('/checkout')
def checkout():
    """Página de checkout - Requer login"""
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        # Salvar a URL atual na sessão para redirecionamento após login
        session['redirect_after_login'] = request.url
        flash('Você precisa estar logado para finalizar a compra. Faça login ou crie uma conta.', 'warning')
        return redirect(url_for('usuarios.login'))
    
    cart = session.get('cart', {})
    if not cart:
        flash('Seu carrinho está vazio!', 'warning')
        return redirect(url_for('loja.index'))
    
    total = sum(float(item['preco']) * int(item['quantidade']) for item in cart.values())
    
    # Buscar dados do usuário logado
    from models import Usuario
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Erro ao carregar dados do usuário. Faça login novamente.', 'error')
        session.clear()
        return redirect(url_for('usuarios.login'))
    
    return render_template('loja/checkout.html', cart=cart, total=total, usuario=usuario)

@loja_bp.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    """Finalizar pedido e gerar link do WhatsApp"""
    # Verificar se o usuário está logado
    if 'user_id' not in session:
        # Salvar a URL atual na sessão para redirecionamento após login
        session['redirect_after_login'] = request.url
        flash('Você precisa estar logado para finalizar a compra.', 'error')
        return redirect(url_for('usuarios.login'))
    
    cart = session.get('cart', {})
    if not cart:
        flash('Seu carrinho está vazio!', 'error')
        return redirect(url_for('loja.index'))
    
    # Buscar dados do usuário logado
    from models import Usuario, Pedido, ItemPedido
    usuario = Usuario.query.get(session['user_id'])
    if not usuario:
        flash('Erro ao carregar dados do usuário.', 'error')
        return redirect(url_for('usuarios.login'))
    
    try:
        # Calcular total
        total = sum(float(item['preco']) * int(item['quantidade']) for item in cart.values())
        
        # Gerar número único do pedido
        import random
        import string
        from datetime import datetime
        
        # Formato: YYYYMMDD + 4 dígitos aleatórios
        data_hoje = datetime.now().strftime("%Y%m%d")
        numero_aleatorio = ''.join(random.choices(string.digits, k=4))
        numero_pedido = f"{data_hoje}{numero_aleatorio}"
        
        # Verificar se o número já existe (improvável, mas garantia)
        while Pedido.query.filter_by(numero_pedido=numero_pedido).first():
            numero_aleatorio = ''.join(random.choices(string.digits, k=4))
            numero_pedido = f"{data_hoje}{numero_aleatorio}"
        
        # Criar pedido no banco de dados
        pedido = Pedido(
            usuario_id=usuario.id,
            numero_pedido=numero_pedido,
            status='pendente',
            total=total,
            observacoes=f"Pedido realizado via site. Contato: {usuario.telefone or 'N/A'}"
        )
        db.session.add(pedido)
        db.session.flush()  # Para obter o ID do pedido
        
        # Criar itens do pedido
        for cart_key, item in cart.items():
            # Extrair o ID do doce e o sabor da chave (pode ser composta como "10_Chocolate Branco")
            parts = cart_key.split('_', 1)  # Divide apenas na primeira ocorrência
            doce_id = parts[0]  # Pega apenas a primeira parte antes do underscore
            sabor_selecionado = parts[1] if len(parts) > 1 else None  # Pega o resto como sabor
            
            item_pedido = ItemPedido(
                pedido_id=pedido.id,
                doce_id=int(doce_id),
                quantidade=item['quantidade'],
                preco_unitario=float(item['preco']),
                preco_total=float(item['preco']) * int(item['quantidade']),
                sabor_selecionado=sabor_selecionado
            )
            db.session.add(item_pedido)
        
        db.session.commit()
        debug_log(f"Pedido #{pedido.id} criado para usuário {usuario.nome}", "SUCCESS")
        
        # Gerar mensagem do WhatsApp (versão simplificada)
        mensagem = f"Novo Pedido #{pedido.numero_pedido} - Pasta Art Encanto\n\n"
        mensagem += f"Cliente: {usuario.nome}\n"
        mensagem += f"Email: {usuario.email}\n"
        if usuario.telefone:
            mensagem += f"Telefone: {usuario.telefone}\n"
        if usuario.endereco:
            mensagem += f"Endereco: {usuario.endereco}\n"
        mensagem += f"\nItens do Pedido:\n"
        
        for cart_key, item in cart.items():
            subtotal = float(item['preco']) * int(item['quantidade'])
            # Extrair o sabor da chave do carrinho
            parts = cart_key.split('_', 1)
            sabor_info = f" ({parts[1]})" if len(parts) > 1 else ""
            mensagem += f"- {item['nome']}{sabor_info} - Qtd: {item['quantidade']} - R$ {subtotal:.2f}\n"
        
        mensagem += f"\nTotal: R$ {total:.2f}\n\n"
        mensagem += f"Pedido: {pedido.numero_pedido}\n"
        mensagem += "Obrigado pela preferencia!"
        
        # Buscar número do WhatsApp das configurações
        from models import Configuracao
        whatsapp_config = Configuracao.query.filter_by(chave='whatsapp').first()
        whatsapp_numero = whatsapp_config.valor if whatsapp_config else "5566999348738"
        
        # Limpar o número (remover caracteres não numéricos)
        whatsapp_numero_limpo = ''.join(filter(str.isdigit, whatsapp_numero))
        
        # Garantir que comece com 55 (código do Brasil)
        if not whatsapp_numero_limpo.startswith('55'):
            whatsapp_numero_limpo = '55' + whatsapp_numero_limpo
        
        # Criar URL do WhatsApp com codificação simples
        debug_log(f"Mensagem original: {mensagem[:100]}...", "INFO")
        mensagem_codificada = quote(mensagem)
        whatsapp_url = f"https://wa.me/{whatsapp_numero_limpo}?text={mensagem_codificada}"
        debug_log(f"URL WhatsApp: {whatsapp_url[:100]}...", "INFO")
        
        # Limpar carrinho após finalizar pedido
        session.pop('cart', None)
        session.modified = True
        
        flash(f'Pedido #{pedido.numero_pedido} realizado com sucesso!', 'success')
        
        return render_template('loja/pedido_finalizado.html', 
                             whatsapp_url=whatsapp_url, 
                             nome=usuario.nome, 
                             total=total,
                             pedido_id=pedido.numero_pedido)
        
    except Exception as e:
        db.session.rollback()
        debug_log(f"Erro ao finalizar pedido: {str(e)}", "ERROR")
        flash('Erro ao processar pedido. Tente novamente.', 'error')
        return redirect(url_for('loja.checkout'))
