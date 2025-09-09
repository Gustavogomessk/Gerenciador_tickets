# Sistema de Gerenciamento de Tickets

Sistema desenvolvido em Python com PyQt5 para gerenciamento de tickets de suporte.

## 🚀 Funcionalidades Implementadas

### ✅ Área de Ações da Tabela
- **Visualizar**: Abre uma janela detalhada com informações do ticket e comentários
- **Editar**: Permite editar título, descrição, prioridade e status do ticket
- **Excluir**: Remove o ticket com confirmação

### ✅ Visualização de Tickets
- Janela modal com todas as informações do ticket
- Lista de comentários com data/hora e autor
- Botão para adicionar novos comentários
- Interface intuitiva e responsiva

### ✅ Seleção de Prioridade
- Combobox na criação de tickets com opções:
  - Baixa
  - Média  
  - Alta
  - Urgente

### ✅ Tabela Somente Leitura
- Tabela não permite edição direta dos dados
- Todas as modificações são feitas através dos botões de ação
- Interface mais segura e controlada

### ✅ Sistema de Busca
- Campo de busca por número do ticket, título ou cliente
- Botão de buscar e busca por Enter
- Resultados filtrados em tempo real

## 🛠️ Instalação e Configuração

### Pré-requisitos
- Python 3.7+
- MySQL Server
- PyQt5
- mysql-connector-python
- matplotlib

### Instalação das Dependências
```bash
pip install PyQt5 mysql-connector-python matplotlib
```

### Configuração do Banco de Dados
1. Certifique-se de que o MySQL está rodando
2. Execute o script de configuração:
```bash
python setup_database.py
```

### Executar o Sistema
```bash
python main1.py
```

## 👤 Usuários Padrão

**Administrador:**
- Email: admin@admin.com
- Senha: admin123

## 🗄️ Estrutura do Banco de Dados

### Tabelas
- **usuarios**: Armazena dados de usuários (admin/cliente)
- **tickets**: Armazena informações dos tickets
- **comentarios**: Armazena comentários dos tickets

### Campos dos Tickets
- ID único
- Número do ticket (gerado automaticamente)
- Título e descrição
- Cliente associado
- Prioridade (baixa, média, alta, urgente)
- Status (aberto, em andamento, resolvido, fechado)
- Data de criação

## 🎯 Como Usar

### Para Administradores
1. Faça login com as credenciais de admin
2. Acesse todas as funcionalidades:
   - Dashboard com estatísticas
   - Gerenciar tickets de todos os clientes
   - Gerenciar usuários
   - Criar novos tickets

### Para Clientes
1. Faça login com suas credenciais
2. Visualize apenas seus próprios tickets
3. Crie novos tickets
4. Adicione comentários aos tickets

### Operações Principais
- **Criar Ticket**: Preencha título, descrição e selecione prioridade
- **Buscar**: Use o campo de busca para encontrar tickets específicos
- **Visualizar**: Clique em "Ver" para ver detalhes e comentários
- **Editar**: Clique em "Editar" para modificar informações
- **Excluir**: Clique em "Excluir" para remover o ticket

## 🔧 Configurações

### Conexão com Banco de Dados
Edite a função `connect()` em `main1.py` se necessário:
```python
def connect():
    return mysql.connector.connect(
        user='root',        # Seu usuário MySQL
        password='',        # Sua senha MySQL
        host='localhost',   # Host do MySQL
        port='3306',        # Porta do MySQL
        database='gestao_tickets'
    )
```

## 📝 Notas de Desenvolvimento

- Sistema desenvolvido com PyQt5 para interface gráfica
- Banco de dados MySQL para persistência
- Gráficos gerados com matplotlib
- Interface responsiva e moderna
- Código organizado em funções modulares

## 🐛 Solução de Problemas

### Erro de Conexão com MySQL
- Verifique se o MySQL está rodando
- Confirme as credenciais de conexão
- Execute o script `setup_database.py`

### Erro de Módulos Python
- Instale as dependências: `pip install -r requirements.txt`
- Verifique a versão do Python (3.7+)

### Interface não Carrega
- Verifique se o arquivo `main.ui` está presente
- Confirme se o PyQt5 está instalado corretamente
