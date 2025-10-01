#!/usr/bin/env python3
"""
Verificador de Credenciais do Google Drive
==========================================

Script simples para verificar se as credenciais estão configuradas corretamente.
"""

import os
import json
from pathlib import Path

def check_google_drive_credentials():
    """Verifica se as credenciais do Google Drive estão configuradas."""
    
    print("🔍 VERIFICAÇÃO DE CREDENCIAIS - GOOGLE DRIVE")
    print("=" * 50)
    
    # Verificar arquivo local
    credential_files = [
        "google_credentials.json",
        "credentials.json"
    ]
    
    print("1️⃣ Verificando arquivos de credenciais locais...")
    
    for cred_file in credential_files:
        if os.path.exists(cred_file):
            print(f"   ✅ Encontrado: {cred_file}")
            
            # Tentar ler e validar o arquivo
            try:
                with open(cred_file, 'r') as f:
                    creds = json.load(f)
                
                # Verificar campos obrigatórios
                required_fields = [
                    'type', 'project_id', 'private_key_id', 'private_key',
                    'client_email', 'client_id', 'auth_uri', 'token_uri'
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in creds:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"   ❌ Arquivo inválido - campos ausentes: {missing_fields}")
                else:
                    print(f"   ✅ Arquivo válido!")
                    print(f"   📧 Service Account: {creds.get('client_email', 'N/A')}")
                    print(f"   🔧 Project ID: {creds.get('project_id', 'N/A')}")
                    
                    return True, creds.get('client_email')
                    
            except json.JSONDecodeError:
                print(f"   ❌ Erro: {cred_file} não é um JSON válido")
            except Exception as e:
                print(f"   ❌ Erro ao ler {cred_file}: {e}")
        else:
            print(f"   ❌ Não encontrado: {cred_file}")
    
    print()
    print("2️⃣ Verificando variável de ambiente...")
    
    env_creds = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
    if env_creds:
        try:
            creds = json.loads(env_creds)
            print("   ✅ Credenciais encontradas em GOOGLE_DRIVE_CREDENTIALS")
            print(f"   📧 Service Account: {creds.get('client_email', 'N/A')}")
            return True, creds.get('client_email')
        except json.JSONDecodeError:
            print("   ❌ GOOGLE_DRIVE_CREDENTIALS não é um JSON válido")
    else:
        print("   ❌ Variável GOOGLE_DRIVE_CREDENTIALS não definida")
    
    print()
    print("❌ NENHUMA CREDENCIAL ENCONTRADA!")
    print()
    
    return False, None

def show_setup_instructions():
    """Mostra instruções de configuração."""
    print("📋 COMO CONFIGURAR AS CREDENCIAIS:")
    print("=" * 50)
    print()
    print("🔧 MÉTODO RECOMENDADO - Arquivo Local:")
    print("1. Siga as instruções em GOOGLE_DRIVE_SETUP.md")
    print("2. Baixe o arquivo JSON das credenciais do Google Cloud Console")
    print("3. Renomeie para 'google_credentials.json'")
    print("4. Coloque na mesma pasta do bot")
    print()
    print("🌐 MÉTODO ALTERNATIVO - Variável de Ambiente:")
    print("1. Defina a variável GOOGLE_DRIVE_CREDENTIALS")
    print("2. Valor deve ser o conteúdo completo do arquivo JSON")
    print()
    print("📝 PASSOS PRINCIPAIS:")
    print("1. Criar projeto no Google Cloud Console")
    print("2. Ativar Google Drive API")
    print("3. Criar Service Account")
    print("4. Baixar credenciais JSON")
    print("5. Compartilhar pasta do Google Drive com o Service Account")
    print()
    print("📁 Sua pasta Google Drive:")
    print("   https://drive.google.com/drive/folders/1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc")
    print()
    print("✅ Depois de configurar, execute: python test_google_drive.py")

def main():
    """Função principal."""
    print()
    
    has_credentials, service_email = check_google_drive_credentials()
    
    print()
    if has_credentials:
        print("🎉 CREDENCIAIS CONFIGURADAS COM SUCESSO!")
        print()
        print("📧 Service Account Email:", service_email)
        print()
        print("🔗 PRÓXIMOS PASSOS:")
        print("1. Compartilhe sua pasta Google Drive com este email:")
        print(f"   {service_email}")
        print("2. Dê permissão 'Viewer' (apenas visualizar)")
        print("3. Execute: python test_google_drive.py")
        print("4. Execute o bot: python teacher_isa_bot.py")
        print()
        print("✅ O bot já deve conseguir acessar o Google Drive!")
        
    else:
        show_setup_instructions()
        print()
        print("⚠️  Execute este script novamente depois de configurar as credenciais")

if __name__ == "__main__":
    main()