from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Será inicializado em app.py
db = SQLAlchemy()

class Configuracao(db.Model):
    """Modelo para configurações dinâmicas do site"""
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    chave = db.Column(db.String(100), unique=True, nullable=False, index=True)
    valor = db.Column(db.Text(length=65535), nullable=False)  # MEDIUMTEXT
    descricao = db.Column(db.String(200), nullable=True)
    tipo = db.Column(db.String(20), default='texto')  # texto, numero, email, url, boolean
    categoria = db.Column(db.String(50), default='geral', index=True)  # geral, contato, redes_sociais, rodape
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracao {self.chave}>'



class Usuario(db.Model):
    """Modelo para usuários da loja"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(200), nullable=True)  # Pode ser null para usuários sociais
    telefone = db.Column(db.String(20), nullable=True)
    # Endereço agregado (legado/fallback)
    endereco = db.Column(db.Text(length=16383), nullable=True)  # TEXT
    # Campos normalizados de endereço
    cep = db.Column(db.String(9), nullable=True)
    logradouro = db.Column(db.String(150), nullable=True)
    bairro = db.Column(db.String(100), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    numero_endereco = db.Column(db.String(20), nullable=True)
    complemento_endereco = db.Column(db.String(100), nullable=True)
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    
    # Campos para autenticação social
    provider = db.Column(db.String(20), nullable=True)  # 'google', 'facebook', 'local'
    provider_id = db.Column(db.String(100), nullable=True, index=True)  # ID do usuário no provedor
    avatar_url = db.Column(db.String(500), nullable=True)  # URL da foto do perfil
    
    # Relacionamento com pedidos
    pedidos = db.relationship('Pedido', backref='usuario', lazy=True)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

    def get_endereco_formatado(self) -> str:
        """Retorna endereço formatado a partir dos campos normalizados, com fallback para campo agregado."""
        partes = []
        if self.logradouro:
            logradouro_str = self.logradouro
            if self.numero_endereco:
                logradouro_str += f", {self.numero_endereco}"
            if self.complemento_endereco:
                logradouro_str += f" - {self.complemento_endereco}"
            partes.append(logradouro_str)
        if self.bairro:
            partes.append(self.bairro)
        cidade_estado = []
        if self.cidade:
            cidade_estado.append(self.cidade)
        if self.estado:
            cidade_estado.append(self.estado)
        if cidade_estado:
            partes.append('/'.join(cidade_estado))
        if self.cep:
            partes.append(self.cep)
        if partes:
            return ' - '.join(partes)
        return self.endereco or ''

class Pedido(db.Model):
    """Modelo para pedidos dos usuários"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    numero_pedido = db.Column(db.String(20), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='pendente', index=True)  # pendente, confirmado, em_preparo, enviado, entregue, cancelado
    total = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL para precisão monetária
    observacoes = db.Column(db.Text(length=16383), nullable=True)  # TEXT
    data_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    removido = db.Column(db.Boolean, default=False, index=True)  # Soft delete
    data_remocao = db.Column(db.DateTime, nullable=True)  # Data da remoção
    
    # Relacionamento com itens do pedido
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido {self.numero_pedido}>'

class ItemPedido(db.Model):
    """Modelo para itens de um pedido"""
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    doce_id = db.Column(db.Integer, db.ForeignKey('doces.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL para precisão monetária
    preco_total = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL para precisão monetária
    sabor_selecionado = db.Column(db.String(100), nullable=True)  # Sabor escolhido pelo usuário
    
    # Relacionamento com o doce
    doce = db.relationship('Doce', backref='itens_pedido')
    
    def __repr__(self):
        sabor_info = f" ({self.sabor_selecionado})" if self.sabor_selecionado else ""
        return f'<ItemPedido {self.doce.nome}{sabor_info} x{self.quantidade}>'

class Doce(db.Model):
    """Modelo para os doces da loja"""
    __tablename__ = 'doces'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    descricao = db.Column(db.Text(length=16383), nullable=False)  # TEXT
    preco = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL para precisão monetária
    imagem_url = db.Column(db.String(200), nullable=True)
    ativo = db.Column(db.Boolean, default=True, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Novos campos para robustez
    sabores = db.Column(db.Text(length=16383), nullable=True)  # TEXT - Lista de sabores disponíveis
    quantidade_minima = db.Column(db.Integer, default=1)  # Quantidade mínima para venda
    unidade_venda = db.Column(db.String(20), default='unidade')  # unidade, kg, g, etc.
    estoque_disponivel = db.Column(db.Integer, nullable=True)  # Controle de estoque
    destaque = db.Column(db.Boolean, default=False)  # Produto em destaque
    categoria = db.Column(db.String(50), default='tradicional', index=True)  # tradicional, personalizado

    
    def __repr__(self):
        return f'<Doce {self.nome}>'
    
    def to_dict(self):
        """Converter para dicionário para uso no carrinho"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'preco': self.preco,
            'imagem_url': self.imagem_url,
            'sabores': self.sabores,
            'quantidade_minima': self.quantidade_minima,
            'unidade_venda': self.unidade_venda,
            'estoque_disponivel': self.estoque_disponivel,
            'destaque': self.destaque,
            'categoria': self.categoria,
        }
    
    def get_sabores_list(self):
        """Retorna lista de sabores como array"""
        if self.sabores:
            return [s.strip() for s in self.sabores.split(',')]
        return []
    
    def is_disponivel(self):
        """Verifica se o produto está disponível para venda"""
        if not self.ativo:
            return False
        if self.estoque_disponivel is not None and self.estoque_disponivel <= 0:
            return False
        return True

class Admin(db.Model):
    """Modelo para administradores"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Admin {self.usuario}>'
