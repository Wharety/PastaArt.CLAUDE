#!/usr/bin/env python3
"""
Script para upload e verificação do Google Search Console
PastaArt Encanto - https://www.pastaart.com.br
"""

import os
import shutil
from pathlib import Path

def print_header():
    """Imprime o cabeçalho do script"""
    print("=" * 60)
    print("🚀 UPLOAD VERIFICAÇÃO GOOGLE SEARCH CONSOLE")
    print("   PastaArt Encanto - pastaart.com.br")
    print("=" * 60)

def verify_files():
    """Verifica se os arquivos de verificação existem"""
    files_to_check = [
        "google96c321be4f1469b2.html",
        "static/google96c321be4f1469b2.html",
        "google-verification.html"
    ]
    
    print("📋 Verificando arquivos de verificação:")
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (não encontrado)")
    
    return True

def show_upload_instructions():
    """Mostra instruções para upload"""
    print("\n" + "=" * 60)
    print("📤 INSTRUÇÕES PARA UPLOAD")
    print("=" * 60)
    
    instructions = [
        "1. 📁 Arquivo para upload:",
        "   Nome: google96c321be4f1469b2.html",
        "   Conteúdo: google-site-verification: google96c321be4f1469b2.html",
        "",
        "2. 🌐 Acesse o painel da sua hospedagem:",
        "   - cPanel, Plesk, ou painel da sua hospedagem",
        "   - Navegue até o gerenciador de arquivos",
        "",
        "3. 📂 Vá para a pasta raiz do site:",
        "   - Pasta: public_html/",
        "   - Esta é a pasta onde está o index.html do seu site",
        "",
        "4. 📤 Faça upload do arquivo:",
        "   - Faça upload do arquivo google96c321be4f1469b2.html",
        "   - Certifique-se que está na pasta public_html/",
        "",
        "5. ✅ Teste a acessibilidade:",
        "   - Acesse: https://www.pastaart.com.br/google96c321be4f1469b2.html",
        "   - Deve mostrar: google-site-verification: google96c321be4f1469b2.html",
        "",
        "6. 🎯 Finalize no Google Search Console:",
        "   - Volte ao Google Search Console",
        "   - Clique em 'Verificar'",
        "   - Aguarde a confirmação de sucesso"
    ]
    
    for instruction in instructions:
        print(instruction)

def show_verification_urls():
    """Mostra URLs para teste"""
    print("\n" + "=" * 60)
    print("🔗 URLs PARA TESTE")
    print("=" * 60)
    
    urls = [
        "🌐 URL principal:",
        "   https://www.pastaart.com.br/google96c321be4f1469b2.html",
        "",
        "📱 URLs alternativas (se necessário):",
        "   https://pastaart.com.br/google96c321be4f1469b2.html",
        "   https://www.pastaart.com.br/google-verification.html",
        "",
        "✅ Resultado esperado:",
        "   google-site-verification: google96c321be4f1469b2.html"
    ]
    
    for url in urls:
        print(url)

def show_troubleshooting():
    """Mostra soluções para problemas comuns"""
    print("\n" + "=" * 60)
    print("🆘 SOLUÇÃO DE PROBLEMAS")
    print("=" * 60)
    
    problems = [
        "❌ Arquivo não carrega:",
        "   - Verifique se o upload foi feito na pasta correta",
        "   - Confirme que o nome do arquivo está exato",
        "   - Aguarde alguns minutos e tente novamente",
        "",
        "❌ Verificação falha:",
        "   - Verifique se o conteúdo do arquivo está correto",
        "   - Confirme que não há espaços extras",
        "   - Teste a URL diretamente no navegador",
        "",
        "❌ Erro 404:",
        "   - O arquivo não está na pasta correta",
        "   - Verifique se está em public_html/",
        "   - Confirme o nome do arquivo",
        "",
        "❌ Erro 403:",
        "   - Problema de permissões no servidor",
        "   - Entre em contato com o suporte da hospedagem"
    ]
    
    for problem in problems:
        print(problem)

def main():
    """Função principal"""
    print_header()
    
    # Verificar arquivos
    verify_files()
    
    # Mostrar instruções
    show_upload_instructions()
    
    # Mostrar URLs para teste
    show_verification_urls()
    
    # Mostrar solução de problemas
    show_troubleshooting()
    
    print("\n" + "=" * 60)
    print("🎉 Arquivo pronto para upload!")
    print("📁 Arquivo: google96c321be4f1469b2.html")
    print("📄 Conteúdo: google-site-verification: google96c321be4f1469b2.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
