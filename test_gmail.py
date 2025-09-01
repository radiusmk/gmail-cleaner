#!/usr/bin/env python3
"""
Script de teste para diagnosticar problemas com filtros Gmail
"""

import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """Autentica com o Gmail"""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("❌ Arquivo 'credentials.json' não encontrado!")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Erro ao criar serviço: {e}")
        return None

def test_basic_connection(service):
    """Testa conexão básica"""
    print("🔍 Teste 1: Conexão básica")
    try:
        profile = service.users().getProfile(userId='me').execute()
        print(f"✅ Conectado como: {profile.get('emailAddress', 'N/A')}")
        print(f"📊 Total de mensagens: {profile.get('messagesTotal', 'N/A')}")
        print(f"📧 Mensagens não lidas: {profile.get('threadsUnread', 'N/A')}")
        return True
    except HttpError as error:
        print(f"❌ Erro: {error}")
        return False

def test_message_listing(service):
    """Testa listagem de mensagens"""
    print("\n🔍 Teste 2: Listagem de mensagens")
    
    # Teste sem filtro
    try:
        results = service.users().messages().list(userId='me', maxResults=5).execute()
        messages = results.get('messages', [])
        total = results.get('resultSizeEstimate', 0)
        
        print(f"✅ Sem filtro: {len(messages)} mensagens de {total} total")
        
        if messages:
            print("📋 Primeiras mensagens:")
            for i, msg in enumerate(messages[:3], 1):
                print(f"   {i}. ID: {msg['id']}")
        
        return len(messages) > 0
    except HttpError as error:
        print(f"❌ Erro: {error}")
        return False

def test_specific_filters(service):
    """Testa filtros específicos"""
    print("\n🔍 Teste 3: Filtros específicos")
    
    filters_to_test = [
        ("", "Sem filtro"),
        ("is:unread", "Não lidas"),
        ("is:read", "Lidas"),
        ("has:attachment", "Com anexos"),
        ("gmail", "Contém 'gmail'"),
        ("from:gmail.com", "De gmail.com"),
        ("subject:test", "Assunto contém 'test'"),
        ("after:2024/01/01", "Após 2024/01/01"),
        ("before:2024/12/31", "Antes de 2024/12/31"),
    ]
    
    results = {}
    
    for filter_query, description in filters_to_test:
        try:
            print(f"\n🔍 Testando: {description} ('{filter_query}')")
            results_filter = service.users().messages().list(
                userId='me', 
                q=filter_query, 
                maxResults=10
            ).execute()
            
            messages = results_filter.get('messages', [])
            total = results_filter.get('resultSizeEstimate', 0)
            
            print(f"   📊 Encontradas: {len(messages)} de {total} estimadas")
            
            if messages:
                # Pega detalhes da primeira mensagem
                first_msg = service.users().messages().get(
                    userId='me',
                    id=messages[0]['id'],
                    format='metadata',
                    metadataHeaders=['Subject', 'From', 'Date']
                ).execute()
                
                headers = first_msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'N/A')
                
                print(f"   📧 Exemplo: {subject[:50]}... - {sender}")
            
            results[filter_query] = len(messages)
            
        except HttpError as error:
            print(f"   ❌ Erro: {error}")
            results[filter_query] = -1
    
    return results

def test_message_details(service):
    """Testa obtenção de detalhes de mensagens"""
    print("\n🔍 Teste 4: Detalhes de mensagens")
    
    try:
        # Busca uma mensagem qualquer
        results = service.users().messages().list(userId='me', maxResults=1).execute()
        messages = results.get('messages', [])
        
        if not messages:
            print("❌ Nenhuma mensagem encontrada para teste")
            return False
        
        message_id = messages[0]['id']
        print(f"📧 Testando detalhes da mensagem: {message_id}")
        
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'N/A')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'N/A')
        
        print(f"✅ Detalhes obtidos:")
        print(f"   📋 Assunto: {subject}")
        print(f"   📨 De: {sender}")
        print(f"   📅 Data: {date}")
        print(f"   📝 Snippet: {message.get('snippet', 'N/A')[:100]}...")
        
        return True
        
    except HttpError as error:
        print(f"❌ Erro: {error}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste de Diagnóstico do Gmail API")
    print("=" * 50)
    
    # Autenticação
    print("🔐 Autenticando...")
    service = authenticate_gmail()
    
    if not service:
        print("❌ Falha na autenticação")
        return
    
    print("✅ Autenticação OK!")
    
    # Executa todos os testes
    tests = [
        ("Conexão básica", test_basic_connection),
        ("Listagem de mensagens", test_message_listing),
        ("Filtros específicos", test_specific_filters),
        ("Detalhes de mensagens", test_message_details),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if test_name == "Filtros específicos":
                results[test_name] = test_func(service)
            else:
                results[test_name] = test_func(service)
        except Exception as e:
            print(f"❌ Erro no teste '{test_name}': {e}")
            results[test_name] = False
    
    # Resumo
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    for test_name, result in results.items():
        if test_name == "Filtros específicos":
            print(f"\n🔍 {test_name}:")
            for filter_query, count in result.items():
                status = "✅" if count > 0 else "❌" if count == 0 else "⚠️"
                print(f"   {status} {filter_query or '(vazio)'}: {count} mensagens")
        else:
            status = "✅" if result else "❌"
            print(f"{status} {test_name}")
    
    print("\n💡 RECOMENDAÇÕES:")
    print("1. Se todos os testes passaram, o problema pode estar no filtro específico")
    print("2. Verifique se há mensagens na sua caixa de entrada")
    print("3. Teste filtros mais simples primeiro")
    print("4. Use o comando: python gmail_cleaner.py --test")

if __name__ == '__main__':
    main()
