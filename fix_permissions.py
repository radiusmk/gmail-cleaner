#!/usr/bin/env python3
"""
Script para corrigir permissões do Gmail API
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopo correto que inclui permissão para deletar
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def check_current_permissions():
    """Verifica as permissões atuais do token"""
    print("🔍 Verificando permissões atuais...")
    
    if not os.path.exists('token.pickle'):
        print("❌ Nenhum token encontrado. Será necessário autenticar.")
        return False
    
    try:
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        print(f"✅ Token encontrado: {type(creds).__name__}")
        print(f"   Válido: {creds.valid}")
        print(f"   Expirado: {creds.expired}")
        
        if hasattr(creds, 'scopes'):
            print(f"   Escopos atuais: {creds.scopes}")
            
            # Verifica se tem o escopo correto
            correct_scope = 'https://www.googleapis.com/auth/gmail.modify'
            if correct_scope in creds.scopes:
                print("✅ Escopo correto encontrado!")
                return True
            else:
                print("❌ Escopo incorreto ou ausente!")
                print(f"   Necessário: {correct_scope}")
                print(f"   Atual: {creds.scopes}")
                return False
        else:
            print("⚠️ Não foi possível verificar escopos")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar token: {e}")
        return False

def re_authenticate():
    """Re-autentica com as permissões corretas"""
    print("\n🔄 Re-autenticando com permissões corretas...")
    
    try:
        # Remove token antigo
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
            print("✅ Token antigo removido")
        
        # Verifica se credentials.json existe
        if not os.path.exists('credentials.json'):
            print("❌ Arquivo credentials.json não encontrado!")
            print("💡 Baixe o arquivo do Google Cloud Console")
            return None
        
        # Inicia fluxo de autenticação
        print("🔄 Iniciando fluxo OAuth...")
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        
        # Executa o fluxo
        print("🌐 Abrindo navegador para autenticação...")
        print("📋 IMPORTANTE: Certifique-se de conceder TODAS as permissões solicitadas!")
        creds = flow.run_local_server(port=0)
        
        # Salva as novas credenciais
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("✅ Re-autenticação concluída!")
        print(f"✅ Escopos concedidos: {creds.scopes}")
        
        return creds
        
    except Exception as e:
        print(f"❌ Erro durante re-autenticação: {e}")
        return None

def test_delete_permission(creds):
    """Testa se tem permissão para deletar"""
    print("\n🔍 Testando permissão para deletar...")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Primeiro, busca uma mensagem para testar
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("⚠️ Nenhuma mensagem encontrada para teste")
            return False
        
        message_id = messages[0]['id']
        print(f"📧 Testando com mensagem ID: {message_id}")
        
        # Tenta mover para lixeira (deletar)
        try:
            service.users().messages().trash(userId='me', id=message_id).execute()
            print("✅ Permissão para deletar: OK")
            
            # Restaura a mensagem (move de volta da lixeira)
            service.users().messages().untrash(userId='me', id=message_id).execute()
            print("✅ Mensagem restaurada (teste concluído)")
            
            return True
            
        except HttpError as error:
            if error.resp.status == 403:
                print("❌ Permissão para deletar: NEGADA")
                print(f"   Erro: {error}")
                return False
            else:
                print(f"⚠️ Erro inesperado: {error}")
                return False
                
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 CORREÇÃO DE PERMISSÕES - Gmail API")
    print("=" * 50)
    
    # Verifica permissões atuais
    has_correct_permissions = check_current_permissions()
    
    if has_correct_permissions:
        print("\n✅ Permissões já estão corretas!")
        
        # Testa se consegue deletar
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        if test_delete_permission(creds):
            print("\n🎉 Tudo funcionando! Você pode usar o script normalmente.")
        else:
            print("\n❌ Mesmo com escopo correto, não consegue deletar.")
            print("💡 Pode ser restrição da conta ou domínio.")
    else:
        print("\n❌ Permissões incorretas ou ausentes.")
        print("🔄 Será necessário re-autenticar.")
        
        # Re-autentica
        creds = re_authenticate()
        
        if creds:
            # Testa novamente
            if test_delete_permission(creds):
                print("\n🎉 Permissões corrigidas! Agora você pode deletar mensagens.")
            else:
                print("\n❌ Ainda não consegue deletar após re-autenticação.")
                print("💡 Possíveis causas:")
                print("   1. Restrições da conta Google Workspace")
                print("   2. Políticas de segurança do domínio")
                print("   3. Conta com restrições especiais")
        else:
            print("\n❌ Falha na re-autenticação.")
    
    print("\n" + "=" * 50)
    print("📋 PRÓXIMOS PASSOS:")
    print("1. Execute: python gmail_cleaner.py --test")
    print("2. Teste: python gmail_cleaner.py 'gmail' --delete")
    print("3. Se ainda der erro, verifique restrições da conta")

if __name__ == '__main__':
    main()
