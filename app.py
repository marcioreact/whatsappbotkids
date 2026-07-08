import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

ACCESS_TOKEN = "EAAMagaZAploIBR5EZBTLgsuia18OetyIr5kQwI86yuRZAQMNNA0OOdU73p5oMKWtkTcJunkIdeB3fInvhxrbQJasBofq0Ri6cL2gsCSMmHz0s8T61OxlFXDOvEdcwcfVlcuW6ZBYbNnUnsVDzZBrUuz0ZCyl0D0AAqXZCicpaq1q6ebJQ4QVByYHR598QQF108Xvf3V40J3QonHdFKIn491oKZALYy5ebMZCzRAJpzDv5eC369vWbcuL4dlrDNAVMJJs9ZCSSrUd37Pxy8JpO9g1NtfAlI"
PHONE_NUMBER_ID = "1068403969700473"
VERIFY_TOKEN = "MeuTokenUltraSecretoSalaoKids2026"

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
            
            if texto_recebido in ["oi", "olá", "ola", "bom dia", "boa tarde", "menu"]:
                resposta = (
                    "✨ *Bem-vindo ao Salão Tesourinha da Beleza Kids!* ✨\n\n"
                    "Aqui o corte de cabelo vira uma grande diversão! 🎪🍿\n"
                    "Digite o número da opção desejada:\n\n"
                    "1️⃣ - Agendar um horário\n"
                    "2️⃣ - Ver serviços e valores 💇‍♂️💅\n"
                    "3️⃣ - Nosso endereço e horários 📍\n"
                    "4️⃣ - Falar com uma atendente humana 🙋‍♀️"
                )
            elif texto_recebido == "1":
                resposta = (
                    "📅 *Agendamento Prático*\n\n"
                    "Para agendar, por favor nos envie:\n"
                    "• Nome da criança:\n"
                    "• Idade:\n"
                    "• Dia e horário de preferência:\n\n"
                    "Nossa equipe vai validar a vaga em instantes!"
                )
            elif texto_recebido == "2":
                resposta = (
                    "🎨 *Nossos Serviços:*\n\n"
                    "• *Corte Kids (com direito a videogame):* R$ 60\n"
                    "• *Penteado Divertido com Glitter:* R$ 40\n"
                    "• *Manicure Clássica Infantil:* R$ 25\n"
                    "• *Combo Corte + Lavagem + Brinde:* R$ 80"
                )
            elif texto_recebido == "3":
                resposta = (
                    "📍 *Onde Estamos:*\n"
                    "Edf. Empresarial Nossa Senhora de Fátima - Alameda Dilson Jatahy Fonseca, 1255 - Stella Maris, Salvador - BA\n\n"
                    "⏰ *Horário de Funcionamento:*\n"
                    "Terça a Sábado: 09h às 18h"
                )
            elif texto_recebido == "4":
                resposta = "⏳ Entendido! Um de nossos atendentes já vai assumir a conversa para te ajudar de forma personalizada. Aguarde um momentinho!"
            else:
                resposta = "Ops! Não entendi. 🤭\nDigite *MENU* para ver as opções disponíveis."

            enviar_mensagem_whatsapp(telefone_cliente, resposta)
            
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)
