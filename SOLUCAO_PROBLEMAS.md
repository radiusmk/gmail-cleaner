# 🔧 Guia de Solução de Problemas - Gmail API

## 🚨 Problema: "Conexão: ❌ Falha" e "Total de mensagens: 0"

### 📋 Diagnóstico Passo a Passo

Execute o script de debug detalhado:

```bash
python debug_gmail.py
```

Este script irá verificar:
- ✅ Arquivos necessários
- ✅ Validade das credenciais
- ✅ Status do token
- ✅ Processo de autenticação
- ✅ Criação do serviço
- ✅ Chamadas básicas da API

### 🔍 Possíveis Causas e Soluções

#### 1. **Problema: Arquivo credentials.json inválido ou ausente**

**Sintomas:**
- ❌ "Arquivo credentials.json não encontrado"
- ❌ "Campo 'installed' não encontrado no JSON"

**Solução:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione seu projeto
3. Vá em "APIs e Serviços" > "Credenciais"
4. Clique no ID do cliente OAuth 2.0
5. Clique em "Baixar JSON"
6. Renomeie para `credentials.json`
7. Coloque na pasta do script

#### 2. **Problema: Gmail API não ativada**

**Sintomas:**
- ❌ "API not enabled" ou "403 Forbidden"
- ❌ "Gmail API has not been used in project"

**Solução:**
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Selecione seu projeto
3. Vá em "APIs e Serviços" > "Biblioteca"
4. Procure por "Gmail API"
5. Clique na API e depois em "Ativar"
6. Aguarde alguns minutos

#### 3. **Problema: Token expirado ou inválido**

**Sintomas:**
- ❌ "Token expirado"
- ❌ "Invalid credentials"

**Solução:**
```bash
# Delete o token atual
rm token.pickle

# Execute novamente para re-autenticar
python gmail_cleaner.py --test
```

#### 4. **Problema: Permissões insuficientes**

**Sintomas:**
- ❌ "403 Forbidden"
- ❌ "Insufficient permissions"

**Solução:**
1. Verifique se o escopo está correto: `https://www.googleapis.com/auth/gmail.modify`
2. Re-autentique deletando `token.pickle`
3. Confirme as permissões durante o fluxo OAuth

#### 5. **Problema: Conta Google sem mensagens**

**Sintomas:**
- ✅ Autenticação OK
- ✅ API funcionando
- ❌ Total de mensagens: 0

**Solução:**
1. Acesse o Gmail no navegador
2. Confirme que há mensagens na caixa de entrada
3. Verifique se não está filtrando por pastas específicas
4. Envie um email de teste para si mesmo

#### 6. **Problema: Conta Google Workspace com restrições**

**Sintomas:**
- ❌ "Access denied"
- ❌ "Domain policy restricts access"

**Solução:**
1. Verifique com o administrador da sua organização
2. Confirme se a API está habilitada para o domínio
3. Use uma conta Google pessoal para teste

#### 7. **Problema: Permissão para deletar negada**

**Sintomas:**
- ✅ Busca de mensagens funciona
- ✅ Autenticação OK
- ❌ "Insufficient authentication scopes" ao deletar
- ❌ "403 Forbidden" ao deletar

**Solução:**
```bash
# Execute o script de correção de permissões
python fix_permissions.py
```

**Passos manuais:**
1. Delete o arquivo `token.pickle`
2. Re-autentique com: `python gmail_cleaner.py --test`
3. **IMPORTANTE**: Conceda TODAS as permissões solicitadas no navegador
4. Teste novamente: `python gmail_cleaner.py "gmail" --delete`

### 🛠️ Comandos de Diagnóstico

#### 1. **Debug Completo:**
```bash
python debug_gmail.py
```

#### 2. **Teste Básico:**
```bash
python gmail_cleaner.py --test
```

#### 3. **Teste Sem Filtro:**
```bash
python gmail_cleaner.py
```

#### 4. **Re-autenticação:**
```bash
rm token.pickle
python gmail_cleaner.py --test
```

### 📊 Interpretando os Resultados

#### ✅ **Sucesso Total:**
```
✅ credentials.json - Arquivo de credenciais OAuth (2048 bytes)
✅ token.pickle - Token de autenticação (971 bytes)
✅ Token carregado: Credentials
✅ Serviço Gmail criado com sucesso
✅ getProfile: OK
   Email: seu.email@gmail.com
   Total de mensagens: 1234
```

#### ❌ **Problema de Credenciais:**
```
❌ credentials.json - Arquivo de credenciais OAuth (NÃO ENCONTRADO)
❌ Arquivo credentials.json não encontrado!
```

#### ❌ **Problema de API:**
```
❌ getProfile: 403 Forbidden
   Status: 403
   Detalhes: Gmail API has not been used in project
```

#### ❌ **Problema de Token:**
```
❌ Token carregado: Credentials
   Válido: False
   Expirado: True
```

### 🔄 Processo de Recuperação

#### **Passo 1: Verificar Configuração**
```bash
python debug_gmail.py
```

#### **Passo 2: Corrigir Problemas Identificados**
- Baixar novo `credentials.json` se necessário
- Ativar Gmail API se não estiver ativa
- Re-autenticar se token estiver inválido

#### **Passo 3: Testar Novamente**
```bash
python gmail_cleaner.py --test
```

#### **Passo 4: Testar Filtros**
```bash
python gmail_cleaner.py
python gmail_cleaner.py "is:unread"
```

### 📞 Suporte Adicional

Se os problemas persistirem:

1. **Verifique os logs completos** do `debug_gmail.py`
2. **Confirme a configuração** no Google Cloud Console
3. **Teste com uma conta Google pessoal** diferente
4. **Verifique se há mensagens** na caixa de entrada
5. **Consulte a documentação** da Gmail API

### 🎯 Checklist Final

- [ ] Arquivo `credentials.json` existe e é válido
- [ ] Gmail API está ativada no projeto
- [ ] Token de autenticação é válido
- [ ] Conta tem mensagens na caixa de entrada
- [ ] Não há restrições de domínio
- [ ] Escopo correto: `gmail.modify`
- [ ] Script consegue listar mensagens sem filtro
