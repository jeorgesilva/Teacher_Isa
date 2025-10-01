#!/usr/bin/env python3
"""
Configurador de Google Drive OAuth
==================================

Este script configura o acesso ao Google Drive usando OAuth Client
(requer autorização manual uma vez, depois funciona automaticamente)
"""

import os
import json
import pickle
from pathlib import Path

def setup_oauth_google_drive():
    """Configura Google Drive com OAuth Client."""
    
    print("🔧 CONFIGURANDO GOOGLE DRIVE COM OAUTH")
    print("=" * 50)
    
    # Verificar se o arquivo OAuth existe
    oauth_file = Path("oauth_credentials.json")
    
    if not oauth_file.exists():
        print("❌ Arquivo oauth_credentials.json não encontrado!")
        print("📋 Instruções:")
        print("1. Acesse: https://console.cloud.google.com/")
        print("2. Crie credenciais OAuth 2.0 Client ID")
        print("3. Baixe o arquivo JSON")
        print("4. Renomeie para: oauth_credentials.json")
        print("5. Coloque neste diretório")
        return False
    
    print("✅ Arquivo oauth_credentials.json encontrado!")
    
    # Verificar conteúdo
    try:
        with open(oauth_file) as f:
            oauth_data = json.load(f)
        
        if 'installed' in oauth_data or 'web' in oauth_data:
            print("✅ Arquivo OAuth válido!")
        else:
            print("❌ Arquivo OAuth inválido!")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao ler OAuth file: {e}")
        return False
    
    print("\n🚀 CONFIGURAÇÃO AUTOMÁTICA")
    print("=" * 30)
    
    try:
        # Instalar dependências necessárias
        print("📦 Instalando dependências...")
        os.system("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
        print("✅ Dependências instaladas!")
        
        # Criar script de autorização OAuth
        oauth_script = '''
import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    """Autentica com Google Drive usando OAuth."""
    creds = None
    
    # Verificar se já temos token salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salvar credenciais para próxima execução
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

if __name__ == "__main__":
    print("🔐 Iniciando autenticação OAuth...")
    creds = authenticate()
    
    if creds:
        print("✅ Autenticação bem-sucedida!")
        
        # Testar acesso ao Google Drive
        try:
            service = build('drive', 'v3', credentials=creds)
            results = service.files().list(pageSize=5).execute()
            items = results.get('files', [])
            
            print(f"🎯 Acesso ao Google Drive confirmado!")
            print(f"📁 Arquivos encontrados: {len(items)}")
            
            if items:
                print("\\n📋 Primeiros arquivos:")
                for item in items[:3]:
                    print(f"  📄 {item['name']}")
            
            print("\\n🚀 Google Drive está pronto para usar!")
            
        except Exception as e:
            print(f"❌ Erro ao testar Google Drive: {e}")
    else:
        print("❌ Falha na autenticação!")
'''
        
        # Salvar script de autenticação
        with open("authenticate_oauth.py", "w") as f:
            f.write(oauth_script)
        
        print("✅ Script de autenticação criado!")
        
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("=" * 20)
        print("1. Execute: python authenticate_oauth.py")
        print("2. Será aberto um navegador para autorização")
        print("3. Faça login com sua conta Google")
        print("4. Autorize o acesso ao Google Drive")
        print("5. Após autorização, o token será salvo automaticamente")
        print("6. Execute o Teacher Isa Bot normalmente!")
        
        print("\n💡 NOTA:")
        print("A autorização é necessária apenas UMA VEZ.")
        print("Depois disso, o bot funcionará automaticamente!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False

if __name__ == "__main__":
    setup_oauth_google_drive()