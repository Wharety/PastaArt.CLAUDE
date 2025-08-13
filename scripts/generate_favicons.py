#!/usr/bin/env python3
"""
Script para gerar favicons em diferentes tamanhos a partir do SVG
Pasta Art Encanto - Sistema de Favicons
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import cairosvg
        return True
    except ImportError:
        print("❌ Erro: cairosvg não está instalado")
        print("📦 Instale com: pip install cairosvg")
        return False

def generate_favicons():
    """Gera favicons em diferentes tamanhos"""
    
    # Configurações
    svg_path = Path("static/images/favicon.svg")
    output_dir = Path("static/images")
    
    # Tamanhos para gerar
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "apple-touch-icon.png": 180,
        "favicon-192x192.png": 192,
        "favicon-512x512.png": 512
    }
    
    # Verifica se o SVG existe
    if not svg_path.exists():
        print(f"❌ Erro: {svg_path} não encontrado")
        return False
    
    # Cria diretório de saída se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        import cairosvg
        
        print("🎨 Gerando favicons...")
        
        for filename, size in sizes.items():
            output_path = output_dir / filename
            
            # Converte SVG para PNG
            cairosvg.svg2png(
                url=str(svg_path),
                write_to=str(output_path),
                output_width=size,
                output_height=size
            )
            
            print(f"✅ {filename} ({size}x{size})")
        
        print("\n🎉 Favicons gerados com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar favicons: {e}")
        return False

def create_ico_file():
    """Cria arquivo ICO a partir do PNG 32x32"""
    try:
        from PIL import Image
        
        png_path = Path("static/images/favicon-32x32.png")
        ico_path = Path("static/images/favicon.ico")
        
        if png_path.exists():
            # Abre o PNG e salva como ICO
            img = Image.open(png_path)
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48)])
            print("✅ favicon.ico criado")
            return True
        else:
            print("❌ favicon-32x32.png não encontrado")
            return False
            
    except ImportError:
        print("⚠️  PIL/Pillow não instalado - favicon.ico não será criado")
        print("📦 Instale com: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ Erro ao criar ICO: {e}")
        return False

def main():
    """Função principal"""
    print("🍫 Pasta Art Encanto - Gerador de Favicons")
    print("=" * 50)
    
    # Verifica dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Gera favicons PNG
    if generate_favicons():
        # Tenta criar ICO
        create_ico_file()
        
        print("\n📋 Próximos passos:")
        print("1. Teste os favicons no navegador")
        print("2. Verifique se aparecem corretamente")
        print("3. Teste em dispositivos móveis")
        print("4. Valide o PWA se necessário")
        
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
