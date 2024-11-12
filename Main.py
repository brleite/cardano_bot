from exceptiongroup import catch
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from funcoes import iniciar, send_message
from Database import obter_respostas, inserir_pergunta
import time
import re
import random

SEPARADOR_RESPOSTAS_BANCO = '#;#'
SEPARADOR_RESPOSTAS_CHATGPT = ','

def persiste_respostas(pergunta, lista_respostas):
    inserir_pergunta(pergunta, SEPARADOR_RESPOSTAS_BANCO.join(lista_respostas))

def verifica_respostas_corretas(driver):
    div_group = obter_div_respostas(driver)

    lista_li = div_group.find_elements(By.TAG_NAME, 'li')
    lista_respostas = []
    for index, li in enumerate(lista_li):
        try:
            div_check = li.find_element(By.CLASS_NAME, 'i-fa6-regular-circle-check')

            lista_respostas.append(li.text)
        except NoSuchElementException as e:
            continue

    return lista_respostas

def avalia_respostas(driver, pergunta, lista_respostas, persiste=True):
    intervalo = 0.05
    while True:
        try:
            div_card = driver.find_element(By.CLASS_NAME, 'question-card__root')
            classes = div_card.get_attribute('class')

            if 'question-card__root--state_correct' in classes:
                if persiste:
                    persiste_respostas(pergunta, lista_respostas)
                break
            elif 'question-card__root--state_incorrect' in classes:
                if persiste:
                    lista_respostas_corretas = verifica_respostas_corretas(driver)
                    persiste_respostas(pergunta, lista_respostas_corretas)
                break
            else:
                time.sleep(intervalo)
        except NoSuchElementException as e:
            print(e)
            raise e

def obter_enunciado(text_div):
    enunciado = text_div.find_element(By.TAG_NAME, 'div').text

    enunciado_list = enunciado.split('\n')

    # Verificar se a primeira linha corresponde ao padrão <N>/<M>
    padrao = r'^\d+/\d+$'
    if re.match(padrao, enunciado_list[0]):
        enunciado_list.pop(0)

        return '\n'.join(enunciado_list)
    else:
        return enunciado

def obter_numero_respostas(enunciado):
    pattern = r"ESCOLHA (\d+)"
    match = re.search(pattern, enunciado)

    if match:
        numero_respostas = int(match.group(1))
        print(f"The value of <N> is: {numero_respostas}")
    else:
        print("Pattern not found")

    return numero_respostas

def enriquecer_enunciado(enunciado):
    pattern = r"(ESCOLHA \d+)"
    replacement = r"\1 RESPOSTAS"
    enunciado = re.sub(pattern, replacement, enunciado)

    numero_respostas = obter_numero_respostas(enunciado)

    # Define the pattern to match "ESCOLHA <N> RESPOSTAS"
    pattern = r"ESCOLHA \d+ RESPOSTAS"

    instrucao = f"""Escolha {numero_respostas} respostas entre as alternativas apresentadas acima. Apresente apenas o número da alternativa como um inteiro. Se houver mais de uma resposta, separe-as utilizando o caractere '""" + SEPARADOR_RESPOSTAS_CHATGPT + "'"

    # Use re.sub to replace the pattern with an empty string
    enunciado = re.sub(pattern, instrucao, enunciado)

    return enunciado

def obter_div_respostas(driver):
    try:
        div_group = driver.find_element(By.CSS_SELECTOR, 'div[role="group"]')

        return div_group
    except NoSuchElementException as e:
        try:
            div_group = driver.find_element(By.CSS_SELECTOR, 'div[role="radiogroup"]')

            return div_group
        except NoSuchElementException as e2:
            print("Não foi possível encontrar nem group e nem radiogroup")
            raise e2

def criar_questao_completa(enunciado, lista_respostas):
    questao_completa = enunciado + '\n\n' +  '\n'.join(lista_respostas)

    return questao_completa

def obter_lista_respostas(div):
    lista_li = div.find_elements(By.TAG_NAME, 'li')

    lista_respostas = [resposta.text for resposta in lista_li]

    return (lista_li, lista_respostas)

def valida_respostas_chatgpt(lista_respostas_retorno, numero_respostas, numero_alternativas):
    if len(lista_respostas_retorno) != numero_respostas:
        return False

    for resposta in lista_respostas_retorno:
        if not resposta.isnumeric():
            return False
        if int(resposta) > numero_alternativas:
            return False

    return True

def obter_enunciado_tratado(enunciado):
    enunciado_list = enunciado.split('\n')
    if enunciado_list:
        enunciado_list.pop()

    if enunciado_list[0] == 'RECAPITULAÇÃO':
        enunciado_list = enunciado_list[1:]
    elif enunciado_list[0] == 'HORA DE RECAPITULAR':
        enunciado_list = enunciado_list[2:]
    else:
        enunciado_list = enunciado_list[3:]
    return '\n'.join(enunciado_list)

