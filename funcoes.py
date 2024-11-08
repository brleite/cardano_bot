# Importar lib openai versão 1.3, precisa ter a versão do Python acima de 3.10 (Portal da empresa oferece 3.11)
# pip install --trusted-host nexus.petrobras.com.br --index-url https://nexus.petrobras.com.br/repository/pypi-all/simple openai

import openai
import os
from openai import AzureOpenAI
from configparser import ConfigParser, ExtendedInterpolation
import httpx
import numpy as np

client = None

def iniciar():
    global client
    config = ConfigParser(interpolation=ExtendedInterpolation())
    config.read('config-litellm.ini', 'UTF-8')
    # config.read('PRD_config-litellm.ini', 'UTF-8')


    http_client = httpx.Client(verify='petrobras-ca-root.pem')

    client = AzureOpenAI(
        api_key=config['OPENAI']['OPENAI_API_KEY'],
        api_version=config['OPENAI']['OPENAI_API_VERSION'],
        azure_endpoint=config['OPENAI']['AZURE_OPENAI_BASE_URL'],
        http_client=http_client
    )

    # Consulta API para listar modelos
    models_resp = http_client.get(config['OPENAI']['AZURE_OPENAI_BASE_URL'] + '/models', headers={
        'api-key': config['OPENAI']['OPENAI_API_KEY'],
        'Authorization': 'Bearer ' + config['OPENAI']['OPENAI_API_KEY']
    })
    models_resp.raise_for_status()

    all_models = [m['id'] for m in models_resp.json()['data']]
    len(all_models)

    print("Modelos disponíveis no serviço =================================")
    # Modelos de chat
    models_chat = sorted(m for m in all_models if 'embedding' not in m)
    print("Modelos de chat: ", models_chat)

    # Modelos de embedding
    models_embedding = sorted(m for m in all_models if 'embedding' in m)
    print("Modelos de embedding: ",models_embedding)
    print("================================================================")

    return models_chat, models_embedding

def get_embedding(text, engine, **kwargs):
    response = client.embeddings.create(
        # Contact your team admin to get the name of your engine or model deployment.
        # This is the name that they used when they created the model deployment.
        input=text,
        model=engine,
        **kwargs
    )

    embeddings = response.data[0].embedding
    return np.array(embeddings)

# Defining a function to send the prompt to the ChatGPT model
# More info : https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt?pivots=programming-language-chat-completions
def send_message(messages, engine, max_response_tokens=500):
    response = client.chat.completions.create(
        model=engine,
        messages=messages,
        # temperature=0.5,
        max_tokens=max_response_tokens,
        # top_p=0.9,
    )
    return response.choices[0].message.content


# Defining a function to print out the conversation in a readable format
def print_conversation(messages):
    for message in messages:
        print(f"[{message['role'].upper()}]")
        print(message['content'])
        print()