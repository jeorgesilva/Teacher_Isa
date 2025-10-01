#!/usr/bin/env python3
"""
Autenticação OAuth para Servidor (sem navegador)
===============================================

Script modificado para funcionar em VM/servidor sem interface gráfica.
"""

import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_server():
    """Autentica com Google Drive usando OAuth sem navegador."""
    creds = None
    
    # Verificar se já temos token salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, fazer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                print("✅ Token renovado automaticamente!")
            except Exception as e:
                print(f"❌ Erro ao renovar token: {e}")
                creds = None
        
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json', SCOPES)
            
            # Configurar para autenticação manual (sem navegador)
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            
            # Obter URL de autorização
            auth_url, _ = flow.authorization_url(prompt='consent')
            
            print("\n🌐 AUTORIZAÇÃO NECESSÁRIA:")
            print("=" * 60)
            print("1. Copie esta URL e abra no seu navegador:")
            print(f"\n{auth_url}\n")
            print("2. Faça login com sua conta Google")
            print("3. Autorize o acesso ao Google Drive")
            print("4. Copie o código de autorização que aparecer")
            print("=" * 60)
            
            # Solicitar código de autorização
            auth_code = input("Cole o código de autorização aqui: ").strip()
            
            # Obter credenciais com o código
            try:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                print("✅ Autenticação bem-sucedida!")
            except Exception as e:
                print(f"❌ Erro na autenticação: {e}")
                return None
        
        # Salvar credenciais para próxima execução
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def test_drive_access(creds):
    """Testa acesso ao Google Drive."""
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5).execute()
        items = results.get('files', [])
        
        print(f"\n🎯 Acesso ao Google Drive confirmado!")
        print(f"📁 Arquivos encontrados: {len(items)}")
        
        if items:
            print("\n📋 Primeiros arquivos:")
            for item in items[:3]:
                print(f"  📄 {item['name']}")
        
        print("\n🚀 Google Drive está pronto para usar!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Google Drive: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Iniciando autenticação OAuth para servidor...")
    
    # Verificar se arquivo de credenciais existe
    if not os.path.exists('oauth_credentials.json'):
        print("❌ Arquivo oauth_credentials.json não encontrado!")
        print("Certifique-se de que o arquivo está no diretório atual.")
        exit(1)
    
    # Autenticar
    creds = authenticate_server()
    
    if creds:
        # Testar acesso
        success = test_drive_access(creds)
        
        if success:
            print("\n✅ CONFIGURAÇÃO COMPLETA!")
            print("Agora você pode executar o Teacher Isa Bot:")
            print("python3 teacher_isa_bot.py")
        else:
            print("\n❌ Falha no teste do Google Drive")
    else:
        print("❌ Falha na autenticação!")