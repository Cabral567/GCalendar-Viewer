# 🗓️ PyGoogleCal - Widget de Calendário Google em Python

Um widget flutuante de desktop feito em Python que exibe os próximos eventos do seu Google Calendar. Ideal para manter seus compromissos visíveis enquanto trabalha.

![Licença](https://img.shields.io/badge/licença-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)

## ✅ Funcionalidades

- Interface flutuante usando `tkinter`
- Conexão com a Google Calendar API
- Atualização automática de eventos a cada 5 minutos
- Widget arrastável e sem bordas, sempre visível
- Modo escuro/claro
- Visualização por dia com indicador de cores do evento
- Suporte a eventos de dia inteiro e com horário específico

## 🚀 Como usar

1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/PyGoogleCal.git
   cd PyGoogleCal
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o acesso à API do Google Calendar:
   - Acesse o [Google Cloud Console](https://console.cloud.google.com/)
   - Crie um novo projeto
   - Ative a API do Google Calendar para o projeto
   - Configure a tela de consentimento OAuth (externo, pode ser de teste)
   - Crie credenciais **ID do cliente OAuth 2.0** (tipo: "Aplicativo para computador")
   - Adicione seu e-mail como **usuário de teste** na tela de consentimento OAuth
   - Baixe o arquivo JSON de credenciais e renomeie para `credentials.json`
   - Coloque o arquivo `credentials.json` na raiz do projeto

4. Execute o aplicativo:
   ```bash
   python app.py
   ```
  
## 🔐 O que acontece na primeira execução

1. O app abre o navegador solicitando que você **faça login com sua conta Google**.
2. Ele pede permissão para **acessar seus eventos do Google Calendar** (somente leitura).
3. Após o login, um arquivo `token.json` será salvo localmente com seu acesso.
4. O widget será exibido no seu desktop com os **próximos eventos**.

⚠️ Esse processo de login é feito **apenas na primeira vez**. Nas execuções seguintes, o app usará o token salvo e abrirá direto o widget.

## 📆 Requisitos

- Python 3.8+

- Bibliotecas:
  - `google-api-python-client`
  - `google-auth-oauthlib`
  - `google-auth-httplib2`
  - `tkinter` (vem embutido no Windows/macOS; no Linux: `sudo apt install python3-tk`)
  - `Pillow` (para processamento de imagens)

## 📂 Estrutura do Projeto

```
PyGoogleCal/
│
├── app.py                     # Ponto de entrada principal
├── credentials.example.json   # Exemplo da estrutura de credenciais necessária
├── requirements.txt           # Dependências do projeto
├── README.md                  # Este arquivo
├── LICENSE                    # Licença MIT
│
└── src/                       # Código fonte principal
    ├── __init__.py            # Marca o diretório como um pacote Python
    ├── main.py                # Módulo principal que integra os componentes
    ├── auth.py                # Autenticação com Google Calendar
    ├── calendar_api.py        # Interações com a API do Calendar
    ├── ui.py                  # Interface gráfica do usuário
    └── utils.py               # Funções utilitárias
```

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Abrir issues relatando bugs ou sugerindo recursos
2. Enviar pull requests com melhorias ou correções
3. Melhorar a documentação

## 📜 Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).



