# Gmail Cleaner - Script de Limpeza de E-mails

Este script Python permite conectar ao Gmail via autenticação OAuth 2.0 e deletar mensagens com base em filtros personalizados. Antes de deletar, o script exibe uma amostra das mensagens que atendem aos critérios de busca.

## 🚀 Funcionalidades

- ✅ Autenticação OAuth 2.0 segura com o Gmail
- 🔍 Busca de mensagens com filtros personalizados
- 📋 Visualização de amostra das mensagens antes da exclusão
- 🗑️ Exclusão de TODAS as mensagens que combinam com o filtro
- ⚠️ Confirmação antes da exclusão
- 📊 Controle do número máximo de resultados para amostra
- 🔄 Processamento em lotes para melhor performance

## 📋 Pré-requisitos

1. **Python 3.7+** instalado
2. **Conta Google** com Gmail ativo
3. **Projeto no Google Cloud Console** com Gmail API ativada

## 🔧 Configuração

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Credenciais OAuth 2.0

#### Passo a Passo:

1. **Acesse o Google Cloud Console**
   - Vá para [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Faça login com sua conta Google

2. **Crie um novo projeto ou selecione um existente**
   - Clique no seletor de projeto no topo
   - Clique em "Novo Projeto" ou selecione um existente

3. **Ative a Gmail API**
   - No menu lateral, vá em "APIs e Serviços" > "Biblioteca"
   - Procure por "Gmail API"
   - Clique na API e depois em "Ativar"

4. **Crie credenciais OAuth 2.0**
   - Vá em "APIs e Serviços" > "Credenciais"
   - Clique em "Criar Credenciais" > "ID do cliente OAuth 2.0"
   - Selecione "Aplicativo de desktop"
   - Dê um nome ao projeto (ex: "Gmail Cleaner")
   - Clique em "Criar"

5. **Baixe o arquivo de credenciais**
   - Clique no ID do cliente criado
   - Clique em "Baixar JSON"
   - Renomeie o arquivo para `credentials.json`
   - Coloque o arquivo na mesma pasta do script

### 3. Estrutura de Arquivos

```
gmail-tools/
├── gmail_cleaner.py      # Script principal
├── requirements.txt      # Dependências
├── credentials.json      # Suas credenciais OAuth (você precisa criar)
├── token.pickle         # Token de autenticação (criado automaticamente)
└── README.md           # Este arquivo
```

## 🎯 Como Usar

### Sintaxe Básica

```bash
python gmail_cleaner.py "filtro" [opções]
```

### Exemplos de Uso

#### 1. Testar conexão e ver estatísticas
```bash
python gmail_cleaner.py --test
```

#### 2. Visualizar todas as mensagens (sem filtro)
```bash
python gmail_cleaner.py
```

#### 3. Visualizar mensagens com filtro "gmail"
```bash
python gmail_cleaner.py "gmail"
```

#### 4. Deletar mensagens com filtro "gmail"
```bash
python gmail_cleaner.py "gmail" --delete
```

#### 5. Buscar mensagens de um remetente específico
```bash
python gmail_cleaner.py "from:exemplo@gmail.com" --delete
```

#### 6. Buscar mensagens com assunto específico
```bash
python gmail_cleaner.py "subject:newsletter" --delete
```

#### 7. Limitar número de resultados
```bash
python gmail_cleaner.py "gmail" --max-results 100 --delete
```

### 📋 Como Funciona: Amostra vs Deleção Completa

O script funciona em duas etapas:

#### **1. Visualização (Amostra)**
```bash
python gmail_cleaner.py "gmail"
```
- Mostra uma amostra de até 50 mensagens (configurável)
- Exibe detalhes: remetente, assunto, data, preview
- **NÃO deleta** nenhuma mensagem
- Útil para verificar se o filtro está correto

#### **2. Deleção Completa**
```bash
python gmail_cleaner.py "gmail" --delete
```
- Primeiro mostra a amostra (como acima)
- Depois busca **TODAS** as mensagens que combinam com o filtro
- Deleta **TODAS** as mensagens encontradas (não apenas a amostra)
- Processa em lotes de 100 mensagens para melhor performance
- Mostra progresso em tempo real

#### **Exemplo:**
```bash
# Mostra amostra de 50 mensagens com "gmail" no assunto
python gmail_cleaner.py "subject:gmail"

# Deleta TODAS as mensagens com "gmail" no assunto (pode ser 1000+ mensagens)
python gmail_cleaner.py "subject:gmail" --delete
```

### Diagnóstico de Problemas

Se os filtros não estiverem funcionando, execute o script de diagnóstico:

```bash
python test_gmail.py
```

Este script irá:
- Testar a conexão básica
- Verificar se há mensagens na caixa
- Testar vários filtros comuns
- Mostrar estatísticas detalhadas

### 🔧 Correção de Permissões

Se você conseguir buscar mensagens mas receber erro de permissão ao deletar:

```bash
python fix_permissions.py
```

Este script irá:
- Verificar as permissões atuais
- Re-autenticar com permissões corretas
- Testar se consegue deletar mensagens
- Fornecer instruções específicas

### Filtros Disponíveis

O script aceita todos os filtros de busca do Gmail:

- **`gmail`** - Busca por "gmail" em qualquer lugar
- **`from:email@exemplo.com`** - Mensagens de um remetente específico
- **`to:email@exemplo.com`** - Mensagens para um destinatário específico
- **`subject:palavra`** - Mensagens com palavra no assunto
- **`has:attachment`** - Mensagens com anexos
- **`is:unread`** - Mensagens não lidas
- **`is:read`** - Mensagens lidas
- **`after:2023/01/01`** - Mensagens após uma data
- **`before:2023/12/31`** - Mensagens antes de uma data
- **`larger:10M`** - Mensagens maiores que 10MB
- **`smaller:1M`** - Mensagens menores que 1MB

### Combinações de Filtros

Você pode combinar filtros usando operadores lógicos:

```bash
# Mensagens não lidas de um remetente específico
python gmail_cleaner.py "from:exemplo@gmail.com is:unread" --delete

# Mensagens com anexos e assunto específico
python gmail_cleaner.py "has:attachment subject:relatório" --delete

# Mensagens antigas de um remetente
python gmail_cleaner.py "from:newsletter@gmail.com before:2023/01/01" --delete
```

## ⚠️ Importante

- **Sempre teste primeiro sem `--delete`** para ver quais mensagens serão afetadas
- **O script pede confirmação** antes de deletar (digite "SIM" para confirmar)
- **As mensagens são movidas para a Lixeira** do Gmail (não são deletadas permanentemente)
- **Mantenha o arquivo `credentials.json` seguro** e não o compartilhe

## 🔒 Segurança

- O arquivo `token.pickle` contém suas credenciais de acesso
- Mantenha este arquivo seguro e não o compartilhe
- Se suspeitar de comprometimento, delete o arquivo `token.pickle` e re-autentique

## 🐛 Solução de Problemas

### Problema: "Nenhuma mensagem encontrada" com qualquer filtro

**Sintomas:**
- O script se autentica corretamente
- Mas sempre retorna "nenhuma mensagem encontrada"
- Mesmo com filtros simples como "gmail" ou ""

**Soluções:**

1. **Execute o teste de diagnóstico:**
   ```bash
   python test_gmail.py
   ```

2. **Teste a conexão básica:**
   ```bash
   python gmail_cleaner.py --test
   ```

3. **Verifique se há mensagens na caixa:**
   - Acesse o Gmail no navegador
   - Confirme que há mensagens na caixa de entrada
   - Verifique se não está filtrando por pastas específicas

4. **Teste sem filtro primeiro:**
   ```bash
   python gmail_cleaner.py
   ```

5. **Possíveis causas:**
   - Caixa de entrada vazia
   - Filtros muito específicos
   - Problemas de permissão da API
   - Mensagens em pastas específicas (Spam, Lixeira, etc.)

### Erro: "Arquivo 'credentials.json' não encontrado"
- Verifique se o arquivo está na mesma pasta do script
- Confirme se o nome está correto (exatamente `credentials.json`)

### Erro: "Falha na autenticação"
- Delete o arquivo `token.pickle` e tente novamente
- Verifique se o arquivo `credentials.json` está correto
- Confirme se a Gmail API está ativada no Google Cloud Console

### Erro: "Quota exceeded"
- A API do Gmail tem limites de uso
- Aguarde algumas horas e tente novamente
- Considere usar filtros mais específicos para reduzir o número de requisições

### Erro: "Access denied" ou "Insufficient permissions"
- Verifique se o escopo da API está correto
- Confirme se a Gmail API está ativada
- Tente re-autenticar deletando `token.pickle`

## 📝 Logs e Debug

O script exibe informações detalhadas sobre:
- Status da autenticação
- Número de mensagens encontradas
- Detalhes de cada mensagem (remetente, assunto, data)
- Confirmação de exclusão

## 🤝 Contribuição

Sinta-se à vontade para contribuir com melhorias, correções de bugs ou novas funcionalidades!

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes. #   g m a i l - c l e a n e r 
 
