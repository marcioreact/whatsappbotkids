import os
import requests
import sqlite3
from datetime import datetime, date, timedelta
import re
from texto import mensagens
from flask import Flask, request, jsonify

app = Flask(__name__)

ACCESS_TOKEN = "EAAMagaZAploIBR5EZBTLgsuia18OetyIr5kQwI86yuRZAQMNNA0OOdU73p5oMKWtkTcJunkIdeB3fInvhxrbQJasBofq0Ri6cL2gsCSMmHz0s8T61OxlFXDOvEdcwcfVlcuW6ZBYbNnUnsVDzZBrUuz0ZCyl0D0AAqXZCicpaq1q6ebJQ4QVByYHR598QQF108Xvf3V40J3QonHdFKIn491oKZALYy5ebMZCzRAJpzDv5eC369vWbcuL4dlrDNAVMJJs9ZCSSrUd37Pxy8JpO9g1NtfAlI"
PHONE_NUMBER_ID = "1068403969700473"
VERIFY_TOKEN = "MeuTokenUltraSecretoSalaoKids2026"

DATABASE = 'tesourinha.db'
# Funcoes para acessar o banco de dados

def coneccao():
    """Conecta ao banco de dados SQLite"""
    conectar = sqlite3.connect(DATABASE)
    conectar.row_factory = sqlite3.Row

    return conectar

def verificar_cadastro(telefone):
    """Verifica se o telefone do WhatsApp já está na tabela de responsáveis e traz o ID e o Nome"""
    conectar = coneccao()
    cursor = conectar.cursor()

    cursor.execute("SELECT id_responsavel, nome_responsavel FROM responsaveis WHERE telefone = ?", (telefone,))
    cliente = cursor.fetchone()
    conectar.close()

    return cliente

def armazenar_mensagem(telefone, texto, direcao):
    """Salva a mensagem no histórico do banco de dados"""
    conectar = coneccao()

    conectar.execute(
        "INSERT INTO mensagens (telefone_cliente, mensagem, direcao) VALUES (?, ?, ?)",
        (telefone, texto, direcao)
    )
    conectar.commit()
    conectar.close()

def estado(telefone):
    """Descobre em qual etapa o cliente parou"""
    conectar = coneccao()
    cursor = conectar.cursor()

    cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'bot' ORDER BY id DSC LIMIT 1",(telefone,))

    resultado = cursor.fetchone()
    conectar.close()

    if resultado:
        return resultado['mensagem']
    return ""

def buscar_criancas_do_adulto(id_adulto):
    """Vai na tabela de crianças e busca todos os filhos atrelados a este adulto"""
    conectar = coneccao()
    cursor = conectar.cursor()

    cursor.execute("SELECT id, nome FROM criancas WHERE responsavel_id = ?", (id_adulto,))
    lista_criancas = cursor.fetchall()
    conectar.close()

    return lista_criancas

def horarios_disponiveis(data_desejada):
    """Vai na tabela de horarios e mostra os horarios disponiveis para a data digitado pelo cliente"""
    conectar = coneccao()
    cursor = conectar.cursor()

    data = f"{data_desejada}%"
    cursor.execute("SELECT id, data_hora FROM horarios WHERE data_hora LIKE ? AND status = 'Disponível'", (data,))
    lista_horarios = cursor.fetchall()
    conectar.close()
 
    return lista_horarios

