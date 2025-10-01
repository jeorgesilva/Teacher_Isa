#!/usr/bin/env python3
"""
Explorador do Google Drive
=========================

Script para explorar a estrutura do Google Drive e encontrar a pasta correta com vídeos.
"""

import os
import pickle
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def explore_google_drive():
    """Explora o Google Drive para encontrar pastas e vídeos."""
    
    print("🔍 Explorando Google Drive...")
    
    # Carregar credenciais
    if not os.path.exists('token.pickle'):
        print("❌ Token não encontrado! Execute authenticate_oauth.py primeiro.")
        return
    
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)
    
    # Criar service
    service = build('drive', 'v3', credentials=credentials)
    
    print("\n📁 PASTAS ENCONTRADAS:")
    print("=" * 50)
    
    # Buscar pastas
    folders_query = "mimeType='application/vnd.google-apps.folder'"
    folders_result = service.files().list(
        q=folders_query,
        pageSize=20,
        fields="files(id, name, parents)"
    ).execute()
    
    folders = folders_result.get('files', [])
    
    for i, folder in enumerate(folders, 1):
        print(f"{i}. 📁 {folder['name']}")
        print(f"   ID: {folder['id']}")
        
        # Verificar se há vídeos nesta pasta
        videos_query = f"'{folder['id']}' in parents and (mimeType contains 'video/')"
        videos_result = service.files().list(
            q=videos_query,
            pageSize=5,
            fields="files(id, name, size)"
        ).execute()
        
        videos = videos_result.get('files', [])
        if videos:
            print(f"   🎬 {len(videos)} vídeo(s) encontrado(s):")
            for video in videos[:3]:  # Mostrar apenas 3 primeiros
                size_mb = int(video.get('size', 0)) / (1024 * 1024) if video.get('size') else 0
                print(f"     • {video['name']} ({size_mb:.1f} MB)")
        else:
            print(f"   📂 Pasta vazia ou sem vídeos")
        print()
    
    print("\n🎬 TODOS OS VÍDEOS ENCONTRADOS:")
    print("=" * 50)
    
    # Buscar todos os vídeos (não importa a pasta)
    all_videos_query = "mimeType contains 'video/'"
    all_videos_result = service.files().list(
        q=all_videos_query,
        pageSize=50,
        fields="files(id, name, size, parents)"
    ).execute()
    
    all_videos = all_videos_result.get('files', [])
    
    if all_videos:
        print(f"Total de vídeos encontrados: {len(all_videos)}")
        print()
        
        # Agrupar por pasta
        videos_by_folder = {}
        
        for video in all_videos:
            size_mb = int(video.get('size', 0)) / (1024 * 1024) if video.get('size') else 0
            
            # Encontrar pasta pai
            parent_id = video.get('parents', ['root'])[0] if video.get('parents') else 'root'
            
            # Buscar nome da pasta pai
            if parent_id != 'root':
                try:
                    parent = service.files().get(fileId=parent_id, fields="name").execute()
                    parent_name = parent.get('name', 'Unknown')
                except:
                    parent_name = f"ID: {parent_id}"
            else:
                parent_name = "Raiz do Drive"
            
            if parent_name not in videos_by_folder:
                videos_by_folder[parent_name] = []
            
            videos_by_folder[parent_name].append({
                'name': video['name'],
                'size_mb': size_mb,
                'parent_id': parent_id
            })
        
        # Mostrar vídeos agrupados por pasta
        for folder_name, videos in videos_by_folder.items():
            print(f"📁 {folder_name}:")
            for video in videos[:5]:  # Limit to 5 videos per folder
                print(f"   🎬 {video['name']} ({video['size_mb']:.1f} MB)")
            if len(videos) > 5:
                print(f"   ... e mais {len(videos) - 5} vídeo(s)")
            print(f"   📊 Total: {len(videos)} vídeo(s)")
            
            # Se esta pasta tem vídeos, mostrar como usar
            if videos and folder_name != "Raiz do Drive":
                sample_video = videos[0]
                folder_id = sample_video['parent_id']
                print(f"   🔧 Para usar esta pasta, configure FOLDER_ID = '{folder_id}'")
            print()
    else:
        print("❌ Nenhum vídeo encontrado em todo o Google Drive!")
    
    print("\n💡 INSTRUÇÕES:")
    print("=" * 20)
    print("1. Identifique a pasta com vídeos que você quer usar")
    print("2. Copie o ID da pasta (FOLDER_ID)")
    print("3. Atualize a configuração no Teacher Isa Bot")
    print("4. Execute o bot!")

if __name__ == "__main__":
    explore_google_drive()