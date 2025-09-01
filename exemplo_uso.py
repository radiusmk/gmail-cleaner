#!/usr/bin/env python3
"""
Exemplo de uso do script Gmail Cleaner com filtro "gmail"
"""

import subprocess
import sys

def executar_comando(comando):
    """Executa um comando e exibe o resultado"""
    print(f"\n🔧 Executando: {comando}")
    print("=" * 60)
    
    try:
        resultado = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        
        if resultado.stdout:
            print(resultado.stdout)
        
        if resultado.stderr:
            print("❌ Erro:", resultado.stderr)
            
        return resultado.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return False

def main():
    """Função principal com exemplos de uso"""
    
    print("📧 Exemplos de uso do Gmail Cleaner")
    print("=" * 60)
    
    # Exemplo 1: Visualizar mensagens com filtro "gmail"
    print("\n1️⃣ Exemplo: Visualizar mensagens com filtro 'gmail'")
    sucesso1 = executar_comando('python gmail_cleaner.py "gmail"')
    
    if sucesso1:
        print("\n✅ Comando executado com sucesso!")
        print("💡 Para deletar estas mensagens, use: python gmail_cleaner.py 'gmail' --delete")
    else:
        print("\n❌ Erro na execução. Verifique se:")
        print("   - O arquivo credentials.json existe")
        print("   - As dependências estão instaladas (pip install -r requirements.txt)")
        print("   - A Gmail API está ativada no Google Cloud Console")
    
    # Exemplo 2: Buscar mensagens de um remetente específico
    print("\n2️⃣ Exemplo: Buscar mensagens de um remetente específico")
    print("💡 Substitua 'exemplo@gmail.com' pelo email desejado")
    executar_comando('python gmail_cleaner.py "from:exemplo@gmail.com"')
    
    # Exemplo 3: Buscar mensagens com anexos
    print("\n3️⃣ Exemplo: Buscar mensagens com anexos")
    executar_comando('python gmail_cleaner.py "has:attachment"')
    
    # Exemplo 4: Buscar mensagens não lidas
    print("\n4️⃣ Exemplo: Buscar mensagens não lidas")
    executar_comando('python gmail_cleaner.py "is:unread"')
    
    print("\n🎯 Dicas importantes:")
    print("   - Sempre teste primeiro sem --delete")
    print("   - Use filtros específicos para melhor performance")
    print("   - O script pede confirmação antes de deletar")
    print("   - As mensagens vão para a Lixeira (não são deletadas permanentemente)")

if __name__ == '__main__':
    main() 