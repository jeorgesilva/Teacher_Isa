#!/usr/bin/env python3
"""
Google Drive Manager - OAuth Version
====================================

Gerenciador de vídeos do Google Drive usando OAuth Client
(versão atualizada para funcionar com oauth_credentials.json)
"""

import os
import asyncio
import pickle
import logging
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import tempfile

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

logger = logging.getLogger(__name__)

def extract_folder_id_from_url(drive_url):
    """Extrai o ID da pasta do Google Drive da URL."""
    try:
        if '/drive/folders/' in drive_url:
            folder_id = drive_url.split('/drive/folders/')[1].split('?')[0]
            return folder_id
        elif 'id=' in drive_url:
            parsed = urlparse(drive_url)
            params = parse_qs(parsed.query)
            return params.get('id', [None])[0]
        else:
            logger.warning(f"URL não reconhecida: {drive_url}")
            return None
    except Exception as e:
        logger.error(f"Erro ao extrair folder ID: {e}")
        return None

class GoogleDriveManager:
    """Gerenciador de vídeos do Google Drive com OAuth."""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, folder_id=None):
        """
        Inicializa o gerenciador do Google Drive.
        
        Args:
            folder_id (str): ID da pasta do Google Drive
        """
        self.folder_id = folder_id
        self.service = None
        self.cache_dir = Path("video_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.credentials = None
        self.max_cache_size_mb = 200  # Limite do cache em MB
        
    async def initialize(self):
        """Inicializa conexão com Google Drive usando OAuth."""
        try:
            # Carregar credenciais salvas
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Se credenciais inválidas ou expiradas, reautenticar
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    # Tentar autenticação apenas se arquivo OAuth existe
                    if os.path.exists('oauth_credentials.json'):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'oauth_credentials.json', self.SCOPES)
                        self.credentials = flow.run_local_server(port=0)
                    else:
                        logger.error("❌ Arquivo oauth_credentials.json não encontrado!")
                        return False
                
                # Salvar credenciais para uso futuro
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.credentials, token)
            
            # Criar service do Google Drive
            self.service = build('drive', 'v3', credentials=self.credentials)
            
            # Testar conexão
            test_result = self.service.files().list(pageSize=1).execute()
            
            logger.info("✅ Google Drive conectado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Google Drive: {e}")
            return False
    
    async def sync_videos(self, force=False):
        """Sincroniza lista de vídeos da pasta especificada."""
        if not self.service or not self.folder_id:
            logger.warning("⚠️ Google Drive não inicializado ou folder_id não definido")
            return []
        
        try:
            # Buscar vídeos na pasta
            query = f"'{self.folder_id}' in parents and (mimeType contains 'video/')"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, size, createdTime, mimeType)"
            ).execute()
            
            videos = results.get('files', [])
            
            logger.info(f"📹 Encontrados {len(videos)} vídeos na pasta Google Drive")
            
            # Adicionar informação de cache
            for video in videos:
                cache_path = self.cache_dir / f"{video['id']}.mp4"
                video['cached'] = cache_path.exists()
                video['cache_path'] = str(cache_path)
            
            return videos
            
        except Exception as e:
            logger.error(f"❌ Erro ao sincronizar vídeos: {e}")
            return []
    
    async def download_video(self, video_info):
        """Baixa um vídeo específico para o cache local."""
        try:
            video_id = video_info['id']
            video_name = video_info['name']
            cache_path = self.cache_dir / f"{video_id}.mp4"
            
            # Se já está em cache, retornar path
            if cache_path.exists():
                logger.info(f"📁 Vídeo já em cache: {video_name}")
                return str(cache_path)
            
            logger.info(f"⬇️ Baixando vídeo: {video_name}")
            
            # Baixar o arquivo
            request = self.service.files().get_media(fileId=video_id)
            file_buffer = io.BytesIO()
            downloader = MediaIoBaseDownload(file_buffer, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                if status:
                    logger.debug(f"📊 Download progress: {int(status.progress() * 100)}%")
            
            # Salvar no cache
            with open(cache_path, 'wb') as f:
                f.write(file_buffer.getvalue())
            
            logger.info(f"✅ Vídeo baixado: {cache_path}")
            return str(cache_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao baixar vídeo {video_info.get('name', 'Unknown')}: {e}")
            return None
    
    async def get_random_video(self):
        """Obtém um vídeo aleatório, baixando se necessário."""
        try:
            # Sincronizar lista de vídeos
            videos = await self.sync_videos()
            
            if not videos:
                logger.warning("⚠️ Nenhum vídeo encontrado na pasta Google Drive")
                return None
            
            # Selecionar vídeo aleatório
            import random
            selected_video = random.choice(videos)
            
            # Baixar se não estiver em cache
            video_path = await self.download_video(selected_video)
            
            if video_path and os.path.exists(video_path):
                logger.info(f"🎬 Vídeo selecionado: {selected_video['name']}")
                return video_path
            else:
                logger.error("❌ Falha ao obter vídeo")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro em get_random_video: {e}")
            return None
    
    async def cleanup_cache(self, max_size_mb=None):
        """Limpa cache antigo para manter dentro do limite de tamanho."""
        try:
            if max_size_mb is None:
                max_size_mb = self.max_cache_size_mb
            
            # Obter todos os arquivos do cache
            cache_files = []
            total_size = 0
            
            for file_path in self.cache_dir.glob("*.mp4"):
                if file_path.is_file():
                    stat = file_path.stat()
                    cache_files.append({
                        'path': file_path,
                        'size': stat.st_size,
                        'mtime': stat.st_mtime
                    })
                    total_size += stat.st_size
            
            total_size_mb = total_size / (1024 * 1024)
            
            if total_size_mb <= max_size_mb:
                logger.info(f"📊 Cache dentro do limite: {total_size_mb:.1f}MB / {max_size_mb}MB")
                return
            
            # Ordenar por data de modificação (mais antigos primeiro)
            cache_files.sort(key=lambda x: x['mtime'])
            
            # Remover arquivos mais antigos até ficar dentro do limite
            removed_count = 0
            for file_info in cache_files:
                if total_size_mb <= max_size_mb:
                    break
                
                file_size_mb = file_info['size'] / (1024 * 1024)
                file_info['path'].unlink()
                total_size_mb -= file_size_mb
                removed_count += 1
                
                logger.info(f"🗑️ Removido do cache: {file_info['path'].name} ({file_size_mb:.1f}MB)")
            
            if removed_count > 0:
                logger.info(f"🧹 Cache limpo: {removed_count} arquivos removidos, {total_size_mb:.1f}MB restantes")
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache: {e}")
    
    async def get_cache_stats(self):
        """Obtém estatísticas do cache."""
        try:
            files = list(self.cache_dir.glob("*.mp4"))
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            total_size_mb = total_size / (1024 * 1024)
            
            return {
                'files': len(files),
                'size_mb': round(total_size_mb, 1)
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas do cache: {e}")
            return {'files': 0, 'size_mb': 0}

# Função de teste
async def test_google_drive():
    """Testa a conexão e funcionalidades do Google Drive."""
    print("🧪 Testando Google Drive Manager...")
    
    # ID da pasta de exemplo
    FOLDER_ID = "1KslzJkbExVY8X2ZifP6YGiM62BxNRSyc"
    
    manager = GoogleDriveManager(FOLDER_ID)
    
    # Testar inicialização
    success = await manager.initialize()
    if not success:
        print("❌ Falha na inicialização")
        return
    
    print("✅ Inicialização bem-sucedida!")
    
    # Testar sincronização
    videos = await manager.sync_videos()
    print(f"📹 Vídeos encontrados: {len(videos)}")
    
    for i, video in enumerate(videos[:3]):  # Mostrar apenas 3 primeiros
        print(f"  {i+1}. {video['name']} ({'cached' if video['cached'] else 'not cached'})")
    
    # Testar download de vídeo aleatório
    if videos:
        print("\n🎲 Testando download de vídeo aleatório...")
        video_path = await manager.get_random_video()
        if video_path:
            print(f"✅ Vídeo baixado: {video_path}")
        else:
            print("❌ Falha no download")
    
    # Estatísticas do cache
    stats = await manager.get_cache_stats()
    print(f"\n📊 Cache: {stats['files']} arquivos, {stats['size_mb']} MB")

if __name__ == "__main__":
    asyncio.run(test_google_drive())