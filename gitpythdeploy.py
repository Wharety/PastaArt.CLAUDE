#!/usr/bin/env python3
"""
Script para executar comandos git de deploy automaticamente.
Executa: git add . && git commit -m "fix" && git push origin main
"""

import subprocess
import sys
import os

def run_command(command):
    """Executa um comando no terminal e retorna o resultado."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        print(f"✓ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Erro ao executar: {command}")
        print(f"Código de erro: {e.returncode}")
        if e.stderr:
            print(f"Erro: {e.stderr}")
        return False

def main():
    """Função principal que executa os comandos git."""
    print("🚀 Iniciando deploy automático...")
    print("-" * 40)
    
    # Verifica se estamos em um repositório git
    if not os.path.exists('.git'):
        print("❌ Erro: Este diretório não é um repositório git!")
        sys.exit(1)
    
    # Lista de comandos para executar
    commands = [
        "git add .",
        'git commit -m "fix"',
        "git push origin main"
    ]
    
    # Executa cada comando
    for command in commands:
        if not run_command(command):
            print(f"❌ Deploy interrompido devido a erro no comando: {command}")
            sys.exit(1)
    
    print("-" * 40)
    print("✅ Deploy concluído com sucesso!")

if __name__ == "__main__":
    main()
