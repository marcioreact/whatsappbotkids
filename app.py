import os
import requests
import sqlite3
from datetime import datetime, date, timedelta
import re
from texto import mensagens
from flask import Flask, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from waitress import serve

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

    cursor.execute("SELECT id, nome FROM responsaveis WHERE telefone = ?", (telefone,))
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

def enviar_mensagem_whatsapp(destinatario, texto):
    """Envia uma mensagem de texto usando a API do WhatsApp Business"""
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"
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
    ### porque tirou esse return
    return response.json()

def botoes(destinatario, texto, botoes_lista):
    url = f"https://graph.facebook.com/v23.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
        }
    botoes_meta = [{"type": "reply", "reply": {"id": b["id"], "title": b["titulo"]}} for b in botoes_lista]

    payload = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto
            },
            "action": {
                "buttons": botoes_meta
            }
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    ### porque tirou esse return
    return response.json()

def buscar_criancas_do_adulto(id_adulto):
    """Vai na tabela de crianças e busca todos os filhos atrelados a este adulto"""
    conectar = coneccao()
    cursor = conectar.cursor()
    cursor.execute("SELECT id, nome FROM criancas WHERE responsavel_id = ?", (id_adulto,))
    lista_criancas = cursor.fetchall()
    conectar.close()
    return lista_criancas

