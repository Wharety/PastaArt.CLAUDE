#!/usr/bin/env python3
"""
Script para gerar favicons em diferentes tamanhos a partir de uma imagem fonte
(SVG ou PNG). Mantém o restante do projeto inalterado.
"""

import sys
from pathlib import Path


def detect_source_image() -> Path:
    """Detecta o arquivo de origem do favicon.

    Prioridade:
    1) static/images/favicon-source.png (nova imagem enviada)
    2) static/images/favicon.svg (legado)
    """
    png_source = Path("static/images/favicon-source.png")
    svg_source = Path("static/images/favicon.svg")

    if png_source.exists():
        return png_source
    return svg_source


def generate_favicons() -> bool:
    """Gera favicons nos tamanhos necessários a partir do arquivo fonte."""

    output_dir = Path("static/images")

    # Tamanhos a gerar (somente favicons / ícones, nada além disso)
    sizes = {
        "favicon-16x16.png": 16,
        "favicon-32x32.png": 32,
        "favicon-48x48.png": 48,
        "favicon-64x64.png": 64,
        "favicon-128x128.png": 128,
        "favicon-256x256.png": 256,
        "apple-touch-icon.png": 180,
        "favicon-192x192.png": 192,
        "favicon-512x512.png": 512,
    }

    source_path = detect_source_image()
    if not source_path.exists():
        print(f"❌ Erro: arquivo de origem não encontrado: {source_path}")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        if source_path.suffix.lower() == ".svg":
            # Converter a partir de SVG (usa cairosvg se disponível)
            try:
                import cairosvg  # type: ignore
            except ImportError:
                print("❌ Erro: cairosvg não está instalado para converter SVG → PNG")
                print("📦 Instale com: pip install cairosvg")
                return False

            print("🎨 Gerando favicons a partir do SVG...")
            for filename, size in sizes.items():
                output_path = output_dir / filename
                cairosvg.svg2png(
                    url=str(source_path),
                    write_to=str(output_path),
                    output_width=size,
                    output_height=size,
                )
                print(f"✅ {filename} ({size}x{size})")
        else:
            # Converter a partir de PNG (usa Pillow)
            try:
                from PIL import Image  # type: ignore
            except ImportError:
                print("❌ Erro: Pillow não está instalado para converter PNG → PNG")
                print("📦 Instale com: pip install Pillow")
                return False

            print("🎨 Gerando favicons a partir do PNG...")
            with Image.open(source_path) as img:
                for filename, size in sizes.items():
                    output_path = output_dir / filename
                    resized = img.convert("RGBA").resize((size, size), Image.LANCZOS)
                    resized.save(output_path, format="PNG")
                    print(f"✅ {filename} ({size}x{size})")

        print("\n🎉 Favicons gerados com sucesso!")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Erro ao gerar favicons: {exc}")
        return False


def create_ico_file() -> bool:
    """Cria `favicon.ico` com múltiplos tamanhos (16/32/48)."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        print("⚠️  Pillow não instalado - favicon.ico não será criado")
        print("📦 Instale com: pip install Pillow")
        return False

    output_dir = Path("static/images")
    ico_path = output_dir / "favicon.ico"
    sizes = [
        (16, 16),
        (32, 32),
        (48, 48),
    ]

    try:
        # Prioriza gerar ICO a partir da melhor origem disponível
        source_path = detect_source_image()
        with Image.open(source_path) as img:
            frames = [img.convert("RGBA").resize(size, Image.LANCZOS) for size in sizes]
            frames[0].save(ico_path, format="ICO", sizes=sizes)
        print("✅ favicon.ico criado")
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Erro ao criar ICO: {exc}")
        return False


def main() -> None:
    print("🍫 PastaArt Encanto - Gerador de Favicons")
    print("=" * 50)

    # Gera favicons PNG
    if generate_favicons():
        # Tenta criar ICO
        create_ico_file()

        print("\n📋 Próximos passos:")
        print("1. Limpe o cache do navegador (ou use uma janela anônima)")
        print("2. Verifique se os ícones aparecem corretamente nas páginas")
        print("3. Em dispositivos Apple, confira o atalho na tela inicial (180x180)")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
