
import sys
import random
import string
import mysql.connector
from PyQt5 import uic, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

usuario_logado = None

def connect():
    return mysql.connector.connect(
        user='root', password='', host='localhost', port='3306', database='gestao_tickets'
    )

def gerar_numero_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

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

    tela.btn_dash.clicked.connect(lambda: [mudar_pagina(4), atualizar_dashboard()])
    tela.btn_tel_tickets.clicked.connect(lambda: [mudar_pagina(0), carregar_tabela_tickets()])
    tela.btn_tela_usurios.clicked.connect(lambda: [mudar_pagina(1), carregar_tabela_users()])
    tela.btn_novo_ticket.clicked.connect(lambda: mudar_pagina(3))
    tela.btn_cadastrar_ticket.clicked.connect(cadastrar_ticket)
    tela.btn_novo_usuario.clicked.connect(lambda: mudar_pagina(2))
    tela.btn_cadastrar_usuario.clicked.connect(cadastrar_usuario)
    tela.pushButton_3.clicked.connect(app.quit)

    tela.show()

# ===== Navegação =====
def mudar_pagina(index):
    tela.stackedWidget.setCurrentIndex(index)

# ===== Carregar Tabela de Tickets =====
def carregar_tabela_tickets():
    conn = connect()
    cursor = conn.cursor()
    if usuario_logado["tipo"] == "admin":
        cursor.execute("""SELECT t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id""")
    else:
        cursor.execute("""SELECT t.numero_ticket, t.titulo, u.nome, t.prioridade, t.status, t.criado_em
                          FROM tickets t JOIN usuarios u ON t.cliente_id = u.id
                          WHERE u.id = %s""", (usuario_logado["id"],))
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_tickets
    tb.setRowCount(0)
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))

# ===== Carregar Tabela de Usuários =====
def carregar_tabela_users():
    if usuario_logado["tipo"] != "admin":
        return
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""SELECT u.nome, u.email, u.tipo, COUNT(t.id) AS quant_tickets, u.criado_em
                      FROM usuarios u LEFT JOIN tickets t ON u.id = t.cliente_id
                      GROUP BY u.id""")
    registros = cursor.fetchall()
    conn.close()

    tb = tela.tb_users
    tb.setRowCount(0)
    for linha, row in enumerate(registros):
        tb.insertRow(linha)
        for col, dado in enumerate(row):
            tb.setItem(linha, col, QtWidgets.QTableWidgetItem(str(dado)))

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
    if not titulo or not descricao:
        QtWidgets.QMessageBox.warning(tela, "Atenção", "Preencha todos os campos.")
        return

    numero = gerar_numero_ticket()
    try:
        conn = connect(); cursor = conn.cursor()
        cursor.execute("""INSERT INTO tickets (numero_ticket, titulo, descricao, cliente_id, prioridade)
                          VALUES (%s, %s, %s, %s, 'media')""",
                       (numero, titulo, descricao, cliente_id))
        conn.commit()
        QtWidgets.QMessageBox.information(tela, "Sucesso", "Ticket criado.")
        tela.titulo_ticket.clear(); tela.descricao_ticket.clear()
    except mysql.connector.Error as e:
        QtWidgets.QMessageBox.critical(tela, "Erro no cadastro", str(e))
    finally:
        cursor.close(); conn.close()

# ===== Atualizar Dashboard =====
def atualizar_dashboard():
    conn = connect(); cursor = conn.cursor()
    user_id = usuario_logado["id"]

    if usuario_logado["tipo"] == "admin":
        cursor.execute("SELECT COUNT(*) FROM tickets")
    else:
        cursor.execute("SELECT COUNT(*) FROM tickets WHERE cliente_id = %s", (user_id,))
    total = cursor.fetchone()[0]

    query_prioridade = ("SELECT prioridade, COUNT(*) FROM tickets WHERE cliente_id = %s GROUP BY prioridade"
                        if usuario_logado["tipo"] != "admin"
                        else "SELECT prioridade, COUNT(*) FROM tickets GROUP BY prioridade")
    cursor.execute(query_prioridade, (user_id,) if usuario_logado["tipo"] != "admin" else ())
    contagens = dict(cursor.fetchall())

    conn.close()

    tela.label_total_tickets.setText(str(total))
    mapping = {
    "baixa": tela.label_baixa,
    "media": tela.label_media,
    "alta": tela.label_alta,
    }

    for prio in ["baixa", "media", "alta"]: 
        mapping[prio].setText(str(contagens.get(prio, 0)))


    plotar_grafico([contagens.get("baixa", 0), contagens.get("media", 0), contagens.get("alta", 0)])

# ===== Plotar Gráfico =====
def plotar_grafico(dados):
    fig = Figure(figsize=(4, 3)); canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    ax.bar(['Baixa', 'Média', 'Alta'], dados, color=['green', 'orange', 'red'])
    ax.set_title("Tickets por Prioridade"); ax.set_ylabel("Quantidade")

    layout = QtWidgets.QVBoxLayout(tela.widget_grafico)
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)
    layout.addWidget(canvas)
    canvas.draw()

#  ==== Início do App ====
app = QtWidgets.QApplication(sys.argv)
login = uic.loadUi("login.ui")
login.btn_login.clicked.connect(fazer_login)
login.show()
sys.exit(app.exec_())
