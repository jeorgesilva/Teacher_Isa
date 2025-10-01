
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
                print("\n📋 Primeiros arquivos:")
                for item in items[:3]:
                    print(f"  📄 {item['name']}")
            
            print("\n🚀 Google Drive está pronto para usar!")
            
        except Exception as e:
            print(f"❌ Erro ao testar Google Drive: {e}")
    else:
        print("❌ Falha na autenticação!")
