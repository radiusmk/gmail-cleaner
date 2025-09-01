#!/usr/bin/env python3
"""
Script de debug detalhado para problemas de conexão Gmail API
"""

import os
import pickle
import json
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def check_files():
    """Verifica se os arquivos necessários existem"""
    print("🔍 Verificando arquivos necessários...")
    
    files_to_check = [
        ('credentials.json', 'Arquivo de credenciais OAuth'),
        ('token.pickle', 'Token de autenticação'),
    ]
    
    for filename, description in files_to_check:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            print(f"✅ {filename} - {description} ({size} bytes)")
        else:
            print(f"❌ {filename} - {description} (NÃO ENCONTRADO)")
    
    print()

def check_credentials_file():
    """Verifica se o arquivo de credenciais é válido"""
    print("🔍 Verificando arquivo de credenciais...")
    
    if not os.path.exists('credentials.json'):
        print("❌ Arquivo credentials.json não encontrado!")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds_data = json.load(f)
        
        required_fields = ['installed', 'client_id', 'client_secret', 'auth_uri', 'token_uri']
        
        if 'installed' in creds_data:
            installed = creds_data['installed']
            for field in required_fields:
                if field in installed:
                    print(f"✅ {field}: {installed[field][:20]}...")
                else:
                    print(f"❌ {field}: FALTANDO")
                    return False
        else:
            print("❌ Campo 'installed' não encontrado no JSON")
            return False
        
        print("✅ Arquivo de credenciais parece válido")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return False

def check_token_file():
    """Verifica se o token é válido"""
    print("\n🔍 Verificando token de autenticação...")
    
    if not os.path.exists('token.pickle'):
        print("❌ Arquivo token.pickle não encontrado")
        return False
    
    try:
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
        
        print(f"✅ Token carregado: {type(creds).__name__}")
        print(f"   Válido: {creds.valid}")
        print(f"   Expirado: {creds.expired}")
        print(f"   Tem refresh token: {hasattr(creds, 'refresh_token') and creds.refresh_token is not None}")
        
        if hasattr(creds, 'scopes'):
            print(f"   Escopos: {creds.scopes}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar token: {e}")
        return False

def test_authentication():
    """Testa o processo de autenticação"""
    print("\n🔍 Testando autenticação...")
    
    creds = None
    
    try:
        # Tenta carregar token existente
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            print("✅ Token carregado do arquivo")
        
        # Verifica se precisa renovar
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Renovando token expirado...")
            creds.refresh(Request())
            print("✅ Token renovado com sucesso")
            
            # Salva o token renovado
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Token renovado salvo")
        
        # Se não há credenciais válidas, tenta autenticar
        if not creds or not creds.valid:
            if not os.path.exists('credentials.json'):
                print("❌ Arquivo credentials.json não encontrado!")
                return None
            
            print("🔄 Iniciando fluxo de autenticação OAuth...")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("✅ Autenticação OAuth concluída")
            
            # Salva as credenciais
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
            print("✅ Credenciais salvas")
        
        return creds
        
    except Exception as e:
        print(f"❌ Erro durante autenticação: {e}")
        return None

def test_service_creation(creds):
    """Testa a criação do serviço Gmail"""
    print("\n🔍 Testando criação do serviço Gmail...")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        print("✅ Serviço Gmail criado com sucesso")
        return service
    except Exception as e:
        print(f"❌ Erro ao criar serviço: {e}")
        return None

def test_basic_api_calls(service):
    """Testa chamadas básicas da API"""
    print("\n🔍 Testando chamadas básicas da API...")
    
    tests = [
        ("getProfile", lambda: service.users().getProfile(userId='me').execute()),
        ("listMessages (sem filtro)", lambda: service.users().messages().list(userId='me', maxResults=1).execute()),
        ("listLabels", lambda: service.users().labels().list(userId='me').execute()),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"🔍 Testando: {test_name}")
            result = test_func()
            print(f"✅ {test_name}: OK")
            
            # Mostra algumas informações úteis
            if test_name == "getProfile":
                print(f"   Email: {result.get('emailAddress', 'N/A')}")
                print(f"   Total de mensagens: {result.get('messagesTotal', 'N/A')}")
                print(f"   Threads não lidos: {result.get('threadsUnread', 'N/A')}")
            elif test_name == "listMessages (sem filtro)":
                messages = result.get('messages', [])
                print(f"   Mensagens encontradas: {len(messages)}")
                if messages:
                    print(f"   Primeira mensagem ID: {messages[0]['id']}")
            elif test_name == "listLabels":
                labels = result.get('labels', [])
                print(f"   Labels encontrados: {len(labels)}")
                
        except HttpError as error:
            print(f"❌ {test_name}: {error}")
            print(f"   Status: {error.resp.status}")
            print(f"   Detalhes: {error.content}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")

def test_specific_permissions():
    """Testa permissões específicas"""
    print("\n🔍 Testando permissões específicas...")
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Testa diferentes operações
        operations = [
            ("Ler perfil", lambda: service.users().getProfile(userId='me').execute()),
            ("Listar mensagens", lambda: service.users().messages().list(userId='me', maxResults=1).execute()),
            ("Ler mensagem", lambda: service.users().messages().get(userId='me', id='test').execute()),
        ]
        
        for op_name, op_func in operations:
            try:
                op_func()
                print(f"✅ {op_name}: Permissão concedida")
            except HttpError as error:
                if error.resp.status == 403:
                    print(f"❌ {op_name}: Permissão negada (403)")
                elif error.resp.status == 404:
                    print(f"⚠️ {op_name}: Recurso não encontrado (404) - mas permissão OK")
                else:
                    print(f"❌ {op_name}: Erro {error.resp.status}")
                    
    except Exception as e:
        print(f"❌ Erro ao testar permissões: {e}")

def main():
    """Função principal"""
    print("🔧 DEBUG DETALHADO - Gmail API")
    print("=" * 50)
    
    # Verifica arquivos
    check_files()
    
    # Verifica credenciais
    if not check_credentials_file():
        print("\n❌ Problema com arquivo de credenciais!")
        print("💡 Solução: Baixe um novo arquivo credentials.json do Google Cloud Console")
        return
    
    # Verifica token
    check_token_file()
    
    # Testa autenticação
    creds = test_authentication()
    if not creds:
        print("\n❌ Falha na autenticação!")
        print("💡 Soluções:")
        print("   1. Delete o arquivo token.pickle e tente novamente")
        print("   2. Verifique se o arquivo credentials.json está correto")
        print("   3. Confirme se a Gmail API está ativada")
        return
    
    # Testa criação do serviço
    service = test_service_creation(creds)
    if not service:
        print("\n❌ Falha ao criar serviço!")
        return
    
    # Testa chamadas básicas
    test_basic_api_calls(service)
    
    # Testa permissões
    test_specific_permissions()
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DO DEBUG")
    print("=" * 50)
    print("✅ Se chegou até aqui, a autenticação está funcionando")
    print("💡 Se ainda há problemas, verifique:")
    print("   1. Se há mensagens na sua caixa de entrada")
    print("   2. Se a Gmail API está ativada no Google Cloud Console")
    print("   3. Se as credenciais têm as permissões corretas")

if __name__ == '__main__':
    main()