def main(tipo='RECAPITULAÇÃO'):
    models = iniciar()

    modeloDefinido = 'gpt-4o'
    print("Executando modelo:", modeloDefinido, "\n")

    driver = webdriver.Edge()

    try:
        driver.get("https://petrobras.academy.cardanofoundation.org/app/learn/retest")

        title = driver.title

        driver.implicitly_wait(0.5)

        navbar_auth = driver.find_element(by=By.ID, value="navbar-auth")
        print(navbar_auth)

        login_button = navbar_auth.find_element(by=By.CLASS_NAME, value="btn-login-auth")
        print(login_button)
        #time.sleep(3)

        login_button.click()

        login_petrobras_button = driver.find_elements(by=By.CLASS_NAME, value="btn-digemy-primary")[1]
        print(login_petrobras_button)
        login_petrobras_button.click()
        time.sleep(2)

        menu = driver.find_element(by=By.CLASS_NAME, value="grow-999")
        menuList = menu.find_elements(by=By.TAG_NAME, value="a")
        [m.click() for m in menu.find_elements(by=By.TAG_NAME, value="a") if m.text == tipo]
        if tipo == 'SALA DE QUIZ':
            [m.click() for m in driver.find_elements(by=By.TAG_NAME, value="a") if m.text == 'Entrar na Sala de Quiz']
            time.sleep(2)
            classe_card_pergunta = "lt-sm\\:self-start"
        else:
            classe_card_pergunta = "smDown\\:self_start"

        while True:
            try:
                text_div = driver.find_element(by=By.CLASS_NAME, value=classe_card_pergunta)
            except NoSuchElementException as eButtonEntendi:
                [button.click() for button in driver.find_elements(By.TAG_NAME, "button") if button.text == "Entendi"]
                time.sleep(3)
                text_div = driver.find_element(by=By.CLASS_NAME, value=classe_card_pergunta)

            print(text_div)
            print(text_div.text)

            #questaoCompleta = text_div.text.replace("Responder perguntas mais tarde", "").replace("Enviar", "")

            #questaoCompleta = enriquecer_enunciado(questaoCompleta)
            #print(questaoCompleta)

            enunciado = obter_enunciado(text_div)
            numero_respostas = obter_numero_respostas(enunciado)
            enunciado = enriquecer_enunciado(enunciado)

            div_group = obter_div_respostas(driver)
            print(div_group)
            print(div_group.text)

            # lista_li = div_group.find_elements(By.TAG_NAME, 'li')
            lista_li, lista_texto_respostas = obter_lista_respostas(div_group)

            enunciado_tratado = obter_enunciado_tratado(enunciado)
            respostas = obter_respostas(enunciado_tratado)
            if len(respostas) > 0:
                flag_resposta = True
                lista_respostas = respostas[0][2].split(SEPARADOR_RESPOSTAS_BANCO)
                lista_respostas_indice = []
                for r in lista_respostas:
                    if r in lista_texto_respostas:
                        lista_respostas_indice.append(lista_texto_respostas.index(r))
            else:
                flag_resposta = False
                messages = [
                    {"role": "system", "content": '''
                    Você é um profissional de TI utilizando como parâmetro "temperature" o valor de 0,01. Forneça como resposta apenas o número da alternativa como um inteiro. Se houver mais de uma resposta, separe-as por vírgula.
                    '''}
                ]

                questao_completa = criar_questao_completa(enunciado, lista_texto_respostas)

                messages.append({"role": "user", "content": [
                    {
                        'type': 'text',
                        'text': questao_completa
                    }
                    ]
                })

                retorno = send_message(
                    messages,
                    engine=modeloDefinido,
                    max_response_tokens=400
                )

                print("Resposta:", retorno)

                lista_respostas_retorno = retorno.split(SEPARADOR_RESPOSTAS_CHATGPT)
                if not valida_respostas_chatgpt(lista_respostas_retorno, numero_respostas, len(lista_texto_respostas)):
                    lista_respostas_retorno = [i for i in range(1, numero_respostas + 1)]
                lista_respostas = [lista_texto_respostas[int(indice_resposta) - 1] for indice_resposta in lista_respostas_retorno]
                lista_respostas_indice = [int(indice_resposta) - 1 for indice_resposta in lista_respostas_retorno]

                print(lista_respostas)


            for indice_resposta in lista_respostas_indice:
                if indice_resposta < len(lista_li):
                    item = lista_li[indice_resposta]
                    item.click()

            [button.click() for button in driver.find_elements(By.TAG_NAME, "button") if button.text == "Enviar"]
            if not flag_resposta:
                avalia_respostas(driver, enunciado, lista_respostas, persiste=(not flag_resposta))
            time.sleep(4)
            button_continuar_list = [button for button in driver.find_elements(By.TAG_NAME, "button") if button.text == "Continuar"]
            if len(button_continuar_list) > 0:
                [button.click() for button in button_continuar_list]
                time.sleep(4)

        driver.quit()
    except Exception as e:
        if driver is not None:
            driver.quit()


# main(tipo = 'SALA DE QUIZ')
main(tipo = 'RECAPITULAÇÃO')