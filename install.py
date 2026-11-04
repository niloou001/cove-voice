"""Instala o ouvinte no perfil do usuario, sem exigir administrador."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import venv
import zipfile

MODEL = 'vosk-model-small-pt-0.3'
MODEL_URL = f'https://alphacephei.com/vosk/models/{MODEL}.zip'

def install():
    if sys.platform != 'win32' or sys.version_info < (3, 10):
        raise SystemExit('Requer Windows e Python 3.10 ou superior.')
    source = Path(__file__).resolve().parent
    target = Path(os.environ['LOCALAPPDATA']) / 'Cove'
    target.mkdir(parents=True, exist_ok=True)
    print('Criando ambiente Python...', flush=True)
    venv.create(target / 'venv', with_pip=True)
    python = target / 'venv' / 'Scripts' / 'python.exe'
    subprocess.run([str(python), '-m', 'pip', 'install', '--no-cache-dir', '-r', str(source / 'requirements.txt')], check=True)
    if not (target / MODEL / 'am' / 'final.mdl').is_file():
        print('Baixando modelo de portugues (aproximadamente 31 MB)...', flush=True)
        archive = target / 'model.zip'
        try:
            with urllib.request.urlopen(MODEL_URL, timeout=120) as response, archive.open('wb') as output:
                shutil.copyfileobj(response, output)
            with zipfile.ZipFile(archive) as model:
                for member in model.infolist():
                    resolved = (target / member.filename).resolve()
                    if not resolved.is_relative_to(target.resolve()):
                        raise ValueError('Caminho invalido no arquivo do modelo.')
                model.extractall(target)
        finally:
            archive.unlink(missing_ok=True)
    for name in ('listener.py', 'start.ps1', 'Cove.bat'):
        shutil.copy2(source / name, target / name)
    subprocess.run([str(python), str(target / 'listener.py'), '--test'], check=True)
    print(f'Arquivos instalados em {target}', flush=True)

if __name__ == '__main__':
    install()