def formatar_data(texto_digitado):
    """Converte o texto em uma data válida"""
    texto_limpo = texto_digitado.lower().strip()
    hoje = date.today()
    ano_atual = hoje.year

    if "hoje" in texto_limpo or "hj" in texto_limpo:
        return hoje.strftime("%d/%m/%Y")
        
    if "amanha" in texto_limpo or "amanhã" in texto_limpo:
        amanha = hoje + timedelta(days=1)
        return amanha.strftime('%d/%m/%Y')

    meses = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
    
    data_extensa = re.search(r"(\d{1,2})\s*(?:de)?\s*([a-zç]+)", texto_limpo)
    if data_extensa:
        dia = int(data_extensa.group(1))
        mes = data_extensa.group(2)

        if mes in meses:
            mes_numero = meses[mes]
            ano = ano_atual

            if mes_numero < hoje.month or (mes_numero == hoje.month and dia < hoje.day):
                ano += 1
            
            data = f"{dia:02d}/{mes_numero:02d}/{ano}"
        
    data_numero = re.search(r"(\d{1,2})[-./](\d{1,2})(?:[-./](\d{2}|\d{4}))?", texto_limpo) 
    if data_numero:
        dia = int(data_numero.group(1))
        mes = int(data_numero.group(2))
        ano = data_numero.group(3)

        if not ano:
            if mes_numero < hoje.month or (mes_numero == hoje.month and dia < hoje.day):
                ano += 1
        
        elif len(str(ano)) == 2:
            ano = f"20{ano}"

        data = f"{dia:02d}/{mes:02d}/{ano}"
    
    data_dia = re.search(r'\b(\d{1,2})\b', texto_limpo)
    if data_dia:
        dia = int(data_dia.group(1))

        if 1 <= dia <= 31:
            mes = hoje.month
            ano = ano_atual

            if dia < hoje.day:
                mes += 1
                if mes > 12:
                    mes = 1
                    ano += 1

            data = f"{dia:02d}/{mes:02d}/{ano}"

    if data:
        try:
            data_conferida = datetime.strptime(data, '%d/%m/%Y')
            return data_conferida.strftime('%d/%m/%Y')
        except ValueError:
            return False
        
    return False       

def buscar_agendamentos(id_cliente):
    """Busca os agendamentos ativos de um cliente e usa JOIN para trazer o nome do serviço, da criança e a data"""   
    conectar = coneccao()
    cursor = conectar.cursor()

    cursor.execute(
        """SELECT
        a.id AS id_agendamento,
        s.nome_servico,
        c.nome AS nome_crianca,
        h.data_hora
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        JOIN criancas c ON a.crianca_id = c.id
        JOIN horarios h ON a.horario_id = h.id
        WHERE a.responsavel_id = ? AND a.status = 'Agendado'
        """, (id_cliente,))

