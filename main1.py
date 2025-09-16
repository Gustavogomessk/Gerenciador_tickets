
import sys
import random
import string
import mysql.connector
from PyQt5 import uic, QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

usuario_logado = None

def connect():
    return mysql.connector.connect(
        user='root', password='', host='localhost', port='3306', database='gestao_tickets'
    )

def gerar_numero_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ===== Criar Botões com Ícones =====
def criar_botao_com_icone(texto, icone_texto, cor_fundo="#4CAF50", cor_texto="white"):
    """Cria um botão com ícone usando texto como ícone"""
    botao = QtWidgets.QPushButton()
    botao.setText(f"{icone_texto} {texto}")
    botao.setMinimumSize(80, 35)
    botao.setMaximumSize(100, 40)
    botao.setStyleSheet(f"""
        QPushButton {{
            background-color: {cor_fundo};
            color: {cor_texto};
            border: none;
            border-radius: 5px;
            font-weight: bold;
            font-size: 11px;
            padding: 5px;
        }}
        QPushButton:hover {{
            background-color: {cor_fundo}dd;
            transform: scale(1.05);
        }}
        QPushButton:pressed {{
            background-color: {cor_fundo}aa;
        }}
    """)
    return botao

# =====  LOGIN  =====
def fazer_login():
    global usuario_logado
    email = login.input_email.text()
    senha = login.input_senha.text()

    if not email or not senha:
        QtWidgets.QMessageBox.warning(login, "Erro", "Preencha todos os campos.")
        return

    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, tipo FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        resultado = cursor.fetchone()
        if resultado:
            usuario_logado = {"id": resultado[0], "tipo": resultado[1]}
            login.close()
            iniciar_aplicacao_principal()
        else:
            QtWidgets.QMessageBox.warning(login, "Erro", "Credenciais inválidas.")
    except mysql.connector.Error as e:
        QtWidgets.QMessageBox.critical(login, "Erro no banco", str(e))
    finally:
        cursor.close()
        conn.close()

# ===== Inicia UI Principal =====
def iniciar_aplicacao_principal():
    global tela
    tela = uic.loadUi("main.ui")
    if usuario_logado["tipo"] == "cliente":
        tela.btn_tela_usurios.setVisible(False)

   
    tela.btn_tel_tickets.clicked.connect(lambda: [mudar_pagina(0), carregar_tabela_tickets()])
    tela.btn_tela_usurios.clicked.connect(lambda: [mudar_pagina(1), carregar_tabela_users()])
    tela.btn_novo_ticket.clicked.connect(lambda: mudar_pagina(3))
    tela.btn_cadastrar_ticket.clicked.connect(cadastrar_ticket)
    tela.btn_novo_usuario.clicked.connect(lambda: mudar_pagina(2))
    tela.btn_cadastrar_usuario.clicked.connect(cadastrar_usuario)
    tela.pushButton_3.clicked.connect(app.quit)
    
    # Conectar funcionalidade de busca
    tela.search_tickets.returnPressed.connect(buscar_tickets)
    tela.btn_buscar_tickets.clicked.connect(buscar_tickets)
    
    # Conectar busca de usuários
    tela.Search_user.returnPressed.connect(buscar_usuarios)
    tela.btn_buscar_users.clicked.connect(buscar_usuarios)

    tela.show()

# ===== Navegação =====
def mudar_pagina(index):
    tela.stackedWidget.setCurrentIndex(index)

