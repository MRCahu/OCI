#!/usr/bin/env python3
"""
Setup script para o OCI GenAI Chatbot v4
Facilita a instalação e configuração do projeto
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9+ é necessário. Versão atual:", sys.version)
        return False
    print("✅ Python", sys.version.split()[0], "detectado")
    return True

def check_pip():
    """Verifica se o pip está disponível"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip está disponível")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip não encontrado")
        return False

def create_virtual_environment():
    """Cria um ambiente virtual se não existir"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Ambiente virtual já existe")
        return True
    
    try:
        print("🔧 Criando ambiente virtual...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Ambiente virtual criado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def install_dependencies():
    """Instala as dependências do projeto"""
    try:
        print("📦 Instalando dependências...")
        
        # Determina o caminho do pip no ambiente virtual
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip")
        else:  # Unix/Linux/macOS
            pip_path = Path("venv/bin/pip")
        
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_env_file():
    """Cria o arquivo .env a partir do exemplo"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Arquivo .env já existe")
        return True
    
    if env_example.exists():
        try:
            shutil.copy(env_example, env_file)
            print("✅ Arquivo .env criado a partir do exemplo")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar arquivo .env: {e}")
            return False
    else:
        print("⚠️  Arquivo .env.example não encontrado")
        return False

def show_next_steps():
    """Mostra os próximos passos para o usuário"""
    print("\n🎉 Setup concluído com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Ative o ambiente virtual:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("\n2. Execute a aplicação:")
    print("   streamlit run src/app.py")
    
    print("\n3. Acesse no navegador:")
    print("   http://localhost:8501")
    
    print("\n📝 Para configurar a integração OCI:")
    print("   Edite o arquivo .env com suas credenciais")

def main():
    """Função principal do setup"""
    print("🚀 Configurando OCI GenAI Chatbot v4...")
    print("=" * 50)
    
    # Verificações iniciais
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Setup do ambiente
    if not create_virtual_environment():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not create_env_file():
        print("⚠️  Continue mesmo assim...")
    
    show_next_steps()

if __name__ == "__main__":
    main()
