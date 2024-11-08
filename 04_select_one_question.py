import sqlite3
from Database import obter_respostas

enunciado = """Módulo 2: Conceitos Avançados de Blockchain
Ataques de Gasto Duplo
Exemplo: Gastos Duplos Etapas 2 e 3
Com base na imagem abaixo, quais dois passos precisam acontecer para que Mallory duplique com sucesso os mesmos tokens?
ESCOLHA 2 RESPOSTAS
Escolha 2 respostas entre as alternativas apresentadas acima. Apresente apenas o número da alternativa como um inteiro. Se houver mais de uma resposta, separe-as por vírgula."""
list_respostas = obter_respostas(enunciado)
[print(resposta) for resposta in list_respostas]