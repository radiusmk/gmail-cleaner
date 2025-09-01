#!/usr/bin/env python3
"""
Script para conectar ao Gmail via OAuth e deletar mensagens conforme filtros.
"""

import os
import pickle
import argparse
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopo necessário para acessar o Gmail (inclui permissão para deletar)
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def authenticate_gmail():
    """
    Autentica com o Gmail usando OAuth 2.0.
    Retorna o serviço autenticado.
    """
    creds = None
    
    # Verifica se já existe um token salvo
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # Se não há credenciais válidas, solicita autenticação
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Verifica se existe o arquivo de credenciais
            if not os.path.exists('credentials.json'):
                print("❌ Arquivo 'credentials.json' não encontrado!")
                print("📋 Para obter o arquivo de credenciais:")
                print("1. Acesse https://console.cloud.google.com/")
                print("2. Crie um novo projeto ou selecione um existente")
                print("3. Ative a Gmail API")
                print("4. Crie credenciais OAuth 2.0")
                print("5. Baixe o arquivo JSON e renomeie para 'credentials.json'")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Salva as credenciais para a próxima execução
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Erro ao criar serviço Gmail: {e}")
        return None

def test_gmail_connection(service):
    """
    Testa a conexão com o Gmail e verifica se há mensagens.
    """
    try:
        # Testa buscar todas as mensagens (sem filtro)
        print("🔍 Testando conexão com Gmail...")
        results = service.users().messages().list(
            userId='me', 
            maxResults=1
        ).execute()
        
        total_messages = results.get('resultSizeEstimate', 0)
        print(f"✅ Conexão OK! Total estimado de mensagens: {total_messages}")
        
        # Testa buscar mensagens com filtro vazio
        print("🔍 Testando busca sem filtro...")
        results_no_filter = service.users().messages().list(
            userId='me', 
            maxResults=5
        ).execute()
        
        messages_no_filter = results_no_filter.get('messages', [])
        print(f"📧 Mensagens encontradas sem filtro: {len(messages_no_filter)}")
        
        return True, total_messages, messages_no_filter
        
    except HttpError as error:
        print(f"❌ Erro ao testar conexão: {error}")
        return False, 0, []

def search_messages(service, query, max_results=50, get_all=False):
    """
    Busca mensagens no Gmail com base na query fornecida.
    
    Args:
        service: Serviço Gmail autenticado
        query: Query de busca (ex: "gmail", "from:exemplo@gmail.com", etc.)
        max_results: Número máximo de resultados para amostra
        get_all: Se True, busca TODAS as mensagens que combinam com o filtro
    
    Returns:
        Lista de IDs das mensagens encontradas
    """
    try:
        print(f"🔍 Executando busca com query: '{query}'")
        
        # Se a query estiver vazia ou for apenas espaços, busca todas as mensagens
        if not query or query.strip() == "":
            query = ""
            print("ℹ️  Query vazia - buscando todas as mensagens")
        
        if get_all:
            print("📊 Buscando TODAS as mensagens que combinam com o filtro...")
            all_messages = []
            page_token = None
            
            while True:
                # Busca um lote de mensagens
                results = service.users().messages().list(
                    userId='me', 
                    q=query, 
                    maxResults=500,  # Máximo por lote
                    pageToken=page_token
                ).execute()
                
                messages = results.get('messages', [])
                all_messages.extend(messages)
                
                print(f"   📧 Lote encontrado: {len(messages)} mensagens (Total: {len(all_messages)})")
                
                # Verifica se há mais páginas
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
            
            total_estimated = results.get('resultSizeEstimate', len(all_messages))
            print(f"📊 Busca completa finalizada:")
            print(f"   - Total de mensagens encontradas: {len(all_messages)}")
            print(f"   - Total estimado: {total_estimated}")
            
            return all_messages
        else:
            print(f"📊 Buscando amostra de até {max_results} mensagens...")
            
            results = service.users().messages().list(
                userId='me', 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            total_estimated = results.get('resultSizeEstimate', 0)
            
            print(f"📊 Resultado da busca (amostra):")
            print(f"   - Mensagens retornadas: {len(messages)}")
            print(f"   - Total estimado: {total_estimated}")
            
            if total_estimated > len(messages):
                print(f"   ⚠️  Há mais mensagens disponíveis! Total estimado: {total_estimated}")
        
        if not messages:
            print("⚠️  Nenhuma mensagem encontrada. Possíveis causas:")
            print("   - O filtro é muito específico")
            print("   - Não há mensagens que atendam ao critério")
            print("   - Problema com a sintaxe do filtro")
            
            # Sugere alguns filtros comuns para teste
            print("\n💡 Sugestões de filtros para teste:")
            print("   - '' (vazio - todas as mensagens)")
            print("   - 'is:unread' (não lidas)")
            print("   - 'is:read' (lidas)")
            print("   - 'has:attachment' (com anexos)")
            print("   - 'after:2024/01/01' (após uma data)")
        
        return messages
    except HttpError as error:
        print(f"❌ Erro ao buscar mensagens: {error}")
        print(f"   Detalhes do erro: {error.resp.status} - {error.content}")
        return []

def get_message_details(service, message_id):
    """
    Obtém detalhes de uma mensagem específica.
    
    Args:
        service: Serviço Gmail autenticado
        message_id: ID da mensagem
    
    Returns:
        Dicionário com detalhes da mensagem
    """
    try:
        message = service.users().messages().get(
            userId='me', 
            id=message_id,
            format='metadata',
            metadataHeaders=['Subject', 'From', 'Date']
        ).execute()
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'Sem assunto')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Remetente desconhecido')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Data desconhecida')
        
        return {
            'id': message_id,
            'subject': subject,
            'from': sender,
            'date': date,
            'snippet': message.get('snippet', '')
        }
    except HttpError as error:
        print(f"❌ Erro ao obter detalhes da mensagem {message_id}: {error}")
        return None