# ===== Carregar Tabela de Tickets =====
def carregar_tabela_tickets():
    conn = connect()
    cursor = conn.cursor()
    if usuario_logado["tipo"] == "admin":
        cursor.execute("""SELECT t.id, t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id""")
    else:
        cursor.execute("""SELECT t.id, t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id
                          WHERE u.id = %s""", (usuario_logado["id"],))
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_tickets
    tb.setRowCount(0)
    tb.setColumnCount(8)  # Adicionar coluna de ações
    
    # Definir cabeçalhos
    headers = ["ID", "N°", "Título", "Cliente", "Prioridade", "Status", "Data de Criação", "Ações"]
    tb.setHorizontalHeaderLabels(headers)
    
    # Tornar tabela somente leitura
    tb.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))
        
        # Adicionar botões de ação com ícones
        btn_visualizar = criar_botao_com_icone("Ver", "👁", "#2196F3", "white")
        btn_editar = criar_botao_com_icone("Editar", "✏", "#FF9800", "white")
        btn_excluir = criar_botao_com_icone("Excluir", "🗑", "#F44336", "white")
        
        btn_visualizar.clicked.connect(lambda checked, ticket_id=row[0]: visualizar_ticket(ticket_id))
        btn_editar.clicked.connect(lambda checked, ticket_id=row[0]: editar_ticket(ticket_id))
        btn_excluir.clicked.connect(lambda checked, ticket_id=row[0]: excluir_ticket(ticket_id))
        
        # Layout horizontal para os botões
        widget_acoes = QtWidgets.QWidget()
        layout_acoes = QtWidgets.QHBoxLayout(widget_acoes)
        layout_acoes.addWidget(btn_visualizar)
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_excluir)
        layout_acoes.setContentsMargins(3, 3, 3, 3)
        layout_acoes.setSpacing(5)
        
        tb.setCellWidget(linha, 7, widget_acoes)

# ===== Buscar Tickets =====
def buscar_tickets():
    termo_busca = tela.search_tickets.text().strip()
    if not termo_busca:
        carregar_tabela_tickets()  # Se vazio, carrega todos
        return
    
    conn = connect()
    cursor = conn.cursor()
    
    if usuario_logado["tipo"] == "admin":
        cursor.execute("""SELECT t.id, t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id
                          WHERE t.numero_ticket LIKE %s OR t.titulo LIKE %s OR u.nome LIKE %s""",
                       (f"%{termo_busca}%", f"%{termo_busca}%", f"%{termo_busca}%"))
    else:
        cursor.execute("""SELECT t.id, t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id
                          WHERE u.id = %s AND (t.numero_ticket LIKE %s OR t.titulo LIKE %s)""",
                       (usuario_logado["id"], f"%{termo_busca}%", f"%{termo_busca}%"))
    
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_tickets
    tb.setRowCount(0)
    tb.setColumnCount(8)
    
    # Definir cabeçalhos
    headers = ["ID", "N°", "Título", "Cliente", "Prioridade", "Status", "Data de Criação", "Ações"]
    tb.setHorizontalHeaderLabels(headers)
    
    # Tornar tabela somente leitura
    tb.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))
        
        # Adicionar botões de ação com ícones
        btn_visualizar = criar_botao_com_icone("Ver", "👁", "#2196F3", "white")
        btn_editar = criar_botao_com_icone("Editar", "✏", "#FF9800", "white")
        btn_excluir = criar_botao_com_icone("Excluir", "🗑", "#F44336", "white")
        
        btn_visualizar.clicked.connect(lambda checked, ticket_id=row[0]: visualizar_ticket(ticket_id))
        btn_editar.clicked.connect(lambda checked, ticket_id=row[0]: editar_ticket(ticket_id))
        btn_excluir.clicked.connect(lambda checked, ticket_id=row[0]: excluir_ticket(ticket_id))
        
        # Layout horizontal para os botões
        widget_acoes = QtWidgets.QWidget()
        layout_acoes = QtWidgets.QHBoxLayout(widget_acoes)
        layout_acoes.addWidget(btn_visualizar)
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_excluir)
        layout_acoes.setContentsMargins(3, 3, 3, 3)
        layout_acoes.setSpacing(5)
        
        tb.setCellWidget(linha, 7, widget_acoes)

