"""
Limpar todas as sessões antigas
"""
from pathlib import Path
import shutil

sessions_dir = Path('out/sessions')

if sessions_dir.exists():
    print(f"Limpando sessões em: {sessions_dir}")
    
    # Listar todas as sessões
    sessions = list(sessions_dir.glob('*'))
    print(f"Total de sessões encontradas: {len(sessions)}")
    
    for session in sessions:
        if session.is_dir():
            print(f"  Removendo: {session.name}")
            shutil.rmtree(session)
    
    print("\n✅ Todas as sessões foram removidas!")
    print("Agora faça upload do arquivo ABZ novamente na interface web.")
else:
    print(f"❌ Diretório de sessões não encontrado: {sessions_dir}")