def horarios_disponiveis(data_desejada, tempo_servico, funcionario_id=None):
    """Busca horários verificando se os blocos subsequentes também estão livres"""
    conectar = coneccao()
    cursor = conectar.cursor()
    data = f"{data_desejada}%"

    if funcionario_id:
        cursor.execute("SELECT id, data_hora FROM horarios WHERE data_hora LIKE ? AND status = 'Disponível' AND funcionario_id = ? ORDER BY data_hora", (data, funcionario_id))
    else:
        cursor.execute("SELECT id, data_hora FROM horarios WHERE data_hora LIKE ? AND status = 'Disponível' ORDER BY data_hora", (data,))
    
    lista_horarios = cursor.fetchall()
    conectar.close()

    blocos_necessarios = max(1, tempo_servico // 30)
    horarios_validos = []
 
    for i in range(len(lista_horarios)):
        blocos_sequenciais_encontrados = 1
        hora_atual = datetime.strptime(lista_horarios[i]['data_hora'], '%d/%m/%Y %H:%M')

        for j in range(1, blocos_necessarios):
            if i + j < len(lista_horarios):
                proxima_hora_esperada = hora_atual + timedelta(minutes=30 * j)
                proxima_hora_real = datetime.strptime(lista_horarios[i+j]['data_hora'], '%d/%m/%Y %H:%M')

                if proxima_hora_real == proxima_hora_esperada:
                    blocos_sequenciais_encontrados += 1
                else:
                    break # Furo na agenda encontrado, quebra o loop
            else:
                break # Fim do dia, não cabe

        if blocos_sequenciais_encontrados == blocos_necessarios:
            horarios_validos.append(lista_horarios[i])

    return horarios_validos

def bloquear_horarios_sequenciais(horario_inicial_id, tempo_servico):
    """Altera o status do horário inicial e dos subsequentes para 'Agendado'"""
    conectar = coneccao()
    cursor = conectar.cursor()
    cursor.execute("SELECT data_hora, funcionario_id FROM horarios WHERE id = ?", (horario_inicial_id,))
    horario_base = cursor.fetchone()

    hora_atual = datetime.strptime(horario_base['data_hora'], '%d/%m/%Y %H:%M')
    blocos_necessarios = max(1, tempo_servico // 30)

    for j in range(blocos_necessarios):
        hora_bloco = (hora_atual + timedelta(minutes=30 * j)).strftime('%d/%m/%Y %H:%M')
        conectar.execute("UPDATE horarios SET status = 'Agendado' WHERE data_hora = ? AND funcionario_id = ?", (hora_bloco, horario_base['funcionario_id']))

    conectar.commit()
    conectar.close()

def liberar_horarios_sequenciais(horario_inicial_id, tempo_servico):
    conectar = coneccao()
    cursor = conectar.cursor()
    cursor.execute("SELECT data_hora, funcionario_id FROM horarios WHERE id = ?", (horario_inicial_id,))
    horario_base = cursor.fetchone()
    hora_atual = datetime.strptime(horario_base['data_hora'], '%d/%m/%Y %H:%M')
    blocos_necessarios = max(1, tempo_servico // 30)

    for j in range(blocos_necessarios):
        hora_bloco = (hora_atual + timedelta(minutes=30 * j)).strftime('%d/%m/%Y %H:%M')
        conectar.execute("UPDATE horarios SET status = 'Disponível' WHERE data_hora = ? AND funcionario_id = ?", (hora_bloco, horario_base['funcionario_id']))
    conectar.commit()
    conectar.close()

def buscar_agendamentos(id_cliente):
    """Busca os agendamentos ativos de um cliente e usa JOIN para trazer o nome do serviço, da criança e a data"""   
    conectar = coneccao()
    cursor = conectar.cursor()

    cursor.execute(
        """SELECT
        a.id AS id_agendamento,
        a.horario_id,
        s.nome_servico,
        s.tempo_servico,
        c.nome AS nome_crianca,
        h.data_hora
        FROM agendamentos a
        JOIN servicos s ON a.servico_id = s.id
        LEFT JOIN criancas c ON a.crianca_id = c.id
        JOIN horarios h ON a.horario_id = h.id
        WHERE a.responsavel_id = ? AND a.status = 'Agendado'
        """, (id_cliente,))
    
    agendamentos = cursor.fetchall()
    conectar.close()
    return agendamentos

def formatar_data(texto_digitado):
    """Converte o texto em uma data válida"""
    texto_limpo = texto_digitado.lower().strip()
    hoje = date.today()
    ano_atual = hoje.year
    data = None

    if "hoje" in texto_limpo or "hj" in texto_limpo: return hoje.strftime("%d/%m/%Y")
        
    if "amanha" in texto_limpo or "amanhã" in texto_limpo: return (hoje + timedelta(days=1)).strftime('%d/%m/%Y')

    meses = {"janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
    
    data_extensa = re.search(r"(\d{1,2})\s*(?:de)?\s*([a-zç]+)", texto_limpo)
    if data_extensa:
        dia, mes = int(data_extensa.group(1)), data_extensa.group(2)
        if mes in meses:
            mes_numero = meses[mes]
            ano = ano_atual + 1 if mes_numero < hoje.month or (mes_numero == hoje.month and dia < hoje.day) else ano_atual
            return f"{dia:02d}/{mes_numero:02d}/{ano}"
        
    data_numero = re.search(r"(\d{1,2})[-./](\d{1,2})(?:[-./](\d{2}|\d{4}))?", texto_limpo) 
    if data_numero and not data:
        dia, mes, ano = int(data_numero.group(1)), int(data_numero.group(2)), data_numero.group(3)
        if not ano:
            ano = ano_atual + 1 if mes < hoje.month or (mes == hoje.month and dia < hoje.day) else ano_atual
        elif len(str(ano)) == 2: ano = f"20{ano}"
        data = f"{dia:02d}/{mes:02d}/{ano}"
    
    data_dia = re.search(r'\b(\d{1,2})\b', texto_limpo)
    if data_dia and not data:
        dia = int(data_dia.group(1))

        if 1 <= dia <= 31:
            mes, ano = hoje.month, ano_atual
            if dia < hoje.day:
                mes += 1
                if mes > 12: mes, ano = 1, ano + 1
            data = f"{dia:02d}/{mes:02d}/{ano}"

    if data:
        try:
            data_conferida = datetime.strptime(data, '%d/%m/%Y')
            return data_conferida.strftime('%d/%m/%Y')
        except ValueError:
            return False
    return False   

def verificacao():
    """Roda em segundo plano para enviar confirmações, alertas e cancelamentos automáticos"""
    conectar = coneccao()
    cursor = conectar.cursor()
    agora = datetime.now() 

    daqui_24h = agora + timedelta(hours=24)
    inicio_janela, fim_janela = (daqui_24h - timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M'), (daqui_24h + timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M')

    cursor.execute("""
        SELECT a.id, r.telefone, h.data_hora 
        FROM agendamentos a 
        JOIN horarios h ON a.horario_id = h.id 
        JOIN responsaveis r ON a.responsavel_id = r.id
        WHERE a.status = 'Agendado' AND a.status_confirmacao = 'Pendente' 
        AND h.data_hora BETWEEN ? AND ?
    """, (inicio_janela, fim_janela))

    para_confirmar = cursor.fetchall()
    for ag in para_confirmar:
        msg = mensagens["confirmacao_24h"].format(horario=ag['data_hora'][-5:])
        botoes(ag['telefone'], msg, [{"id": "bnt_confirma", "titulo": "Sim"}, {"id": "bnt_nao_confirma", "titulo": "Não"}])
        armazenar_mensagem(ag['telefone'], msg, "bot")
        cursor.execute("UPDATE agendamentos SET status_confirmacao = 'Aguardando', hora_envio_notificacao = ? WHERE id = ?", (agora.strftime('%Y-%m-%d %H:%M:%S'), ag['id']))

    cursor.execute("""
        SELECT a.id, r.telefone 
        FROM agendamentos a 
        JOIN responsaveis r ON a.responsavel_id = r.id
        WHERE a.status = 'Agendado' AND a.status_confirmacao = 'Aguardando'
    """)

    aguardando = cursor.fetchall()
    for ag in aguardando:
        hora_envio = datetime.strptime(ag['hora_envio_notificacao'], '%Y-%m-%d %H:%M:%S')
        if agora >= hora_envio + timedelta(hours=1):
            enviar_mensagem_whatsapp(ag['telefone'], mensagens["alerta"])
            cursor.execute("UPDATE agendamentos SET status_confirmacao = 'Alerta' WHERE id = ?", (ag['id'],))

    cursor.execute("""
        SELECT a.id, a.horario_id, r.telefone 
        FROM agendamentos a 
        JOIN responsaveis r ON a.responsavel_id = r.id
        WHERE a.status = 'Agendado' AND (a.status_confirmacao = 'Aguardando' OR a.status_confirmacao = 'Alerta')
    """)

    para_cancelar = cursor.fetchall()
    for ag in para_cancelar:
        hora_envio = datetime.strptime(ag['hora_envio_notificacao'], '%Y-%m-%d %H:%M:%S')
        if agora >= hora_envio + timedelta(hours=3):
            enviar_mensagem_whatsapp(ag['telefone'], mensagens["sem_resposta"])
            cursor.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (ag['id'],))
            liberar_horarios_sequenciais(ag['horario_id'], ag['tempo_servico'])

    conectar.commit()
    conectar.close()

motor = BackgroundScheduler()
motor.add_job(verificacao, 'interval', minutes=5)
motor.start()  

# ROTAS DO FLASK

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
        texto_recebido = ""
        
        if mensagem_objeto["type"] == "text":
            texto_recebido = mensagem_objeto["text"]["body"].lower().strip()
        elif mensagem_objeto["type"] == "interactive":
            if mensagem_objeto["interactive"]["type"] == "button_reply":
                texto_recebido = mensagem_objeto["interactive"]["button_reply"]["id"].lower().strip()
            elif mensagem_objeto["interactive"]["type"] == "list_reply":
                texto_recebido = mensagem_objeto["interactive"]["list_reply"]["id"].lower().strip()

        if texto_recebido:
            armazenar_mensagem(telefone_cliente, texto_recebido, "cliente")
            ultima_pergunta = estado(telefone_cliente)
            cliente = verificar_cadastro(telefone_cliente)
            resposta =""

            # RESPOSTAS DA CONFIRMACAO (Sim / Nao)
            if texto_recebido == "bnt_confirma":
                conectar = coneccao()
                conectar.execute("UPDATE agendamentos SET status_confirmacao = 'Confirmado' WHERE responsavel_id = ? AND status = 'Agendado'", (cliente['id'],))
                conectar.commit()
                conectar.close()
                resposta = "Presença confirmada! Nos vemos no salão. 🥰" ###
            
            elif texto_recebido == "bnt_nao_confirma":
                conectar = coneccao()
                cursor = conectar.cursor()
                cursor.execute("""
                    SELECT a.id, a.horario_id, s.tempo_servico, s.nome_servico, h.data_hora 
                    FROM agendamentos a 
                    JOIN servicos s ON a.servico_id = s.id 
                    JOIN horarios h ON a.horario_id = h.id
                    WHERE a.responsavel_id = ? AND a.status = 'Agendado' AND a.status_confirmacao IN ('Aguardando', 'Alerta', 'Pendente')
                """, (cliente['id'],))
                ags = cursor.fetchall()

                for ag in ags:
                    conectar.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (ag['id'],))
                    conectar.commit()

                    liberar_horarios_sequenciais(ag['horario_id'], ag['tempo_servico'])

                conectar.close()
                resposta = mensagens["cancelado"]

            # PRIMEIRO CONTATO (ENVIA O MENU)

            elif not ultima_pergunta or texto_recebido == "menu":
                if cliente:
                    resposta = mensagens["menu_inicial_cliente"].format(nome=cliente["nome"].split()[0])
                else:
                    resposta = mensagens["menu_inicial"]

            # OPCOES DO MENU QUE NAO PRECISAM DE CADASTRO

            # SERVIÇOS E VALORES (OPCAO 2)
            elif texto_recebido == "2" and "como posso te ajudar" in ultima_pergunta.lower():
                conectar = coneccao()
                cursor = conectar.cursor()
                cursor.execute("SELECT nome_servico, valor FROM servicos")
                lista_servicos = cursor.fetchall()
                conectar.close()

                resposta = mensagens["servicos_valores"].format(servicos=lista_servicos)

            # FALE CONOSCO (OPÇÃO 4 OU 3)
            elif texto_recebido == "4" and "como posso te ajudar" in ultima_pergunta.lower(): # Converse conosco
                resposta = mensagens["converse_conosco"]

                # porque tirou?
                num_tesourinha = "5571999999999"
                nome_cliente = cliente["nome_responsavel"].split()[0]
                notificar = mensagens["notificacao"].format(nome=nome_cliente)
                enviar_mensagem_whatsapp(num_tesourinha, notificar)

            # OPCAO DO MENU QUE PRECISA DE CADASTRO

            # (CANCELAMENTO (OPCAO 3)
            elif texto_recebido == "3" and "como posso te ajudar" in ultima_pergunta.lower():
                agendamentos_ativos = buscar_agendamentos(cliente['id'])
                
                if agendamentos_ativos:
                    agendamentos_formatados = "\n".join(f"{i}. {a['nome_servico']} ({a['nome_crianca'] or 'Adulto'}) - {a['data_hora']}" for i, a in enumerate(agendamentos_ativos, start=1))
                    resposta = mensagens["agendamentos_cancelar"].format(agendamentos=agendamentos_formatados)
                else:
                    resposta = mensagens["erro_cancelamento"]

            elif "deseja cancelar" in ultima_pergunta.lower():
                numero_escolhido = texto_recebido.strip()

                if numero_escolhido.isdigit():
                    escolha = int(numero_escolhido)
                    agendamentos = buscar_agendamentos(cliente['id'])
                    
                    if escolha == 0:
                        resposta = mensagens["cancelamento_cancelado"]

                    elif 1 <= escolha <= len(agendamentos):
                        alvo = agendamentos[escolha - 1]
                        resposta_botoes = mensagens["confirmar_cancelamento"].format(servico=alvo["nome_servico"], data_horario=alvo["data_hora"])
                        botoes(telefone_cliente, resposta_botoes, [{"id" : "bnt_sim", "titulo" : "Sim"}, {"id" : "bnt_nao", "titulo" : "Não"}])
                        armazenar_mensagem(telefone_cliente, resposta_botoes, "bot") 
                        resposta = ""
                    else:
                        resposta = mensagem["invalida1"]
                else:
                    resposta = mensagem["invalida2"]
                
            elif "confirma o cancelamento" in ultima_pergunta.lower():
                if texto_recebido == "bnt_sim":
                    conectar = coneccao()
                    cursor = conectar.cursor()
                    cursor = cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'cliente' ORDER BY id DESC LIMIT 1 OFFSET 1", (telefone_cliente,))
                    resultado = cursor.fetchone()

                    if resultado and resultado["mensagem"].isdigit():
                        escolha = int(resultado["mensagem"])
                        agendamentos = buscar_agendamentos(cliente['id'])

                        # acrescentar a opção se o cliente selecionar 0 que é "nenhum, mudei de ideia"

                        if 1 <= escolha <= len(agendamentos):
                            alvo = agendamentos[escolha - 1]
                            conectar.execute("UPDATE agendamentos SET status = 'Cancelado' WHERE id = ?", (alvo['id_agendamento'],))
                            conectar.commit()
        
                            liberar_horarios_sequenciais(alvo['horario_id'], alvo['tempo_servico'])
                            
                            num_tesourinha = "5571999999999"
                            nome_cliente = cliente["nome"].split()[0]
                            adulto_crianca = f"da criança {alvo['nome_crianca']}" if alvo['nome_crianca'] else f"do(a) cliente {nome_cliente}"
                            mensagem = mensagens["notificacao_cancelamento"].format(adulto_crianca=adulto_crianca, servico=alvo['nome_servico'], horario=alvo['data_hora'][:16])
                            enviar_mensagem_whatsapp(num_tesourinha, mensagem)

                    conectar.close()
                    resposta = mensagens["cancelado"]
            
                elif texto_recebido == "bnt_nao" or texto_recebido == "0":
                    resposta = mensagens["cancelamento_cancelado"]

            # AGENDAMENTO (OPCAO 1)
            elif texto_recebido == "1" and "como posso te ajudar" in ultima_pergunta.lower():
                if not cliente:
                    resposta = mensagens["cadastro"]
                else:
                    resposta_botoes = mensagens["crianca_adulto"]
                    botoes(telefone_cliente, resposta, [{"id": "bnt_c", "titulo": "Criança"}, {"id": "bnt_a", "titulo": "Para mim"}])
                    armazenar_mensagem(telefone_cliente, resposta_botoes, "bot")
                    resposta = ""

            # REALIZACAO DO CADASTRO

            elif "me informe seu nome" in ultima_pergunta.lower():
                nome_digitado = texto_recebido.title()

                conectar = coneccao()
                conectar.execute("INSERT INTO responsaveis (telefone, nome) VALUES (?, ?)", (telefone_cliente, nome_digitado))
                conectar.commit()
                conectar.close()

                resposta_botoes = f"{mensagens['boas_vindas'].format(primeiro_nome=nome_digitado.split()[0])}\n\n{mensagens['crianca_adulto']}"
                botoes(telefone_cliente, resposta_botoes, [{"id": "bnt_c", "titulo": "Criança"}, {"id": "bnt_a", "titulo": "Para mim"}])
                armazenar_mensagem(telefone_cliente, resposta_botoes, "bot")
                resposta = ""
                
            # CRIANCA OU ADULTO?    

            elif "você ou para uma criança" in ultima_pergunta.lower():
                if texto_recebido == "bnt_c": 
                    filhos = buscar_criancas_do_adulto(cliente['id'])
                    if filhos:
                        nomes_formatados = "\n".join([f"{c['nome']}" for c in filhos])
                        resposta = mensagens["criancas_cadastradas"].format(lista_criancas=nomes_formatados)
                    else:
                        resposta = mensagens["crianca_nova_nome"]  

                elif texto_recebido == "bnt_a": 
                    conectar = coneccao()
                    cursor = conectar.cursor()

                    cursor.execute("SELECT id, nome_servico FROM servicos")

                    lista = "\n".join(f"{s['id']}. {s['nome_servico']}" for s in cursor.fetchall())
                    conectar.close()
                    resposta = mensagens["escolher_servico"].format(lista_servicos=lista) 

            # CADASTRAR CRIANCA NOVA

            elif "nome completo da criança" in ultima_pergunta.lower():
                resposta = mensagens["crianca_nova_nasc"].format(nome_crianca=texto_recebido.title())

            elif "data de nascimento" in ultima_pergunta.lower():
                data_nascimento = formatar_data(texto_recebido)

                if data_nascimento:
                    conectar = coneccao()
                    cursor = conectar.cursor()
                    cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao ='cliente' ORDER BY id DESC LIMIT 1 OFFSET 1", (telefone_cliente,))
                    resultado = cursor.fetchone()

                    if resultado:
                        nome_crianca = resultado['mensagem'].title()
                        conectar.execute("INSERT INTO criancas (responsavel_id, nome, data_nascimento) VALUES (?, ?, ?)", (cliente['id'], nome_crianca, data_nascimento))
                        conectar.commit()

                    cursor.execute("SELECT id, nome_servico FROM servicos")
                    lista = "\n".join(f"{s['id']}. {s['nome_servico']}" for s in cursor.fetchall())
                    conectar.close()
                    resposta = mensagens["escolher_servico"].format(lista_servicos=lista)
                else:
                    resposta = mensagens["data_invalida"]

            elif "qual serviço você deseja" in ultima_pergunta.lower():
                if texto_recebido.isdigit():
                    resposta = mensagens["agendamento"]
                else:
                    resposta = mensagens["invalida2"]

            elif "qual dia você prefere" in ultima_pergunta.lower() or "deseja escolher outra data" in ultima_pergunta.lower():
                data_digitada = formatar_data(texto_recebido)
                if data_digitada:
                    conectar = coneccao()
                    cursor = conectar.cursor()
                    cursor.execute("SELECT profissional_preferido FROM responsaveis WHERE id = ?", (cliente['id'],))
                    preferido = cursor.fetchone()['profissional_preferido']

                    cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'cliente' AND mensagem NOT LIKE 'bnt_%' ORDER BY id DESC", (telefone_cliente,))
                    id_servico = None
                    for row in cursor.fetchall():
                        if row['mensagem'].isdigit():
                            id_servico = row['mensagem']
                            break
                    
                    cursor.execute("SELECT tempo_servico FROM servicos WHERE id = ?", (id_servico,))
                    tempo_servico = cursor.fetchone()['tempo_servico']

                    if preferido:
                        cursor.execute("SELECT nome FROM funcionarios WHERE id = ?", (preferido,))
                        nome_prof = cursor.fetchone()['nome']
                        horarios_dia = horarios_disponiveis(data_digitada, tempo_servico, preferido)

                        if horarios_dia:
                            lista_horas = "\n".join([f"{h['data_hora'].split()[1]}" for h in horarios_dia])
                            resposta = mensagens["horarios_disponiveis"].format(profissional=nome_prof, lista_horarios=lista_horas)
                        else:
                            msg_outros = mensagens["outro_profissional"].format(profissional=nome_prof)
                            botoes(telefone_cliente, msg_outros, [{"id": "bnt_ver_outros", "titulo": "Ver outros"}, {"id": "bnt_outra_data", "titulo": "Mudar Data"}])
                            armazenar_mensagem(telefone_cliente, msg_outros, "bot")
                            resposta = ""
                    else:
                        # Se não tem preferido, mostra todos
                        horarios_dia = horarios_disponiveis(data_digitada, tempo_servico)
                        if horarios_dia:
                            lista_horas = "\n".join([f"{h['data_hora'].split()[1]}" for h in horarios_dia])
                            resposta = mensagens["horarios_disponiveis"].format(profissional="nossa equipe", lista_horarios=lista_horas)
                        else:
                            resposta = mensagens["data_indisponivel"]
                    conectar.close()
                else:
                    resposta = mensagem["data_invalida"]

            elif "deseja ver os horários deles" in ultima_pergunta.lower():
                if texto_recebido == "bnt_outra_data":
                    resposta = mensagens["agendamento"]

                elif texto_recebido == "bnt_ver_outros":
                    conectar = coneccao()
                    cursor = conectar.cursor()
                    cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'cliente' ORDER BY id DESC", (telefone_cliente,))
                    historico = cursor.fetchall()
                    data_salva, id_servico = None, None
                    for item in historico:
                        msg = item['mensagem']
                        if not data_salva and formatar_data(msg):
                            data_salva = formatar_data(msg)
                            continue
                        if data_salva and msg.isdigit():
                            id_servico = msg
                            break
                    cursor.execute("SELECT tempo_servico FROM servicos WHERE id = ?", (id_servico,))
                    tempo_servico = cursor.fetchone()['tempo_servico']
                    
                    horarios_dia = horarios_disponiveis(data_salva, tempo_servico)

                    if horarios_dia:
                        lista_horas = "\n".join([f"{h['data_hora'].split()[1]}" for h in horarios_dia])
                        resposta = mensagens["horarios_disponiveis"].format(profissional="nossa equipe", lista_horarios=lista_horas)
                    else:
                        resposta = mensagens["data_indisponivel"]
                    conectar.close()

            elif "qual horário deseja" in ultima_pergunta.lower():
                hora_escolhida = texto_recebido.strip()

                if re.match(r"^\d{2}:\d{2}$", hora_escolhida):
                    conectar = coneccao()
                    cursor = conectar.cursor()
                    
                    cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND direcao = 'cliente' ORDER BY id DESC", (telefone_cliente,))
                    historico = cursor.fetchall()
                    data_salva, id_servico = None, None
                    for item in historico:
                        msg = item['mensagem']
                        if not data_salva and formatar_data(msg):
                            data_salva = formatar_data(msg)
                            continue
                        if data_salva and msg.isdigit():
                            id_servico = msg
                            break

                    cursor.execute("SELECT id, tempo_servico FROM servicos WHERE id = ?", (id_servico,))
                    servico = cursor.fetchone()
                    
                    cursor.execute("SELECT profissional_preferido FROM responsaveis WHERE id = ?", (cliente['id'],))
                    preferido = cursor.fetchone()['profissional_preferido']
                    data_hora_completa = f"{data_salva} {hora_escolhida}"
                    
                    if preferido:
                        cursor.execute("SELECT id FROM horarios WHERE data_hora = ? AND status = 'Disponível' AND funcionario_id = ?", (data_hora_completa, preferido))
                    else:
                        cursor.execute("SELECT id FROM horarios WHERE data_hora = ? AND status = 'Disponível'", (data_hora_completa,))
                        
                    horario_alvo = cursor.fetchone()
                    
                    if horario_alvo:
                        cursor.execute("SELECT mensagem FROM mensagens WHERE telefone_cliente = ? AND mensagem IN ('bnt_c', 'bnt_a') ORDER BY id DESC LIMIT 1", (telefone_cliente,))
                        tipo_agendamento = cursor.fetchone()
                        
                        crianca_id = None
                        if tipo_agendamento and tipo_agendamento['mensagem'] == 'bnt_c':
                            cursor.execute("SELECT id FROM criancas WHERE responsavel_id = ? ORDER BY id DESC LIMIT 1", (cliente['id'],))
                            c_id = cursor.fetchone()
                            if c_id:
                                crianca_id = c_id['id']
                        
                        conectar.execute("INSERT INTO agendamentos (responsavel_id, crianca_id, servico_id, horario_id) VALUES (?, ?, ?, ?)", 
                                         (cliente['id'], crianca_id, servico['id'], horario_alvo['id']))
                        conectar.commit()
                        
                        bloquear_horarios_sequenciais(horario_alvo['id'], servico['tempo_servico'])
                        resposta = mensagens["agendado"]
                    else:
                        resposta = "❌ Esse horário não está mais disponível ou é inválido. Por favor, digite outro horário da lista."
                    conectar.close()
                else:
                    resposta = "❌ Formato de hora inválido. Digite no formato HH:MM (Ex: 14:30)."

            else:
                resposta = mensagens["nao_entendi"]
    
            if resposta != "":
                armazenar_mensagem(telefone_cliente, resposta, "bot")
                enviar_mensagem_whatsapp(telefone_cliente, resposta)
            
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