# ===== Carregar Tabela de Usuários =====
def carregar_tabela_users():
    if usuario_logado["tipo"] != "admin":
        return
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.id, u.nome, u.email, u.tipo, COUNT(t.id) AS quant_tickets, u.criado_em
                      FROM usuarios u LEFT JOIN tickets t ON u.id = t.cliente_id
                      GROUP BY u.id""")
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_users
    tb.setRowCount(0)
    tb.setColumnCount(7)  # Adicionar coluna de ações
    
    # Definir cabeçalhos
    headers = ["ID", "Nome", "E-mail", "Tipo", "Quant. tickets", "Criado", "Ações"]
    tb.setHorizontalHeaderLabels(headers)
    
    # Tornar tabela somente leitura
    tb.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))
        
        # Adicionar botões de ação com ícones
        btn_editar = criar_botao_com_icone("Editar", "✏", "#FF9800", "white")
        btn_excluir = criar_botao_com_icone("Excluir", "🗑", "#F44336", "white")
        
        btn_editar.clicked.connect(lambda checked, user_id=row[0]: editar_usuario(user_id))
        btn_excluir.clicked.connect(lambda checked, user_id=row[0]: excluir_usuario(user_id))
        
        # Layout horizontal para os botões
        widget_acoes = QtWidgets.QWidget()
        layout_acoes = QtWidgets.QHBoxLayout(widget_acoes)
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_excluir)
        layout_acoes.setContentsMargins(3, 3, 3, 3)
        layout_acoes.setSpacing(5)
        
        tb.setCellWidget(linha, 6, widget_acoes)

# ===== Buscar Usuários =====
def buscar_usuarios():
    termo_busca = tela.Search_user.text().strip()
    if not termo_busca:
        carregar_tabela_users()  # Se vazio, carrega todos
        return
    
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.id, u.nome, u.email, u.tipo, COUNT(t.id) AS quant_tickets, u.criado_em
                      FROM usuarios u LEFT JOIN tickets t ON u.id = t.cliente_id
                      WHERE u.nome LIKE %s OR u.email LIKE %s
                      GROUP BY u.id""",
                   (f"%{termo_busca}%", f"%{termo_busca}%"))
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_users
    tb.setRowCount(0)
    tb.setColumnCount(7)
    
    # Definir cabeçalhos
    headers = ["ID", "Nome", "E-mail", "Tipo", "Quant. tickets", "Criado", "Ações"]
    tb.setHorizontalHeaderLabels(headers)
    
    # Tornar tabela somente leitura
    tb.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
    
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))
        
        # Adicionar botões de ação com ícones
        btn_editar = criar_botao_com_icone("Editar", "✏", "#FF9800", "white")
        btn_excluir = criar_botao_com_icone("Excluir", "🗑", "#F44336", "white")
        
        btn_editar.clicked.connect(lambda checked, user_id=row[0]: editar_usuario(user_id))
        btn_excluir.clicked.connect(lambda checked, user_id=row[0]: excluir_usuario(user_id))
        
        # Layout horizontal para os botões
        widget_acoes = QtWidgets.QWidget()
        layout_acoes = QtWidgets.QHBoxLayout(widget_acoes)
        layout_acoes.addWidget(btn_editar)
        layout_acoes.addWidget(btn_excluir)
        layout_acoes.setContentsMargins(3, 3, 3, 3)
        layout_acoes.setSpacing(5)
        
        tb.setCellWidget(linha, 6, widget_acoes)

# ===== Cadastrar Usuário =====
def cadastrar_usuario():
    nome = tela.name_user.text()
    email = tela.email_user.text()
    senha = tela.Password_user.text()
    tipo = tela.comboBox.currentText().lower()
    if nome and email and senha:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                           (nome, email, senha, tipo))
            conn.commit()
            QtWidgets.QMessageBox.information(tela, "Sucesso", "Usuário cadastrado.")
            tela.name_user.clear(); tela.email_user.clear(); tela.Password_user.clear()
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(tela, "Erro no cadastro", str(e))
        finally:
            cursor.close(); conn.close()
    else:
        QtWidgets.QMessageBox.warning(tela, "Atenção", "Preencha todos os campos.")