def display_messages(messages):
    """
    Exibe as mensagens encontradas de forma organizada.
    
    Args:
        messages: Lista de mensagens com detalhes
    """
    if not messages:
        print("📭 Nenhuma mensagem encontrada com o filtro especificado.")
        return
    
    print(f"\n📧 Encontradas {len(messages)} mensagens:")
    print("=" * 80)
    
    for i, msg in enumerate(messages, 1):
        print(f"\n{i:2d}. ID: {msg['id']}")
        print(f"    📨 De: {msg['from']}")
        print(f"    📋 Assunto: {msg['subject']}")
        print(f"    📅 Data: {msg['date']}")
        print(f"    📝 Preview: {msg['snippet'][:100]}...")
        print("-" * 80)

def delete_messages(service, message_ids):
    """
    Deleta as mensagens especificadas.
    
    Args:
        service: Serviço Gmail autenticado
        message_ids: Lista de IDs das mensagens a serem deletadas
    
    Returns:
        Número de mensagens deletadas com sucesso
    """
    if not message_ids:
        return 0
    
    deleted_count = 0
    total_messages = len(message_ids)
    
    try:
        print(f"🗑️ Movendo {total_messages} mensagens para a Lixeira...")
        
        # Processa em lotes para melhor performance
        batch_size = 100
        for i in range(0, total_messages, batch_size):
            batch = message_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_messages + batch_size - 1) // batch_size
            
            print(f"   📦 Processando lote {batch_num}/{total_batches} ({len(batch)} mensagens)...")
            
            # Processa cada mensagem do lote
            for j, message_id in enumerate(batch):
                try:
                    service.users().messages().trash(userId='me', id=message_id).execute()
                    deleted_count += 1
                    
                    # Mostra progresso a cada 10 mensagens
                    if (j + 1) % 10 == 0 or j == len(batch) - 1:
                        progress = ((i + j + 1) / total_messages) * 100
                        print(f"      ✅ Progresso: {progress:.1f}% ({deleted_count}/{total_messages})")
                        
                except HttpError as error:
                    print(f"❌ Erro ao deletar mensagem {message_id}: {error}")
                    continue
                except Exception as error:
                    print(f"❌ Erro inesperado ao deletar mensagem {message_id}: {error}")
                    continue
        
        if deleted_count > 0:
            print(f"✅ {deleted_count} mensagens movidas para a Lixeira com sucesso!")
            if deleted_count != total_messages:
                print(f"⚠️  {total_messages - deleted_count} mensagens não puderam ser deletadas.")
        else:
            print("❌ Nenhuma mensagem foi deletada.")
        
    except Exception as error:
        print(f"❌ Erro geral ao deletar mensagens: {error}")
    
    return deleted_count

