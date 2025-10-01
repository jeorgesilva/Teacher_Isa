#!/usr/bin/env python3
"""
Setup Rápido Google Drive - Teacher Isa Bot
==========================================

Este script vai te ajudar a configurar o Google Drive usando sua API key existente.
"""

import os
import json

def create_temporary_solution():
    """Cria uma solução temporária usando a API key fornecida."""
    print("🔧 CONFIGURAÇÃO TEMPORÁRIA - GOOGLE DRIVE")
    print("=" * 50)
    print()
    
    # Sua API key
    api_key = "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"
    
    print("Você tem uma API key do Google, mas para o bot funcionar completamente,")
    print("precisamos de credenciais de Service Account (arquivo JSON).")
    print()
    print("🚀 SOLUÇÕES DISPONÍVEIS:")
    print()
    
    print("1️⃣ SOLUÇÃO RÁPIDA (5 minutos):")
    print("   - Criar Service Account no Google Cloud Console")
    print("   - Baixar arquivo JSON")
    print("   - Colocar na pasta do bot")
    print()
    
    print("2️⃣ CONFIGURAÇÃO MANUAL:")
    print("   - Use a API key atual como fallback")
    print("   - Configure Service Account depois")
    print()
    
    choice = input("Escolha (1 para Service Account, 2 para usar só API key atual): ").strip()
    
    if choice == "1":
        show_service_account_guide()
    else:
        create_api_key_fallback(api_key)

def show_service_account_guide():
    """Mostra guia para criar Service Account."""
    print()
    print("📋 GUIA RÁPIDO - SERVICE ACCOUNT:")
    print("=" * 40)
    print()
    print("1. Acesse: https://console.cloud.google.com/")
    print("2. Selecione seu projeto (ou crie um novo)")
    print("3. Ative a Google Drive API:")
    print("   - Menu: APIs & Services > Library")
    print("   - Procure: 'Google Drive API'")
    print("   - Clique: 'Enable'")
    print()
    print("4. Crie Service Account:")
    print("   - Menu: APIs & Services > Credentials")
    print("   - Clique: 'Create Credentials' > 'Service Account'")
    print("   - Nome: teacher-isa-bot")
    print("   - Clique: 'Create and Continue' > 'Done'")
    print()
    print("5. Baixe credenciais:")
    print("   - Clique no Service Account criado")
    print("   - Aba 'Keys' > 'Add Key' > 'Create new key'")
    print("   - Formato: JSON")
    print("   - Salve como: google_credentials.json")
    print()
    print("6. Compartilhe sua pasta Google Drive:")
    print("   - Email do Service Account estará no arquivo JSON")
    print("   - Adicione com permissão 'Viewer'")
    print()
    print("7. Coloque google_credentials.json na pasta do bot")
    print()
    print("✅ Depois execute: python check_credentials.py")

def create_api_key_fallback(api_key):
    """Cria configuração temporária com API key."""
    print()
    print("⚠️ USANDO API KEY COMO FALLBACK")
    print("=" * 40)
    print()
    
    # Criar arquivo de configuração temporária
    config = {
        "google_api_key": api_key,
        "note": "Esta é uma configuração temporária. Para funcionalidade completa, configure Service Account."
    }
    
    with open("google_config_temp.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Arquivo google_config_temp.json criado")
    print()
    print("🔄 Para funcionalidade completa do Google Drive:")
    print("1. Execute este script novamente")
    print("2. Escolha opção 1 (Service Account)")
    print("3. Siga o guia de 5 minutos")
    print()
    print("📱 Por enquanto, o bot funcionará com:")
    print("- Pasta local de vídeos (reels_content/)")
    print("- Todos os outros recursos normalmente")

def main():
    """Função principal."""
    print()
    print("🎓 TEACHER ISA BOT - SETUP GOOGLE DRIVE")
    print()
    
    try:
        create_temporary_solution()
    except KeyboardInterrupt:
        print("\n⏹️  Setup cancelado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()