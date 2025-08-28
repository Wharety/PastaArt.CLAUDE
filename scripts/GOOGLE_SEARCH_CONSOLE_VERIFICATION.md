# 🔍 Verificação Google Search Console - PastaArt Encanto

Este guia explica como verificar a propriedade do site **pastaart.com.br** no Google Search Console.

## 📋 Pré-requisitos

- Acesso ao painel de controle da sua hospedagem
- Acesso ao Google Search Console
- Conta Google válida

## 🎯 Método Recomendado: Arquivo HTML

### Passo 1: Acessar Google Search Console
1. Acesse: https://search.google.com/search-console
2. Faça login com sua conta Google
3. Clique em "Adicionar propriedade"

### Passo 2: Adicionar Propriedade
1. Digite: `https://www.pastaart.com.br/`
2. Clique em "Continuar"

### Passo 3: Escolher Método de Verificação
1. Selecione **"Arquivo HTML"** (método recomendado)
2. Clique na seta para expandir as instruções
3. Baixe o arquivo de verificação fornecido pelo Google

### Passo 4: Preparar Arquivo
1. Abra o arquivo `static/google-verification.html` neste projeto
2. **Substitua todo o conteúdo** pelo conteúdo do arquivo baixado do Google
3. Salve o arquivo

### Passo 5: Fazer Upload
1. Acesse o painel de controle da sua hospedagem
2. Navegue até a pasta `public_html` (raiz do site)
3. Faça upload do arquivo `google-verification.html`
4. Certifique-se que o arquivo está na raiz do site

### Passo 6: Verificar Acessibilidade
1. Teste se o arquivo está acessível em:
   ```
   https://www.pastaart.com.br/google-verification.html
   ```
2. O arquivo deve carregar normalmente no navegador

### Passo 7: Finalizar Verificação
1. Volte ao Google Search Console
2. Clique em **"Verificar"**
3. Aguarde a confirmação de verificação bem-sucedida

## 🔄 Métodos Alternativos

### 📌 Tag HTML (Meta tag)
Se preferir usar uma meta tag:

1. No Google Search Console, escolha "Tag HTML"
2. Copie a meta tag fornecida
3. Adicione no `<head>` do arquivo `templates/base.html`:

```html
<meta name="google-site-verification" content="SEU_CODIGO_AQUI" />
```

### 📊 Google Analytics
Se já tem Google Analytics configurado:

1. No Google Search Console, escolha "Google Analytics"
2. Selecione sua conta do GA
3. Siga as instruções para vincular

### 🏷️ Google Tag Manager
Se usa GTM:

1. No Google Search Console, escolha "Google Tag Manager"
2. Selecione sua conta do GTM
3. Siga as instruções para configuração

### 🌐 Provedor de Domínio (DNS)
Para configuração via DNS:

1. No Google Search Console, escolha "Provedor do nome de domínio"
2. Adicione o registro TXT fornecido no painel da sua hospedagem
3. Aguarde a propagação do DNS (pode levar até 24h)

## 🛠️ Scripts de Ajuda

### Executar Script de Verificação
```bash
cd scripts
python google_search_console_verification.py
```

Este script irá:
- Criar o arquivo de verificação
- Mostrar instruções detalhadas
- Explicar métodos alternativos

## ✅ Verificação de Sucesso

Após verificação bem-sucedida, você verá:
- ✅ Propriedade verificada no Google Search Console
- ✅ Acesso aos dados de SEO do site
- ✅ Capacidade de enviar sitemaps
- ✅ Monitoramento de erros de indexação

## 🧹 Limpeza (Opcional)

Após verificação bem-sucedida:
- Você pode remover o arquivo `google-verification.html` do servidor
- Ou mantê-lo para futuras verificações
- A verificação permanece ativa mesmo após remoção do arquivo

## 🆘 Solução de Problemas

### Arquivo não acessível
- Verifique se o upload foi feito na pasta correta (`public_html`)
- Confirme que o nome do arquivo está exato
- Teste a URL diretamente no navegador

### Verificação falhou
- Aguarde alguns minutos e tente novamente
- Verifique se o arquivo não tem caracteres especiais
- Confirme que o conteúdo foi substituído corretamente

### Erro de DNS
- Aguarde até 24h para propagação do DNS
- Verifique se o registro TXT foi adicionado corretamente
- Use ferramentas como `nslookup` para verificar

## 📞 Suporte

Se precisar de ajuda adicional:
- Consulte a documentação oficial do Google Search Console
- Verifique os logs de erro da sua hospedagem
- Entre em contato com o suporte da sua hospedagem

---

**PastaArt Encanto** - Doces Personalizados com Carinho ❤️
