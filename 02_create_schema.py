import sqlite3

# conectando...
conn = sqlite3.connect('cardano.db')
# definindo um cursor
cursor = conn.cursor()

# criando a tabela (schema)
cursor.execute("""
CREATE TABLE perguntas (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        pergunta TEXT NOT NULL,
        respostas TEXT NOT NULL
);
""")

print('Tabela criada com sucesso.')
# desconectando...
conn.close()