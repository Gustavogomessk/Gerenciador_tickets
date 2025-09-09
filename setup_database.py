#!/usr/bin/env python3
"""
Script para configurar o banco de dados do sistema de gerenciamento de tickets.
Execute este script antes de usar o sistema pela primeira vez.
"""

import mysql.connector
import sys

def connect_mysql():
    """Conecta ao MySQL sem especificar database"""
    try:
        return mysql.connector.connect(
            user='root',
            password='',
            host='localhost',
            port='3306'
        )
    except mysql.connector.Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

def setup_database():
    """Configura o banco de dados e tabelas"""
    conn = connect_mysql()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Ler o arquivo SQL
        with open('db/db.sql', 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        # Executar comandos SQL
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        
        conn.commit()
        print("✅ Banco de dados configurado com sucesso!")
        
        # Criar usuário admin padrão
        cursor.execute("USE gestao_tickets")
        cursor.execute("""
            INSERT IGNORE INTO usuarios (nome, email, senha, tipo) 
            VALUES ('Admin', 'admin@admin.com', 'admin123', 'admin')
        """)
        conn.commit()
        print("✅ Usuário admin padrão criado (email: admin@admin.com, senha: admin123)")
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Configurando banco de dados...")
    if setup_database():
        print("🎉 Configuração concluída! Você pode agora executar o sistema.")
    else:
        print("💥 Falha na configuração. Verifique se o MySQL está rodando.")
        sys.exit(1)
