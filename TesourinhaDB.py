# Codigo criado por: Juan Felipe Blanco Regueira
# Codigo atualizado por: Ana Luzia Carregosa Alves
# Codigo criado para o projeto TESOURINHA DE BELEZA KIDS, este codigo eh responsavel por criar o banco de dados
# e as tabelas necessarias para o funcionamento do sistema de agendamentos, futuramente sera integrado a um
# chatbot que ira interagir com o usuario e realizar os agendamentos de forma automatizada.

import sqlite3

#conecta ao banco de dados, cria caso nao exista um.
conn = sqlite3.connect('tesourinha.db')

#ativa o suporte a chaves estrangeiras
conn.execute("PRAGMA foreign_keys = ON")

cursor = conn.cursor()

#====================================
# Tabela Funcionarios
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    funcao TEXT NOT NULL,
    horario_trabalho TEXT NOT NULL
)
''')

#====================================
# Tabela Servicos
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS servicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_servico TEXT NOT NULL,
    valor REAL NOT NULL,
    dias_retorno INTEGER
)
''')

#====================================
# Tabela Responsaveis
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS responsaveis(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT NOT NULL UNIQUE,
)
''')

#====================================
# Tabela Criancas
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS criancas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    responsavel_id INTEGER NOT NULL,
    FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id) ON DELETE CASCADE
)
''')

#====================================
# Tabela Horarios
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS horarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER,
    data_hora DATETIME NOT NULL,
    status TEXT DEFAULT 'Disponível',
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id) ON DELETE CASCADE
)
''')

#====================================
# Tabela Agendamentos
#====================================
cursor.execute('''
CREATE TABLE IF NOT EXISTS agendamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    responsavel_id INTEGER NOT NULL,
    crianca_id INTEGER,
    servico_id INTEGER NOT NULL,
    horario_id INTEGER NOT NULL, 
    status TEXT DEFAULT 'Agendado',
    FOREIGN KEY (responsavel_id) REFERENCES responsaveis(id) ON DELETE CASCADE,
    FOREIGN KEY (crianca_id) REFERENCES criancas(id) ON DELETE CASCADE,
    FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE,
    FOREIGN KEY (horario_id) REFERENCES horarios(id) ON DELETE CASCADE
)
''')

#====================================
# Tabela de Mensagens
#====================================
# Guarda o historico para o bot saber em qual etapa da conversa o usuario esta
cursor.execute('''
CREATE TABLE IF NOT EXISTS mensagens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telefone_cliente TEXT NOT NULL,
    mensagem TEXT NOT NULL,
    direcao TEXT NOT NULL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()

print("Banco de dados e tabelas criados com sucesso!")
