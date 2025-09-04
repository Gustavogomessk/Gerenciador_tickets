import sys
import random
import string
import mysql.connector
from PyQt5 import uic, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

def connect():
    return mysql.connector.connect(
        user='root',
        password='',
        host='localhost',
        port='3306',
        database='gestao_tickets'
    )

def gerar_numero_ticket():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def cadastrar_usuario():
    print("Função cadastrar_usuario chamada")
    nome = tela.name_user.text()
    email = tela.email_user.text()
    senha = tela.Password_user.text()
    tipo = tela.comboBox.currentText().lower()
    print(f"Dados recebidos: {nome}, {email}, {senha}, {tipo}")

    if nome and email and senha:
        try:
            conn = connect()
            cursor = conn.cursor()
            sql = "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)"
            valores = (nome, email, senha, tipo)
            cursor.execute(sql, valores)
            conn.commit()
            QtWidgets.QMessageBox.information(tela, "Sucesso", "Usuário cadastrado com sucesso!")
            tela.name_user.clear()
            tela.email_user.clear()
            tela.Password_user.clear()
        except mysql.connector.Error as erro:
            QtWidgets.QMessageBox.critical(tela, "Erro", f"Erro ao cadastrar usuário: {erro}")
        finally:
            cursor.close()
            conn.close()
    else:
        QtWidgets.QMessageBox.warning(tela, "Atenção", "Preencha todos os campos.")

def cadastrar_ticket():
    print("Função cadastrar_ticket chamada")
    titulo = tela.titulo_ticket.text()
    descricao = tela.descricao_ticket.toPlainText()
    prioridade = 'media'  # Fixo por enquanto

    nome_cliente, ok = QtWidgets.QInputDialog.getText(
        tela, "Cliente", "Nome do cliente:"
    )

    if not ok or not (titulo and descricao and nome_cliente):
        QtWidgets.QMessageBox.warning(tela, "Atenção", "Preencha todos os campos.")
        return

    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE nome = %s AND tipo = 'cliente'", (nome_cliente,))
        resultado = cursor.fetchone()

        if not resultado:
            QtWidgets.QMessageBox.warning(tela, "Cliente não encontrado", f"O cliente '{nome_cliente}' não existe.")
            return

        cliente_id = resultado[0]
        numero_ticket = gerar_numero_ticket()

        sql = """
            INSERT INTO tickets (numero_ticket, titulo, descricao, cliente_id, prioridade)
            VALUES (%s, %s, %s, %s, %s)
        """
        valores = (numero_ticket, titulo, descricao, cliente_id, prioridade)
        cursor.execute(sql, valores)
        conn.commit()

        QtWidgets.QMessageBox.information(tela, "Sucesso", "Ticket criado com sucesso!")
        tela.titulo_ticket.clear()
        tela.descricao_ticket.clear()

    except mysql.connector.Error as erro:
        QtWidgets.QMessageBox.critical(tela, "Erro", f"Erro ao criar ticket:\n{erro}")
    finally:
        cursor.close()
        conn.close()

def atualizar_dashboard():
    try:
        print("Atualizando dashboard...")
        conn = connect()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM tickets")
        total = cursor.fetchone()
        total = total[0] if total else 0
        print(f"Total de tickets: {total}")

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE prioridade = 'baixa'")
        baixa = cursor.fetchone()
        baixa = baixa[0] if baixa else 0
        print(f"Tickets baixa: {baixa}")

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE prioridade = 'media'")
        media = cursor.fetchone()
        media = media[0] if media else 0
        print(f"Tickets média: {media}")

        cursor.execute("SELECT COUNT(*) FROM tickets WHERE prioridade = 'alta'")
        alta = cursor.fetchone()
        alta = alta[0] if alta else 0
        print(f"Tickets alta: {alta}")

        tela.label_total_tickets.setText(str(total))
        tela.label_tickets_baixa.setText(str(baixa))
        tela.label_tickets_media.setText(str(media))
        tela.label_tickets_alta.setText(str(alta))

        plotar_grafico([baixa, media, alta])

    except mysql.connector.Error as erro:
        QtWidgets.QMessageBox.critical(tela, "Erro", f"Erro ao atualizar dashboard:\n{erro}")
        print("Erro no banco:", erro)
    except Exception as e:
        QtWidgets.QMessageBox.critical(tela, "Erro inesperado", f"Erro geral: {e}")
        print("Erro geral:", e)
    finally:
        cursor.close()
        conn.close()


def plotar_grafico(dados):
    prioridades = ['Baixa', 'Média', 'Alta']
    cores = ['green', 'orange', 'red']

    fig = Figure(figsize=(4, 3))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)

    ax.bar(prioridades, dados, color=cores)
    ax.set_title("Tickets por Prioridade")
    ax.set_ylabel("Quantidade")

    layout = QtWidgets.QVBoxLayout(tela.widget_grafico)

    # Remove widgets anteriores (gráfico antigo)
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)

    layout.addWidget(canvas)
    canvas.draw()

def mudar_pagina(index):
    tela.stackedWidget.setCurrentIndex(index)

# Inicialização da aplicação
app = QtWidgets.QApplication([])
tela = uic.loadUi("main.ui")

# Botões de navegação
tela.btn_dash.clicked.connect(lambda: [mudar_pagina(4), atualizar_dashboard()])
tela.btn_tel_tickets.clicked.connect(lambda: mudar_pagina(0))  # Página de Tickets
tela.btn_tela_usurios.clicked.connect(lambda: mudar_pagina(1)) # Página de Usuários

# Botões de ação
tela.btn_novo_ticket.clicked.connect(lambda: mudar_pagina(3))         # Ir para tela de novo ticket
tela.btn_cadastrar_ticket.clicked.connect(cadastrar_ticket)           # Criar ticket

tela.btn_novo_usuario.clicked.connect(lambda: mudar_pagina(2))        # Ir para tela de novo usuário
tela.btn_cadastrar_usuario.clicked.connect(cadastrar_usuario)         # Criar usuário

# Botão de sair
tela.pushButton_3.clicked.connect(app.quit)

# Exibe a interface
tela.show()
app.exec()
