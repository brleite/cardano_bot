from funcoes import iniciar, send_message

models = iniciar()

messages = [
    {"role": "system", "content": '''
    Você é um profissional de TI utilizando como parâmetro "temperature" o valor de 0,01. Forneça como resposta apenas o número da alternativa como um inteiro.
    '''},
    {"role": "user", "content": [
        {
            'type': 'text',
            'text':
                f"""Quais são as principais vantagens de armazenar valores de hash de senhas em vez de armazenar senhas em texto claro?

Escolha 1
Permite que as senhas sejam facilmente descriptografadas em caso de esquecimento

Elimina a necessidade de os usuários lembrarem suas senhas

Garante que as senhas originais permaneçam confidenciais mesmo que o banco de dados seja comprometido
"""
        }
    ]}
]

modeloDefinido = 'gpt-4o'
print("Executando modelo:", modeloDefinido, "\n")
retorno = send_message(
    messages,
    engine=modeloDefinido,
    max_response_tokens=400
)

print("Resposta:", retorno)



