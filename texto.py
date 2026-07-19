mensagens = {
    # Mensagens iniciais + menus

    "menu_inicial_cliente": (
                    "Olá! 👋 {nome} Que bom ter você de volta! 🥰\n\n"
                    "📍 Onde estamos: Rua Alameda Dilson Jatahy Fonseca, Edf. Empresarial Nossa Senhora de Fátima, 1255.\n"
                    "⏰ Nosso Horário:\n"
                    "Ter a Sex: 09h às 12h e 14:30h às 18h\n"
                    "Sábados: 09h às 18h\n"
                    "*(Segundas e Domingos: Fechado)*\n\n"
                    "Como posso te ajudar hoje? Por favor, digite o número da opção desejada:\n"
                    "1️⃣ Agendar um horário\n"
                    "2️⃣ Ver nossos serviços e valores\n"
                    "3️⃣ Cancelar um horário\n"
                    "4️⃣ Falar com a nossa equipe"
                ),

    "menu_inicial" : (
                    "Olá! 👋 Bem-vindo(a) ao Tesourinha da Beleza Kids, o primeiro salão de beleza infantil em Stella Maris!\n\n"
                    "📍 Onde estamos: Rua Alameda Dilson Jatahy Fonseca, Edf. Empresarial Nossa Senhora de Fátima, 1255.\n"
                    "⏰ Nosso Horário:\n"
                    "Ter a Sex: 09h às 12h e 14:30h às 18h\n"
                    "Sábados: 09h às 18h\n"
                    "*(Segundas e Domingos: Fechado)*\n\n"
                    "Como posso te ajudar hoje? Por favor, digite o número da opção desejada:\n"
                    "1️⃣ Agendar um horário\n"
                    "2️⃣ Ver nossos serviços e valores\n"
                    "3️⃣ Falar com a nossa equipe"
                ),

    # Mensagens de cadastro
    "cadastro" : "Maravilha! É um prazer ter você com a gente ☺️.  Para que eu possa organizar o seu agendamento, me informe seu nome completo, por favor?",
    "boas_vindas" : "Muito prazer, {primeiro_nome}!😃",
    "crianca_adulto" : "O agendamento é para você ou para uma criança?",
    "crianca_nova_nome" : (
        "Oba! Que alegria receber uma criança nova aqui no Tesourinha! 🎉\n"
        "Para que eu possa organizar o agendamento e deixar tudo pronto para receber vocês, me informe o nome completo da criança, por favor? ☺️"
    ),
    "crianca_nova_nasc" : "Que nome lindo! 😍 Qual é a data de nascimento do(a) {nome_crianca}? (Exemplo: 10/05/2018)",
    "criancas_cadastradas" : "Perfeito! O atendimento é para quem?\n{lista_criancas}\nOu para outra criança?",

    # Mensagens de agendamento
    "escolher_servico" : "Ótimo! Qual serviço você deseja realizar?\n{lista_servicos}\n\n*Digite o número do serviço:*",
    "agendamento" : "Perfeito! Agora me diga: qual dia você prefere para o atendimento?",
    "horarios_disponiveis" : (
        "Maravilha! Dá uma olhadinha nos horários que temos livres:\n{lista_horarios}\n\n"
        "Algum desses horários fica bom para você? ☺️"
    ),
    "outro_profissional" : "Infelizmente o(a) {profissional} não tem horários disponíveis para esse serviço neste dia. 😕\nMas temos vagas com outros excelentes profissionais! Deseja ver os horários deles ou escolher outra data?",
    "data_indisponivel" : (
        "Infelizmente não temos mais horário para esse dia😕\n"
        "Deseja escolher outra data?"
    ), 
    "agendado" : "Tudo certo! Seu horário foi agendado com sucesso🎉 Na véspera do atendimento, eu te mando uma mensagem para confirmarmos, combinado?😉",

    # Mensagens de Confirmacao
    "confirmacao_24h" : (
        "Olá! 👋 Passando para confirmar o horário agendado no Tesourinha amanhã às {horario}.\n"
        "Você confirma a presença?\n"
        "⚠️ Obs: Se a mensagem não for respondida dentro de *3 horas* seu horário será CANCELADO!"
    ),
    "alerta" : "⚠️ Ainda não obtivemos a confirmação, peço que confirme, caso contrário seu horário será CANCELADO!",
    "reconfirmacao_2h" : (
        "Falta pouco para o nosso encontro hoje às {horario} Estamos te esperando!😃 Confirma a presença?\n"
        "⚠️ Obs: Se a mensagem não for respondida dentro de 1 hora e 30 minutos seu horário será CANCELADO!"
    ),
    "sem_resposta" : (
        "Poxa, como não recebi o seu retorno, precisei cancelar o horário e liberar a vaga 🥺. Se quiser tentar um novo agendamento, é só digitar 1!\n"
        "Esperamos ver você em breve!"
    ),

    # Mensagens de Cancelamento
    "cancelado" : "Sinto muito que não possa comparecer🥺 Seu horário foi cancelado e a vaga liberada. Esperamos ver você em breve!",
    "agendamentos_cancelar" : "Qual desses agendamentos você deseja cancelar?\n0. Nenhum, mudei de ideia\n{agendamentos}\n\n*Por favor, digite o NÚMERO do horário que deseja cancelar:*",
    "confirmar_cancelamento" : "Confirma o cancelamento do(a) {servico} {data_horario}?",
    "cancelamento_cancelado" : "Ufa! Cancelamento abortado. Seu horário continua garantido! 🥰\nDigite 'Menu' se precisar de mais alguma coisa.",
    "erro_cancelamento" : "Você não possui nenhum agendamento ativo no momento para cancelar. 😊",
    "notificacao_cancelamento" : (
        "ALERTA DE CANCELAMENTO\n\n"
        "O agendamento de {adulto_crianca} foi cancelado!\n"
        "Serviço: {servico}\n"
        "Data/hora: {horario}\n\n"
        "A vaga já foi liberada no sistema!"
    ),

    # Mensagem de servicos e valores
    "servicos_valores" : "Aqui estão nossos principais serviços, feitos com muito carinho e cuidado! 😍\n{servicos}\n\n*Gostaria de agendar um horário agora?*",

    # Mensagem de converse conosco
    "converse_conosco" : (
        "Entendido! Vou transferir você para a nossa equipe. Por favor, aguarde um instante que logo alguém entrará em contato para te atender 💬\n\n"
        "Enquanto isso, você também pode nos acompanhar ou entrar em contato por aqui:\n"
        "📸 Instagram: @tesourinhadabelezakids\n"
        "🌐 Site: trinks.com/tesourinha-da-beleza-kids-\n"
        "☎️ Telefone: 3190-8252"
    ),
    "notificacao" : "O(A) Cliente {nome} deseja entrar em contato com a equipe do salão Tesourinha Kids ",

    # Mensagens para respostas inválidas
    "invalida1" : "❌ Opção inválida. Por favor digite um número que está na lista. Qual deseja cancelar?",
    "invalida2" : "❌ Opção inválida. Digite apenas o número respectivo ao horário que deseja cancelar",
    "data_invalida" : "❌ Opa, não consegui entender. Por favor, digite a data no formato Dia/Mês/Ano (Ex: 10/05/2018)",
    "nao_entendi" : "Ops, não entendi!"
}
