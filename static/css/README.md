# Sistema de Design CSS - PastaArt Encanto

## Visão Geral

Este sistema de design foi criado para centralizar e organizar os estilos do projeto PastaArt Encanto, tornando a manutenção mais simples e eficiente.

## Estrutura de Arquivos

```
static/css/
├── main.css          # Arquivo principal que importa todos os outros
├── variables.css     # Variáveis CSS e utilitários
├── components.css    # Componentes reutilizáveis
├── loja.css         # Estilos específicos da loja
├── admin.css        # Estilos específicos do painel administrativo
└── README.md        # Esta documentação
```

## Arquivos

### `main.css`
Arquivo principal que importa todos os outros arquivos CSS. Contém também estilos específicos adicionais que não se encaixam nos outros arquivos.

### `variables.css`
- **Variáveis CSS**: Cores, tipografia, espaçamentos, bordas, sombras, transições
- **Utilitários**: Classes utilitárias para cores, espaçamentos, texto, bordas, etc.
- **Sistema de Design**: Definições consistentes para todo o projeto

### `components.css`
- **Componentes Base**: Botões, alertas, cards, formulários, badges, modais
- **Layout**: Grid system, flex utilities, position utilities
- **Animações**: Transições e keyframes
- **Utilitários**: Classes para display, flex, texto, etc.

### `loja.css`
- **Header**: Navegação, logo, menu mobile
- **Produtos**: Cards de produtos, detalhes, grid
- **Banner**: Seção de destaque
- **Footer**: Rodapé da loja
- **Responsivo**: Adaptações para mobile

### `admin.css`
- **Login**: Tela de login administrativa
- **Dashboard**: Cards de estatísticas, ações rápidas
- **Tabelas**: Listagem de produtos, configurações
- **Formulários**: Formulários de produtos e configurações
- **Responsivo**: Adaptações para mobile

## Variáveis CSS

### Cores
```css
--color-primary: #d4a373;
--color-primary-dark: #b8936b;
--color-text: #5c4a3e;
--color-text-light: #8b7a6f;
--color-success: #82c341;
--color-warning: #f39c12;
--color-error: #e74c3c;
```

### Tipografia
```css
--font-primary: 'Open Sans', sans-serif;
--font-heading: 'Playfair Display', serif;
--text-base: 1rem;
--text-lg: 1.125rem;
--text-xl: 1.25rem;
```

### Espaçamentos
```css
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-4: 1rem;      /* 16px */
--space-8: 2rem;      /* 32px */
```

### Bordas e Sombras
```css
--border-radius: 8px;
--shadow-soft: 0 2px 10px rgba(212, 163, 115, 0.1);
--shadow-medium: 0 4px 20px rgba(212, 163, 115, 0.15);
```

## Como Usar

### 1. Classes Utilitárias
```html
<!-- Cores -->
<div class="text-primary">Texto primário</div>
<div class="bg-success">Fundo verde</div>

<!-- Espaçamentos -->
<div class="p-4">Padding 16px</div>
<div class="m-8">Margin 32px</div>

<!-- Flexbox -->
<div class="flex-center">Centralizado</div>
<div class="flex-between">Espaçado</div>

<!-- Texto -->
<div class="text-lg font-semibold">Texto grande e negrito</div>
```

### 2. Componentes
```html
<!-- Botões -->
<button class="btn btn-primary">Botão Primário</button>
<button class="btn btn-outline">Botão Outline</button>

<!-- Alertas -->
<div class="alert alert-success">
    <i class="fas fa-check-circle"></i>
    Sucesso!
</div>

<!-- Cards -->
<div class="card">
    <div class="card-header">Título</div>
    <div class="card-body">Conteúdo</div>
</div>

<!-- Formulários -->
<div class="form-group">
    <label class="form-label">Nome</label>
    <input class="form-control" type="text">
</div>
```

### 3. Grid System
```html
<!-- Grid responsivo -->
<div class="grid grid-3">
    <div>Item 1</div>
    <div>Item 2</div>
    <div>Item 3</div>
</div>
```

## Responsividade

O sistema inclui breakpoints responsivos:

- **Mobile**: `max-width: 768px`
- **Tablet**: `max-width: 1024px`
- **Desktop**: `min-width: 1025px`

## Benefícios

### 1. Manutenibilidade
- Código organizado em arquivos específicos
- Variáveis CSS centralizadas
- Fácil localização de estilos

### 2. Consistência
- Sistema de design unificado
- Variáveis reutilizáveis
- Padrões consistentes

### 3. Performance
- CSS modular
- Imports otimizados
- Menos redundância

### 4. Escalabilidade
- Fácil adição de novos componentes
- Sistema extensível
- Documentação clara

## Migração

Para migrar do sistema antigo:

1. **Substitua** `style.css` por `main.css` no template base
2. **Mantenha** as classes existentes (são compatíveis)
3. **Adicione** novas classes utilitárias conforme necessário
4. **Refatore** gradualmente para usar as variáveis CSS

## Próximos Passos

1. **Testar** todos os componentes em diferentes dispositivos
2. **Otimizar** performance se necessário
3. **Adicionar** novos componentes conforme demanda
4. **Documentar** novos padrões

## Contribuição

Ao adicionar novos estilos:

1. **Use** as variáveis CSS existentes
2. **Siga** os padrões estabelecidos
3. **Documente** novos componentes
4. **Teste** em diferentes dispositivos
5. **Mantenha** a organização dos arquivos



