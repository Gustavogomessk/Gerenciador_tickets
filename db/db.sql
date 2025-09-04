-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS gestao_tickets
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- Usar o banco
USE gestao_tickets;

-- Tabela de usuários (clientes e admins)
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('admin', 'cliente') NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Tabela de tickets
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero_ticket VARCHAR(20) NOT NULL UNIQUE,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT NOT NULL,
    cliente_id INT NOT NULL,
    prioridade ENUM('baixa', 'media', 'alta', 'urgente') NOT NULL,
    status ENUM('aberto', 'em andamento', 'resolvido', 'fechado') DEFAULT 'aberto',
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (cliente_id) REFERENCES usuarios(id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabela de comentários
CREATE TABLE comentarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL,
    autor_id INT NOT NULL,
    comentario TEXT NOT NULL,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
        ON DELETE CASCADE,
    FOREIGN KEY (autor_id) REFERENCES usuarios(id)
        ON DELETE SET NULL
) ENGINE=InnoDB;