# ===== Editar Usuário =====
def editar_usuario(user_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, email, tipo FROM usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    conn.close()
    
    if not usuario:
        QtWidgets.QMessageBox.warning(tela, "Erro", "Usuário não encontrado.")
        return
    
    # Criar janela de edição
    janela_editar = QtWidgets.QDialog(tela)
    janela_editar.setWindowTitle("Editar Usuário")
    janela_editar.setModal(True)
    janela_editar.resize(400, 300)
    
    layout = QtWidgets.QVBoxLayout(janela_editar)
    
    # Campos de edição
    nome_label = QtWidgets.QLabel("Nome:")
    nome_edit = QtWidgets.QLineEdit(usuario[0])
    layout.addWidget(nome_label)
    layout.addWidget(nome_edit)
    
    email_label = QtWidgets.QLabel("E-mail:")
    email_edit = QtWidgets.QLineEdit(usuario[1])
    layout.addWidget(email_label)
    layout.addWidget(email_edit)
    
    tipo_label = QtWidgets.QLabel("Tipo:")
    tipo_combo = QtWidgets.QComboBox()
    tipo_combo.addItems(["Admin", "Cliente"])
    tipo_combo.setCurrentText(usuario[2].title())
    layout.addWidget(tipo_label)
    layout.addWidget(tipo_combo)
    
    senha_label = QtWidgets.QLabel("Nova Senha (deixe em branco para manter a atual):")
    senha_edit = QtWidgets.QLineEdit()
    senha_edit.setEchoMode(QtWidgets.QLineEdit.Password)
    layout.addWidget(senha_label)
    layout.addWidget(senha_edit)
    
    # Botões
    btn_salvar = QtWidgets.QPushButton("Salvar")
    btn_cancelar = QtWidgets.QPushButton("Cancelar")
    
    def salvar_edicao():
        try:
            conn = connect()
            cursor = conn.cursor()
            
            # Se senha foi fornecida, atualizar senha também
            if senha_edit.text().strip():
                cursor.execute("""UPDATE usuarios SET nome = %s, email = %s, tipo = %s, senha = %s
                                  WHERE id = %s""",
                               (nome_edit.text(), email_edit.text(), 
                                tipo_combo.currentText().lower(), 
                                senha_edit.text(), user_id))
            else:
                cursor.execute("""UPDATE usuarios SET nome = %s, email = %s, tipo = %s
                                  WHERE id = %s""",
                               (nome_edit.text(), email_edit.text(), 
                                tipo_combo.currentText().lower(), user_id))
            
            conn.commit()
            QtWidgets.QMessageBox.information(janela_editar, "Sucesso", "Usuário atualizado.")
            janela_editar.close()
            carregar_tabela_users()  # Recarregar tabela
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(janela_editar, "Erro", f"Erro ao atualizar usuário: {e}")
        finally:
            cursor.close()
            conn.close()
    
    btn_salvar.clicked.connect(salvar_edicao)
    btn_cancelar.clicked.connect(janela_editar.close)
    
    layout.addWidget(btn_salvar)
    layout.addWidget(btn_cancelar)
    
    janela_editar.exec_()

# ===== Excluir Usuário =====
def excluir_usuario(user_id):
    # Verificar se o usuário tem tickets
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tickets WHERE cliente_id = %s", (user_id,))
    quant_tickets = cursor.fetchone()[0]
    conn.close()
    
    if quant_tickets > 0:
        QtWidgets.QMessageBox.warning(tela, "Erro", 
                                    f"Não é possível excluir este usuário pois ele possui {quant_tickets} ticket(s).")
        return
    
    reply = QtWidgets.QMessageBox.question(tela, "Confirmar Exclusão", 
                                          "Tem certeza que deseja excluir este usuário?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    
    if reply == QtWidgets.QMessageBox.Yes:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()
            QtWidgets.QMessageBox.information(tela, "Sucesso", "Usuário excluído.")
            carregar_tabela_users()  # Recarregar tabela
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(tela, "Erro", f"Erro ao excluir usuário: {e}")
        finally:
            cursor.close()
            conn.close()

# ===== Cadastrar Ticket =====
def cadastrar_ticket():
    if usuario_logado["tipo"] != "admin":
        cliente_id = usuario_logado["id"]
    else:
        nome_cliente, ok = QtWidgets.QInputDialog.getText(tela, "Cliente", "Nome do cliente:")
        if not ok or not nome_cliente:
            return
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE nome = %s AND tipo = 'cliente'", (nome_cliente,))
        resultado = cursor.fetchone()
        conn.close()
        if not resultado:
            QtWidgets.QMessageBox.warning(tela, "Erro", "Cliente não encontrado.")
            return
        cliente_id = resultado[0]

    titulo = tela.titulo_ticket.text()
    descricao = tela.descricao_ticket.toPlainText()
    prioridade = tela.combo_prioridade.currentText().lower()
    
    if not titulo or not descricao:
        QtWidgets.QMessageBox.warning(tela, "Atenção", "Preencha todos os campos.")
        return

    numero = gerar_numero_ticket()
    try:
        conn = connect(); cursor = conn.cursor()
        cursor.execute("""INSERT INTO tickets (numero_ticket, titulo, descricao, cliente_id, prioridade)
                          VALUES (%s, %s, %s, %s, %s)""",
                       (numero, titulo, descricao, cliente_id, prioridade))
        conn.commit()
        QtWidgets.QMessageBox.information(tela, "Sucesso", "Ticket criado.")
        tela.titulo_ticket.clear(); tela.descricao_ticket.clear()
    except mysql.connector.Error as e:
        QtWidgets.QMessageBox.critical(tela, "Erro no cadastro", str(e))
    finally:
        cursor.close(); conn.close()

# ===== Visualizar Ticket =====
def visualizar_ticket(ticket_id):
    conn = connect()
    cursor = conn.cursor()
    
    # Buscar dados do ticket
    cursor.execute("""SELECT t.numero_ticket, t.titulo, t.descricao, u.nome, t.prioridade, t.status, t.criado_em
                      FROM tickets t JOIN usuarios u ON t.cliente_id = u.id
                      WHERE t.id = %s""", (ticket_id,))
    ticket = cursor.fetchone()
    
    if not ticket:
        QtWidgets.QMessageBox.warning(tela, "Erro", "Ticket não encontrado.")
        return
    
    # Buscar comentários
    cursor.execute("""SELECT c.comentario, c.criado_em, u.nome
                      FROM comentarios c LEFT JOIN usuarios u ON c.autor_id = u.id
                      WHERE c.ticket_id = %s ORDER BY c.criado_em""", (ticket_id,))
    comentarios = cursor.fetchall()
    
    conn.close()
    
    # Criar janela de visualização
    janela_visualizar = QtWidgets.QDialog(tela)
    janela_visualizar.setWindowTitle(f"Ticket #{ticket[0]}")
    janela_visualizar.setModal(True)
    janela_visualizar.resize(800, 600)
    
    layout = QtWidgets.QVBoxLayout(janela_visualizar)
    
    # Informações do ticket
    info_frame = QtWidgets.QFrame()
    info_layout = QtWidgets.QFormLayout(info_frame)
    
    info_layout.addRow("Número:", QtWidgets.QLabel(ticket[0]))
    info_layout.addRow("Título:", QtWidgets.QLabel(ticket[1]))
    info_layout.addRow("Cliente:", QtWidgets.QLabel(ticket[3]))
    info_layout.addRow("Prioridade:", QtWidgets.QLabel(ticket[4].title()))
    info_layout.addRow("Status:", QtWidgets.QLabel(ticket[5].title()))
    info_layout.addRow("Criado em:", QtWidgets.QLabel(str(ticket[6])))
    
    descricao_label = QtWidgets.QLabel("Descrição:")
    descricao_text = QtWidgets.QTextEdit()
    descricao_text.setPlainText(ticket[2])
    descricao_text.setReadOnly(True)
    descricao_text.setMaximumHeight(100)
    
    info_layout.addRow(descricao_label, descricao_text)
    
    layout.addWidget(info_frame)
    
    # Comentários
    comentarios_label = QtWidgets.QLabel("Comentários:")
    layout.addWidget(comentarios_label)
    
    comentarios_list = QtWidgets.QListWidget()
    for comentario in comentarios:
        item_text = f"[{comentario[1]}] {comentario[2] or 'Sistema'}: {comentario[0]}"
        comentarios_list.addItem(item_text)
    
    layout.addWidget(comentarios_list)
    
    # Botão para adicionar comentário
    btn_comentar = QtWidgets.QPushButton("Adicionar Comentário")
    btn_comentar.clicked.connect(lambda: adicionar_comentario(ticket_id, janela_visualizar))
    layout.addWidget(btn_comentar)
    
    # Botão fechar
    btn_fechar = QtWidgets.QPushButton("Fechar")
    btn_fechar.clicked.connect(janela_visualizar.close)
    layout.addWidget(btn_fechar)
    
    janela_visualizar.exec_()

# ===== Adicionar Comentário =====
def adicionar_comentario(ticket_id, janela_pai):
    comentario, ok = QtWidgets.QInputDialog.getMultiLineText(janela_pai, "Novo Comentário", "Digite seu comentário:")
    if ok and comentario.strip():
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO comentarios (ticket_id, autor_id, comentario)
                              VALUES (%s, %s, %s)""",
                           (ticket_id, usuario_logado["id"], comentario))
            conn.commit()
            QtWidgets.QMessageBox.information(janela_pai, "Sucesso", "Comentário adicionado.")
            janela_pai.close()
            visualizar_ticket(ticket_id)  # Recarregar a janela
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(janela_pai, "Erro", f"Erro ao adicionar comentário: {e}")
        finally:
            cursor.close()
            conn.close()

# ===== Editar Ticket =====
def editar_ticket(ticket_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT titulo, descricao, prioridade, status FROM tickets WHERE id = %s", (ticket_id,))
    ticket = cursor.fetchone()
    conn.close()
    
    if not ticket:
        QtWidgets.QMessageBox.warning(tela, "Erro", "Ticket não encontrado.")
        return
    
    # Criar janela de edição
    janela_editar = QtWidgets.QDialog(tela)
    janela_editar.setWindowTitle("Editar Ticket")
    janela_editar.setModal(True)
    janela_editar.resize(500, 400)
    
    layout = QtWidgets.QVBoxLayout(janela_editar)
    
    # Campos de edição
    titulo_label = QtWidgets.QLabel("Título:")
    titulo_edit = QtWidgets.QLineEdit(ticket[0])
    layout.addWidget(titulo_label)
    layout.addWidget(titulo_edit)
    
    descricao_label = QtWidgets.QLabel("Descrição:")
    descricao_edit = QtWidgets.QTextEdit()
    descricao_edit.setPlainText(ticket[1])
    layout.addWidget(descricao_label)
    layout.addWidget(descricao_edit)
    
    prioridade_label = QtWidgets.QLabel("Prioridade:")
    prioridade_combo = QtWidgets.QComboBox()
    prioridade_combo.addItems(["Baixa", "Média", "Alta", "Urgente"])
    prioridade_combo.setCurrentText(ticket[2].title())
    layout.addWidget(prioridade_label)
    layout.addWidget(prioridade_combo)
    
    status_label = QtWidgets.QLabel("Status:")
    status_combo = QtWidgets.QComboBox()
    status_combo.addItems(["Aberto", "Em Andamento", "Resolvido", "Fechado"])
    status_combo.setCurrentText(ticket[3].title())
    layout.addWidget(status_label)
    layout.addWidget(status_combo)
    
    # Botões
    btn_salvar = QtWidgets.QPushButton("Salvar")
    btn_cancelar = QtWidgets.QPushButton("Cancelar")
    
    def salvar_edicao():
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("""UPDATE tickets SET titulo = %s, descricao = %s, prioridade = %s, status = %s
                              WHERE id = %s""",
                           (titulo_edit.text(), descricao_edit.toPlainText(), 
                            prioridade_combo.currentText().lower(), 
                            status_combo.currentText().lower().replace(" ", "_"), ticket_id))
            conn.commit()
            QtWidgets.QMessageBox.information(janela_editar, "Sucesso", "Ticket atualizado.")
            janela_editar.close()
            carregar_tabela_tickets()  # Recarregar tabela
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(janela_editar, "Erro", f"Erro ao atualizar ticket: {e}")
        finally:
            cursor.close()
            conn.close()
    
    btn_salvar.clicked.connect(salvar_edicao)
    btn_cancelar.clicked.connect(janela_editar.close)
    
    layout.addWidget(btn_salvar)
    layout.addWidget(btn_cancelar)
    
    janela_editar.exec_()

# ===== Excluir Ticket =====
def excluir_ticket(ticket_id):
    reply = QtWidgets.QMessageBox.question(tela, "Confirmar Exclusão", 
                                          "Tem certeza que deseja excluir este ticket?",
                                          QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    
    if reply == QtWidgets.QMessageBox.Yes:
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
            conn.commit()
            QtWidgets.QMessageBox.information(tela, "Sucesso", "Ticket excluído.")
            carregar_tabela_tickets()  # Recarregar tabela
        except mysql.connector.Error as e:
            QtWidgets.QMessageBox.critical(tela, "Erro", f"Erro ao excluir ticket: {e}")
        finally:
            cursor.close()
            conn.close()



#  ==== Início do App ====
app = QtWidgets.QApplication(sys.argv)
login = uic.loadUi("login.ui")
login.btn_login.clicked.connect(fazer_login)
login.show()
sys.exit(app.exec_())