def main():
    """
    Função principal do script.
    """
    parser = argparse.ArgumentParser(
        description='Script para deletar mensagens do Gmail com base em filtros'
    )
    parser.add_argument(
        'filter', 
        nargs='?',
        default='',
        help='Filtro de busca Gmail (ex: "gmail", "from:exemplo@gmail.com", "subject:importante"). Deixe vazio para buscar todas as mensagens.'
    )
    parser.add_argument(
        '--delete', 
        action='store_true',
        help='Deletar as mensagens encontradas (sem este flag apenas mostra as mensagens)'
    )
    parser.add_argument(
        '--max-results', 
        type=int, 
        default=50,
        help='Número máximo de mensagens para buscar (padrão: 50)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Executar teste de conexão e mostrar estatísticas básicas'
    )
    
    args = parser.parse_args()
    
    print("🔐 Autenticando com o Gmail...")
    service = authenticate_gmail()
    
    if not service:
        print("❌ Falha na autenticação. Verifique suas credenciais.")
        return
    
    print("✅ Autenticação realizada com sucesso!")
    
    # Se o modo teste estiver ativado, executa testes de conexão
    if args.test:
        print("\n🧪 Executando testes de conexão...")
        success, total_messages, sample_messages = test_gmail_connection(service)
        
        if success and sample_messages:
            print("\n📋 Amostra de mensagens disponíveis:")
            for i, msg in enumerate(sample_messages[:3], 1):
                details = get_message_details(service, msg['id'])
                if details:
                    print(f"{i}. {details['subject']} - {details['from']}")
        
        print(f"\n📊 Estatísticas:")
        print(f"   - Total de mensagens na caixa: {total_messages}")
        print(f"   - Conexão: {'✅ OK' if success else '❌ Falha'}")
        return
    
    # Primeiro, busca uma amostra para mostrar ao usuário
    print(f"\n🔍 Buscando amostra de mensagens com filtro: '{args.filter}'")
    sample_messages = search_messages(service, args.filter, args.max_results, get_all=False)
    
    if not sample_messages:
        print("📭 Nenhuma mensagem encontrada.")
        print("\n💡 Dicas para resolver:")
        print("1. Execute com --test para verificar a conexão")
        print("2. Tente um filtro mais simples como '' (vazio)")
        print("3. Verifique se há mensagens na sua caixa de entrada")
        return
    
    # Obtém detalhes das mensagens da amostra
    print(f"\n📋 Obtendo detalhes da amostra de {len(sample_messages)} mensagens...")
    sample_details = []
    
    for msg in sample_messages:
        details = get_message_details(service, msg['id'])
        if details:
            sample_details.append(details)
    
    # Exibe as mensagens da amostra
    display_messages(sample_details)
    
    if args.delete:
        # Busca TODAS as mensagens que combinam com o filtro
        print(f"\n🔍 Buscando TODAS as mensagens que combinam com o filtro para deleção...")
        all_messages = search_messages(service, args.filter, args.max_results, get_all=True)
        
        if not all_messages:
            print("❌ Nenhuma mensagem encontrada para deletar.")
            return
        
        total_to_delete = len(all_messages)
        print(f"\n⚠️  ATENÇÃO: Você está prestes a deletar {total_to_delete} mensagens!")
        print(f"   (Amostra mostrada acima: {len(sample_details)} mensagens)")
        
        confirm = input("🤔 Tem certeza? Digite 'SIM' para confirmar: ")
        
        if confirm.upper() == 'SIM':
            message_ids = [msg['id'] for msg in all_messages]
            deleted_count = delete_messages(service, message_ids)
            
            if deleted_count > 0:
                print(f"🎉 Operação concluída! {deleted_count} mensagens foram deletadas.")
                if deleted_count != total_to_delete:
                    print(f"⚠️  Nota: {total_to_delete - deleted_count} mensagens não puderam ser deletadas.")
            else:
                print("❌ Nenhuma mensagem foi deletada.")
        else:
            print("❌ Operação cancelada pelo usuário.")
    else:
        # Mostra informações sobre o total estimado
        if len(sample_messages) < args.max_results:
            print(f"\n💡 Para deletar estas mensagens, execute o comando com --delete:")
            print(f"   python gmail_cleaner.py '{args.filter}' --delete")
        else:
            print(f"\n💡 Esta é apenas uma amostra! Para deletar TODAS as mensagens que combinam com o filtro:")
            print(f"   python gmail_cleaner.py '{args.filter}' --delete")

if __name__ == '__main__':
    main() 