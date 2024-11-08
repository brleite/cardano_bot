import sqlite3
conn = sqlite3.connect('cardano.db')

def inserir_pergunta(pergunta, respostas):
    cursor = conn.cursor()

    # inserindo dados na tabela
    cursor.execute("""
    INSERT INTO perguntas (pergunta, respostas)
    VALUES (?, ?)
    """, (pergunta, respostas))

    conn.commit()

def obter_respostas(pergunta):
    cursor = conn.cursor()

    # lendo os dados
    cursor.execute("""
    SELECT * FROM perguntas WHERE pergunta LIKE ?;
    """, ('%' + pergunta + '%',))

    return cursor.fetchall()

def obter_todas_respostas():
    cursor = conn.cursor()

    # lendo os dados
    cursor.execute("""
    SELECT * FROM perguntas;
    """)

    return cursor.fetchall()