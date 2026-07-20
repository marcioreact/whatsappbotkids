<div align="center">

# 💇‍♀️✨ Salão de Beleza Infantil Tesourinha da Beleza Kids Bot

### Chatbot para atendimento automatizado via WhatsApp de um salão de beleza infantil

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_API-black?style=for-the-badge&logo=flask)
![WhatsApp](https://img.shields.io/badge/WhatsApp-Cloud_API-25D366?style=for-the-badge&logo=whatsapp)
![Meta](https://img.shields.io/badge/Meta-Business-1877F2?style=for-the-badge&logo=meta)

---

### 👧 Atendimento inteligente para pais e responsáveis

Agendamento • Informações • Catálogo de serviços • Horários • Localização

</div>

---

# 📋 Funcionalidades

✅ Atendimento automático

✅ Menu interativo

✅ Agendamento

✅ Consulta de horários

✅ Informações sobre serviços

✅ Localização

✅ Encaminhamento para atendente

✅ Mensagens personalizadas

---

# 🏗 Arquitetura

```mermaid
flowchart LR

A[Cliente WhatsApp]

A --> B[WhatsApp Cloud API]

B --> C[Webhook Flask]

C --> D[Motor do Chatbot]

D --> E[Banco de Dados]

D --> F[Agenda]

D --> G[Atendente]
```

---

# 💬 Fluxo da Conversa

```mermaid
flowchart TD

A(Início)

A --> B[Boas-vindas]

B --> C{Escolha}

C --> D[Agendar]

C --> E[Serviços]

C --> F[Horários]

C --> G[Localização]

C --> H[Falar com atendente]

D --> I[Fim]

E --> I

F --> I

G --> I

H --> I
```

---

# 🛠 Tecnologias

| Tecnologia | Utilização |
|------------|------------|
| Python | Backend |
| Flask | Webhook |
| WhatsApp Cloud API | Comunicação |
| Meta Business | Gerenciamento |
| Ngrok | Desenvolvimento |
| Git | Versionamento |

---

# 🔗 Integração

```
Cliente

↓

WhatsApp

↓

Meta Cloud API

↓

Webhook

↓

Flask

↓

Chatbot

↓

Resposta
```

---

# 🎯 Objetivos

- Automatizar atendimento

- Reduzir tempo de resposta

- Facilitar agendamentos

- Melhorar experiência dos clientes

- Integrar com WhatsApp Business

---

# 📈 Melhorias Futuras

- IA para respostas inteligentes

- Integração com Google Agenda

- Painel administrativo

- Dashboard

- Histórico de atendimentos

- Banco de dados

- Envio de lembretes

- Avaliação do atendimento

---

</div>
