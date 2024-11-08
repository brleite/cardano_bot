import sqlite3
from Database import obter_todas_respostas

# conectando...
list_respostas = obter_todas_respostas()
[print(resposta) for resposta in list_respostas]