###
def enviar_mensagem_whatsapp(destinatario, texto):
    """Envia uma mensagem de texto usando a API do WhatsApp Business"""
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"
    # f"https://facebook.com{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": texto}
    }

    print(url)
    response = requests.post(url, json=payload, headers=headers)

    print(response.status_code)
    print(response.text)

    return response.json()

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    """Validação do webhook exigida pela Meta na configuração inicial"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Token de verificação inválido", 403
    return "Requisição inválida", 400

@app.route("/webhook", methods=["POST"])
def receber_mensagem():
    """Recebe as mensagens dos clientes e processa a resposta"""
    dados = request.get_json()

    if "entry" in dados and dados["entry"][0]["changes"][0]["value"].get("messages"):
        mensagem_objeto = dados["entry"][0]["changes"][0]["value"]["messages"][0]
        telefone_cliente = mensagem_objeto["from"]
        
        if mensagem_objeto["type"] == "text":
            texto_recebido = mensagem_objeto["text"]["body"].lower().strip()

            armazenar_mensagem(telefone_cliente, texto_recebido, "cliente")
            ultima_pergunta = estado(telefone_cliente)
            cliente = verificar_cadastro(telefone_cliente)
            resposta =""

            # PRIMEIRO CONTATO (ENVIA O MENU)

            if not ultima_pergunta or texto_recebido == "menu":
                if cliente:
                    resposta = mensagens["menu_inicial_cliente"].format(nome=cliente["nome_responsavel"].split()[0])
                else:
                    resposta = mensagens["menu_inicial"]

            # OPCOES DO MENU QUE NAO PRECISAM DE CADASTRO

            elif texto_recebido == "2" and "como posso te ajudar" in ultima_pergunta.lower(): # Servicos e valores
                conectar = coneccao()
                cursor = conectar.cursor()

                cursor.execute("SELECT nome_servico, valor FROM servicos")
                lista_servicos = cursor.fetchall()
                conectar.close()

                lista_servicos = "\n".join(f"{s['nome_servico']} - R$ {s['valor']:.2f}" for s in lista_servicos)

                resposta = mensagens["servicos_valores"].format(servicos=lista_servicos)
                
            elif texto_recebido == "4" and "como posso te ajudar" in ultima_pergunta.lower(): # Converse conosco
                resposta = mensagens["converse_conosco"]

                num_tesourinha = "5571999999999"
                nome_cliente = cliente["nome_responsavel"].split()[0]

                notificar = mensagens["notificacao"].format(nome=nome_cliente)
                enviar_mensagem_whatsapp(num_tesourinha, notificar)


            # OPCAO DO MENU QUE PRECISA DE CADASTRO (CANCELAMENTO - OPCAO 3)

            elif texto_recebido == "3" and "como posso te ajudar" in ultima_pergunta.lower():
                id_cliente = cliente["id_responsavel"]
                agendamentos_ativos = buscar_agendamentos(id_cliente)

                if agendamentos_ativos:
                    agendamentos_ativos = "\n".join(f"{i}. {a['nome_servico']} {a['nome_crianca']} - {a['[data_hora]']}" for i, a in enumerate(agendamentos_ativos, start=1))
                    resposta = mensagens["agendamentos_cancelar"].format(agendamentos=agendamentos_ativos)
                else:
                    resposta = mensagens["erro_cancelamento"]

            elif "deseja cancelar" in ultima_pergunta.lower():
                numero_escolhido = texto_recebido.strip()

                if numero_escolhido.isdigit():
                    escolha = int(numero_escolhido)
                    id_cliente = cliente["id_responsavel"]

                    agendamentos = buscar_agendamentos(id_cliente)
                    
                    if escolha == 0:
                        resposta = mensagens["cancelamento_cancelado"]

                    if 1 <= escolha <= len(agendamentos):
                        alvo = agendamentos[alvo - 1]
                        servico = alvo["nome_servico"]
                        horario = alvo["data_hora"]
                        
                        resposta = mensagens["confirmar_cancelamento"].format(servico=servico, data_hora=horario)
                    else:
                        resposta = "Opção inválida. Por favor digite um número que está na lista. Qual deseja cancelar?"
                else:
                    resposta = "Opção inválida. Digite apenas o número respectivo ao horário que deseja cancelar"
                
            elif "confirma o cancelamento" in ultima_pergunta.lower():
                texto_limpo = texto_recebido.lower().strip()
                if texto_limpo in  ["sim", "s", "ss"]:
                    id_cliente = cliente["id_responsavel"]

                    conectar = coneccao()
                    cursor = conectar.cursor()
                    cursor = cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'cliente' ORDER BY DESC LIMIT 1 OFFSET 1", (telefone_cliente,))
                    resultado = cursor.fetchone()

                    if resultado and resultado["mensagem"].isdigit():
                        escolha = int(resultado["mensagem"])
                        agendamentos = buscar_agendamentos(id_cliente)

                        if 1 <= escolha <= len(agendamentos):
                            alvo = agendamentos[escolha - 1]
                            id_agendamento = alvo["id_agendamento"]
                            id_horario = alvo["horario_id"]

                            conectar.execute("UPDATE horarios SET status = 'Disponível' WHERE id = ?", (id_horario,))
                            conectar.commit()

                            num_tesourinha = "5571999999999"
                            nome_cliente = cliente["nome_responsavel"].split()[0]

                            if alvo["crianca_id"]:
                                crianca = f"da criança {}"
                            else:
                                adulto = f"do cliente {}"

                            mensagem = mensagens["notificacao_cancelamento"].format()
                            enviar_mensagem_whatsapp(num_tesourinha, mensagem)


                    conectar.close()
                    resposta = mensagens["cancelado"]
            
                elif texto_limpo in ["não", "nao", "n", "nn"]:
                    resposta = mensagens["cancelamento_cancelado"]

                else:
                    resposta = mensagens["cancelamento_cancelado"] + mensagens["confirmar_cancelamento2"]
            

            # OPCAO DO MENU QUE PRECISA DE CADASTRO (AGENDAMENTO - OPCAO 1)

            elif texto_recebido == "1" and "como posso te ajudar" in ultima_pergunta.lower(): # Agendamento
                if not cliente:
                    resposta = mensagens["cadastro"]
                else:
                    resposta = mensagens["crianca_adulto"]

            # REALIZACAO DO CADASTRO

            elif "me informe seu nome" in ultima_pergunta.lower():
                nome_digitado = texto_recebido.title()

                conectar = coneccao()
                conectar.execute("INSERT INTO responsaveis (telefone, nome_responsavel) VALUES (?, ?)", (telefone_cliente, nome_digitado))
                conectar.commit()
                conectar.close()

                resposta = f"{mensagens["boas_vindas"].format(primeiro_nome=nome_digitado.split()[0])}\n\n{mensagens["crianca_adulto"]}"
                
            # CRIANCA OU ADULTO?    

            elif "você ou para uma criança" in ultima_pergunta.lower():
                if texto_recebido == "crianca" or texto_recebido == "criança":
                    id_cliente = cliente["id_responsavel"]
                    filhos = buscar_criancas_do_adulto(id_cliente)
                    if filhos:
                        nomes_formatados = "\n".join([f"{c['nome_crianca']}" for c in filhos])
                        resposta = mensagens["criancas_cadastradas"].format(lista_criancas=nomes_formatados)
                    else:
                        resposta = mensagens["crianca_nova"]  

                elif texto_recebido == "adulto":
                    resposta = mensagens["agendamento"] 

                else:
                        resposta = "Por favor, responda com 'Adulto' ou 'Criança'."

            # CADASTRAR CRIANCA NOVA

            elif "criança nova aqui" in ultima_pergunta.lower():
                nome_crianca = texto_recebido.title()
                resposta = mensagens["crianca_nova_nasc"]

            elif "data de nascimento" in ultima_pergunta.lower():
                data_nascimento = formatar_data(texto_recebido)

                if data_nascimento:
                    id_adulto = cliente["id_responsavel"]
                    conectar = coneccao()
                    cursor = conectar.cursor()

                    cursor.execute("""SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao ='cliente' ORDER BY id DESC LIMIT 1 OFFSET 1""", (telefone_cliente,))
                    resultado = cursor.fetchone()

                    if resultado:
                        nome_crianca = resultado['mensagem'].title()

                        conectar.execute(
                            "INSERT INTO criancas (responsavel_id, nome_crianca, data_nascimento) VALUES (?, ?, ?)", 
                            (id_adulto, nome_crianca, data_nascimento)
                        )
                        conectar.commit()
                    conectar.close()    

                    resposta = mensagens["agendamento"]

                else:
                    resposta = "❌ Opa, não consegui entender. Por favor, digite a data de nascimento no formato Dia/Mês/Ano (Ex: 10/05/2018):"

                        
            elif "qual dia você prefere" in ultima_pergunta.lower():
                data_digitada = formatar_data(texto_recebido)
                if data_digitada:
                    horarios_dia = horarios_disponiveis(data_digitada)

                    if horarios_dia:
                        lista_horas = "\n".join([f"{h['data_hora'].split()[1]}" for h in horarios_dia])
                        resposta = mensagens["horarios_disponiveis"].format(lista_horarios=lista_horas)
                    else:
                        resposta = mensagens["data_indisponivel"]
                
                else:
                    resposta = "❌ Data inválida. Por favor, digite no formato Dia/Mês (Ex: 15/07)."

            else:
                resposta = "Ops, não entendi! 🤭 Digite 'Menu' para ver as opções."
    

            enviar_mensagem_whatsapp(telefone_cliente, resposta)
            
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)
