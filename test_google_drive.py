#!/usr/bin/env python3
"""
Teste de Integração do Google Drive
===================================

Script para testar a conexão com Google Drive antes de rodar o bot completo.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)

from google_drive_manager import GoogleDriveManager, extract_folder_id_from_url

async def test_google_drive():
    """Testa integração completa com Google Drive."""
    
    print("🔧 TESTE DE INTEGRAÇÃO - GOOGLE DRIVE")
    print("=" * 50)
    
    # Configuração
    folder_url = "https://drive.google.com/drive/folders/1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc?usp=sharing"
    folder_id = "1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc"
    
    print(f"📁 Pasta Google Drive: {folder_url}")
    print(f"🆔 Folder ID: {folder_id}")
    print()
    
    try:
        # Verificar se credenciais existem
        print("1️⃣ Verificando credenciais...")
        
        credential_files = ["google_credentials.json", "credentials.json"]
        credentials_found = False
        
        for cred_file in credential_files:
            if os.path.exists(cred_file):
                print(f"   ✅ Encontrado: {cred_file}")
                credentials_found = True
                break
        
        if not credentials_found:
            env_creds = os.getenv('GOOGLE_DRIVE_CREDENTIALS')
            if env_creds:
                print("   ✅ Credenciais encontradas em variável de ambiente")
                credentials_found = True
        
        if not credentials_found:
            print("   ❌ ERRO: Credenciais não encontradas!")
            print("   📋 Veja GOOGLE_DRIVE_SETUP.md para instruções")
            return False
        
        print()
        
        # Inicializar Google Drive Manager
        print("2️⃣ Inicializando Google Drive Manager...")
        drive_manager = GoogleDriveManager(folder_id)
        
        success = await drive_manager.initialize()
        if not success:
            print("   ❌ ERRO: Falha na inicialização")
            return False
        
        print("   ✅ Google Drive Manager inicializado com sucesso!")
        print()
        
        # Testar sincronização
        print("3️⃣ Sincronizando vídeos...")
        videos = await drive_manager.sync_videos(force=True)
        
        print(f"   ✅ Encontrados {len(videos)} vídeos na pasta")
        
        if not videos:
            print("   ⚠️  AVISO: Nenhum vídeo encontrado na pasta!")
            print("   📝 Verifique se:")
            print("      - Pasta foi compartilhada com o Service Account")
            print("      - Há vídeos na pasta")
            print("      - Formatos são suportados (MP4, MOV, AVI, MKV, WebM, 3GP)")
            return False
        
        print()
        
        # Mostrar vídeos encontrados
        print("4️⃣ Vídeos disponíveis:")
        for i, video in enumerate(videos[:10], 1):  # Mostrar até 10
            size_mb = video.get('size', 0) / (1024 * 1024)
            cached = "📁 (cached)" if video.get('cached') else "🌐 (online)"
            print(f"   {i:2d}. {video['name'][:50]}... ({size_mb:.1f}MB) {cached}")
        
        if len(videos) > 10:
            print(f"   ... e mais {len(videos) - 10} vídeos")
        
        print()
        
        # Testar download
        print("5️⃣ Testando download de vídeo...")
        video_path = await drive_manager.get_random_video()
        
        if video_path and os.path.exists(video_path):
            video_name = os.path.basename(video_path)
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            
            print(f"   ✅ Download bem-sucedido!")
            print(f"   📹 Arquivo: {video_name}")
            print(f"   💾 Tamanho: {file_size:.1f} MB")
            print(f"   📁 Caminho: {video_path}")
        else:
            print("   ❌ ERRO: Falha no download do vídeo")
            return False
        
        print()
        
        # Estatísticas do cache
        print("6️⃣ Estatísticas do cache:")
        cache_stats = await drive_manager.get_cache_stats()
        
        print(f"   📁 Arquivos em cache: {cache_stats['files']}")
        print(f"   💾 Tamanho total: {cache_stats['size_mb']} MB")
        
        print()
        
        # Testar limpeza de cache
        print("7️⃣ Testando limpeza de cache...")
        await drive_manager.cleanup_cache(max_size_mb=100)
        
        new_cache_stats = await drive_manager.get_cache_stats()
        print(f"   ✅ Cache otimizado: {new_cache_stats['size_mb']} MB")
        
        print()
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("✅ Google Drive está configurado corretamente")
        print("🤖 O bot está pronto para usar vídeos do Google Drive")
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NO TESTE: {e}")
        logger.error(f"Erro detalhado: {e}", exc_info=True)
        return False

async def main():
    """Função principal do teste."""
    print("🚀 Iniciando teste do Google Drive...")
    print()
    
    try:
        success = await test_google_drive()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ INTEGRAÇÃO GOOGLE DRIVE: FUNCIONANDO")
            print("🎯 Próximos passos:")
            print("   1. Execute o bot: python teacher_isa_bot.py")
            print("   2. Use /drive_test para testar no bot")
            print("   3. Use /stats para monitorar")
            sys.exit(0)
        else:
            print("\n" + "=" * 50)
            print("❌ INTEGRAÇÃO GOOGLE DRIVE: COM PROBLEMAS")
            print("📋 Siga as instruções em GOOGLE_DRIVE_SETUP.md")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Teste interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Verificar se está no diretório correto
    if not os.path.exists("teacher_isa_bot.py"):
        print("❌ Execute este script na mesma pasta do teacher_isa_bot.py")
        sys.exit(1)
    
    # Executar teste
    asyncio.run(main())