import tkinter as tk
from datetime import datetime, timedelta, date
import calendar
import os.path
import threading
from PIL import Image, ImageTk
import requests
from io import BytesIO

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Escopo da API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Cores do Google Calendar
CORES = {
    'azul': '#4285F4',     # Azul principal do Google
    'vermelho': '#EA4335', # Vermelho Google
    'amarelo': '#FBBC05',  # Amarelo Google
    'verde': '#34A853',    # Verde Google
    'cinza_claro': '#F1F3F4', # Fundo claro do Google Calendar
    'cinza_texto': '#3C4043',  # Cor padrão de texto
    'cinza_data': '#5F6368',   # Cor secundária (data)
    'branco': '#FFFFFF',
}

# Cores do modo escuro
CORES_DARK = {
    'azul': '#8AB4F8',     # Azul mais claro para modo escuro
    'vermelho': '#F28B82', # Vermelho adaptado para modo escuro
    'amarelo': '#FDD663',  # Amarelo adaptado para modo escuro
    'verde': '#81C995',    # Verde adaptado para modo escuro
    'cinza_claro': '#202124', # Fundo escuro do Google Calendar
    'cinza_texto': '#E8EAED',  # Cor padrão de texto (claro)
    'cinza_data': '#9AA0A6',   # Cor secundária (data) mais clara
    'branco': '#2D2E30',     # Fundo dos cards
}

# Variável global para controlar o modo atual
modo_dark = False
cores_atuais = CORES

def alternar_modo():
    global modo_dark, cores_atuais
    modo_dark = not modo_dark
    cores_atuais = CORES_DARK if modo_dark else CORES
    # A interface será recriada com as novas cores

def autenticar_google_calendar():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_inicio_fim_mes():
    """Retorna o início e fim do mês atual em formato ISO."""
    hoje = date.today()
    primeiro_dia = date(hoje.year, hoje.month, 1)
    
    # Último dia do mês atual
    if hoje.month == 12:
        ultimo_dia = date(hoje.year + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(hoje.year, hoje.month + 1, 1) - timedelta(days=1)
    
    # Formatando para ISO
    inicio = datetime.combine(primeiro_dia, datetime.min.time()).isoformat() + 'Z'
    fim = datetime.combine(ultimo_dia, datetime.max.time()).isoformat() + 'Z'
    
    return inicio, fim

def buscar_eventos(service, max_results=50):
    # Definir período para o mês atual inteiro
    inicio, fim = get_inicio_fim_mes()
    
    print(f"Buscando eventos entre {inicio} e {fim}")
    
    events_result = service.events().list(
        calendarId='primary', 
        timeMin=inicio,
        timeMax=fim,
        maxResults=max_results, 
        singleEvents=True,
        orderBy='startTime').execute()
    
    return events_result.get('items', [])

def formatar_evento(event):
    try:
        # Obter data e hora de início
        inicio = event['start'].get('dateTime', event['start'].get('date'))
        
        # Tratando formato de data diferente
        if 'Z' in inicio:
            # Formato ISO com timezone
            data_inicio = datetime.fromisoformat(inicio.replace('Z', '+00:00'))
        elif 'T' in inicio:
            # Formato ISO sem timezone
            data_inicio = datetime.fromisoformat(inicio)
        else:
            # Formato simples de data (AAAA-MM-DD)
            data_inicio = datetime.strptime(inicio, '%Y-%m-%d')
        
        # Verificar se é um evento de dia inteiro
        if 'date' in event['start'] and 'dateTime' not in event['start']:
            evento = {
                'dia_inteiro': True,
                'data': data_inicio.strftime('%d/%m/%Y'),
                'data_curta': data_inicio.strftime('%d/%m'),
                'titulo': event.get('summary', 'Evento sem título'),
                'cor': event.get('colorId', '1'),  # Cor padrão se não especificada
                'data_obj': data_inicio,  # Para ordenação
            }
        else:
            # Evento com hora marcada
            evento = {
                'dia_inteiro': False,
                'data': data_inicio.strftime('%d/%m/%Y'),
                'data_curta': data_inicio.strftime('%d/%m'),
                'hora': data_inicio.strftime('%H:%M'),
                'titulo': event.get('summary', 'Evento sem título'),
                'cor': event.get('colorId', '1'),  # Cor padrão se não especificada
                'data_obj': data_inicio,  # Para ordenação
            }
            
        return evento
    except Exception as e:
        print(f"Erro ao formatar evento: {str(e)}")
        print(f"Evento problemático: {event}")
        # Retorna um evento genérico para não quebrar a aplicação
        return {
            'dia_inteiro': False,
            'data': datetime.now().strftime('%d/%m/%Y'),
            'data_curta': datetime.now().strftime('%d/%m'),
            'hora': '??:??',
            'titulo': f"Erro no evento: {e}",
            'cor': '1',
            'data_obj': datetime.now(),
        }

def criar_botao_toggle(parent, is_on=False):
    """Cria um botão de toggle estilo on/off"""
    toggle_frame = tk.Frame(parent, height=22, width=44, bg=cores_atuais['branco'])
    toggle_frame.pack_propagate(False)  # Manter o tamanho fixo
    
    # Cores do botão
    bg_on = "#34A853"  # Verde Google
    bg_off = "#9AA0A6"  # Cinza do Google
    
    # Criar o botão toggle
    toggle_button = tk.Frame(toggle_frame, width=44, height=22, bg=bg_on if is_on else bg_off, cursor="hand2")
    toggle_button.pack(fill="both", expand=True)
    toggle_button.pack_propagate(False)
    
    # Botão deslizante
    slider = tk.Frame(toggle_button, width=18, height=18, bg=cores_atuais['branco'], 
                   highlightthickness=0, bd=0)
    slider.place(x=22 if is_on else 4, y=2)
    
    # Texto de status
    text_var = tk.StringVar(value="ON" if is_on else "OFF")
    status_text = tk.Label(toggle_button, textvariable=text_var, fg=cores_atuais['branco'],
                       bg=bg_on if is_on else bg_off, font=("Arial", 8, "bold"))
    status_text.place(x=6 if is_on else 20, y=2)
    
    def toggle():
        nonlocal is_on
        is_on = not is_on
        if is_on:
            toggle_button.config(bg=bg_on)
            status_text.config(bg=bg_on)
            slider.place(x=22, y=2)
            text_var.set("ON")
            status_text.place(x=6, y=2)
        else:
            toggle_button.config(bg=bg_off)
            status_text.config(bg=bg_off)
            slider.place(x=4, y=2)
            text_var.set("OFF")
            status_text.place(x=20, y=2)
        
        # Chamar a função de alternar modo
        reconstruir_interface(toggle_button.winfo_toplevel(), alternar_modo)
    
    # Vincular o evento de clique
    toggle_button.bind("<Button-1>", lambda e: toggle())
    slider.bind("<Button-1>", lambda e: toggle())
    status_text.bind("<Button-1>", lambda e: toggle())
    
    return toggle_frame

def criar_interface():
    global cores_atuais
    # Criar janela principal
    root = tk.Tk()
    root.overrideredirect(True)  # sem bordas
    root.attributes('-topmost', False)
    root.after(10, lambda: root.wm_attributes("-topmost", False))
    root.geometry("+50+50")  # posição na tela
    
    # Configurar estilo
    root.configure(bg=cores_atuais['cinza_claro'])
    
    # Frame principal com bordas arredondadas e sombra - TAMANHO REDUZIDO
    main_frame = tk.Frame(root, bg=cores_atuais['branco'], padx=10, pady=10)
    main_frame.pack(padx=6, pady=6)
    
    # Cabeçalho com ícone e título
    header_frame = tk.Frame(main_frame, bg=cores_atuais['branco'])
    header_frame.pack(fill='x', pady=(0, 8))
    
    # Tentativa de carregar o ícone do Google Calendar
    try:
        icon_url = "https://ssl.gstatic.com/calendar/images/dynamiclogo_2020q4/calendar_17_2x.png"
        response = requests.get(icon_url)
        img_data = response.content
        icon = Image.open(BytesIO(img_data))
        icon = icon.resize((20, 20))  # Tamanho reduzido
        photo = ImageTk.PhotoImage(icon)
        icon_label = tk.Label(header_frame, image=photo, bg=cores_atuais['branco'])
        icon_label.image = photo
        icon_label.pack(side='left', padx=(0, 6))  # Espaçamento reduzido
    except:
        # Se falhar ao carregar o ícone, usa um label de texto
        icon_label = tk.Label(header_frame, text="📅", font=("Arial", 14), bg=cores_atuais['branco'], fg=cores_atuais['azul'])
        icon_label.pack(side='left', padx=(0, 6))
    
    # Título com o mês atual
    mes_atual = datetime.now().strftime('%B %Y')
    mes_atual = mes_atual.replace('January', 'Janeiro').replace('February', 'Fevereiro')
    mes_atual = mes_atual.replace('March', 'Março').replace('April', 'Abril')
    mes_atual = mes_atual.replace('May', 'Maio').replace('June', 'Junho')
    mes_atual = mes_atual.replace('July', 'Julho').replace('August', 'Agosto')
    mes_atual = mes_atual.replace('September', 'Setembro').replace('October', 'Outubro')
    mes_atual = mes_atual.replace('November', 'Novembro').replace('December', 'Dezembro')
    
    title_label = tk.Label(header_frame, text=f"Agenda - {mes_atual}", font=("Arial", 12, "bold"), 
                        bg=cores_atuais['branco'], fg=cores_atuais['azul'])
    title_label.pack(side='left')
    
    # Adicionar contador de eventos (inicialmente vazio)
    eventos_count_label = tk.Label(header_frame, text="", font=("Arial", 10), 
                               bg=cores_atuais['branco'], fg=cores_atuais['cinza_texto'])
    eventos_count_label.pack(side='left', padx=(8, 0))
    
    # Frame para o modo dark
    dark_mode_frame = tk.Frame(header_frame, bg=cores_atuais['branco'])
    dark_mode_frame.pack(side='right', padx=(0, 6))
    
    # Label para o texto "Dark"
    dark_label = tk.Label(dark_mode_frame, text="Dark", font=("Arial", 10), 
                       bg=cores_atuais['branco'], fg=cores_atuais['cinza_texto'])
    dark_label.pack(side='left', padx=(0, 4))
    
    # Botão toggle
    toggle_button = criar_botao_toggle(dark_mode_frame, modo_dark)
    toggle_button.pack(side='left')
    
    # Botão fechar (X)
    close_button = tk.Label(header_frame, text="✕", font=("Arial", 12), 
                        bg=cores_atuais['branco'], fg=cores_atuais['cinza_texto'])
    close_button.pack(side='right', padx=(6, 0))
    close_button.bind("<Button-1>", lambda e: root.destroy())
    
    # Separador
    separator = tk.Frame(main_frame, height=1, bg=cores_atuais['cinza_claro'])
    separator.pack(fill='x', pady=(0, 8))
    
    # Frame para conter os eventos com rolagem de mouse (sem scrollbar)
    events_container_frame = tk.Frame(main_frame, bg=cores_atuais['branco'])
    events_container_frame.pack(fill='both', expand=True)
    
    # Canvas para permitir rolagem com mouse
    canvas = tk.Canvas(events_container_frame, bg=cores_atuais['branco'], highlightthickness=0, 
                     width=320, height=400)
    canvas.pack(fill='both', expand=True)
    
    # Frame dentro do canvas para conter os eventos
    events_frame = tk.Frame(canvas, bg=cores_atuais['branco'])
    events_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=events_frame, anchor='nw', width=320)
    
    # Configurar rolagem com mouse
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    # Label para mostrar status de carregamento
    loading_label = tk.Label(events_frame, text="Carregando eventos...", 
                          font=("Arial", 10), fg=cores_atuais['cinza_texto'], bg=cores_atuais['branco'])
    loading_label.pack(pady=10)
    
    # Para permitir arrastar a janela
    def start_drag(event):
        root._drag_start_x = event.x
        root._drag_start_y = event.y
    
    def do_drag(event):
        x = root.winfo_x() + event.x - root._drag_start_x
        y = root.winfo_y() + event.y - root._drag_start_y
        root.geometry(f"+{x}+{y}")
    
    # Permitir arrastar a partir do cabeçalho
    header_frame.bind("<Button-1>", start_drag)
    header_frame.bind("<B1-Motion>", do_drag)
    title_label.bind("<Button-1>", start_drag)
    title_label.bind("<B1-Motion>", do_drag)
    icon_label.bind("<Button-1>", start_drag)
    icon_label.bind("<B1-Motion>", do_drag)
    
    return root, events_frame, loading_label, eventos_count_label

def cor_evento(color_id):
    global cores_atuais
    # Mapeamento de IDs de cores do Google Calendar para as cores reais
    cores_calendar = {
        '1': cores_atuais['azul'],     # Azul
        '2': cores_atuais['verde'],    # Verde
        '3': cores_atuais['vermelho'], # Vermelho
        '4': '#9C27B0' if not modo_dark else '#CE93D8',  # Roxo
        '5': '#FF5722' if not modo_dark else '#FFAB91',  # Laranja
        '6': '#00BCD4' if not modo_dark else '#80DEEA',  # Ciano
        '7': '#795548' if not modo_dark else '#BCAAA4',  # Marrom
        '8': '#607D8B' if not modo_dark else '#B0BEC5',  # Cinza azulado
        '9': cores_atuais['amarelo'],  # Amarelo
        '10': '#8BC34A' if not modo_dark else '#C5E1A5',  # Verde claro
        '11': '#009688' if not modo_dark else '#80CBC4',  # Verde azulado
    }
    return cores_calendar.get(color_id, cores_atuais['azul'])

def nome_dia_semana(data_str):
    """Retorna o nome do dia da semana a partir de uma string de data no formato DD/MM"""
    try:
        # Adicionar o ano atual à data para poder converter
        ano_atual = datetime.now().year
        data_completa = f"{data_str}/{ano_atual}"
        data_obj = datetime.strptime(data_completa, '%d/%m/%Y')
        
        # Obter o nome do dia da semana
        dia_semana = data_obj.strftime('%A')
        
        # Traduzir para português
        traducoes = {
            'Monday': 'Segunda',
            'Tuesday': 'Terça',
            'Wednesday': 'Quarta',
            'Thursday': 'Quinta',
            'Friday': 'Sexta',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        
        return traducoes.get(dia_semana, dia_semana)
    except Exception as e:
        print(f"Erro ao obter dia da semana: {e}")
        return ""

def exibir_eventos(events_frame, eventos, eventos_count_label):
    global cores_atuais
    # Limpar frame de eventos
    for widget in events_frame.winfo_children():
        widget.destroy()
    
    # Atualizar contador de eventos
    total_eventos = len(eventos)
    eventos_count_label.config(text=f"({total_eventos} eventos)")
    
    if not eventos:
        empty_label = tk.Label(events_frame, text="Sem eventos para este mês.", 
                            font=("Arial", 11), fg=cores_atuais['cinza_texto'], bg=cores_atuais['branco'])
        empty_label.pack(pady=10)
        return
    
    print(f"Total de eventos recuperados: {len(eventos)}")
    
    # Agrupar eventos por data
    eventos_por_data = {}
    for evento in eventos:
        data = evento['data_curta']  # Formato mais curto (DD/MM)
        if data not in eventos_por_data:
            eventos_por_data[data] = []
        eventos_por_data[data].append(evento)
    
    print(f"Datas diferentes: {len(eventos_por_data.keys())}")
    
    # Ordenar as datas
    datas_ordenadas = sorted(eventos_por_data.keys(), 
                           key=lambda d: datetime.strptime(d + f"/{datetime.now().year}", '%d/%m/%Y'))
    
    # Criar widgets para cada data e seus eventos
    hoje = datetime.now().strftime('%d/%m')
    amanha = (datetime.now() + timedelta(days=1)).strftime('%d/%m')
    
    for i, data in enumerate(datas_ordenadas):
        eventos_do_dia = eventos_por_data[data]
        
        # Se não for o primeiro grupo, adiciona separador
        if i > 0:
            separator = tk.Frame(events_frame, height=1, bg=cores_atuais['cinza_claro'])
            separator.pack(fill='x', pady=6)  # Espaçamento reduzido
        
        # Frame da data
        date_frame = tk.Frame(events_frame, bg=cores_atuais['branco'])
        date_frame.pack(fill='x', anchor='w', pady=(4, 0))  # Espaçamento reduzido
        
        # Label da data com dia da semana
        if data == hoje:
            data_texto = f"Hoje, {data}"
        elif data == amanha:
            data_texto = f"Amanhã, {data}"
        else:
            dia_semana = nome_dia_semana(data)
            data_texto = f"{dia_semana}, {data}"
        
        # Adicionar número de eventos do dia
        num_eventos = len(eventos_do_dia)
        data_texto = f"{data_texto} ({num_eventos})"
        
        date_label = tk.Label(date_frame, text=data_texto, 
                           font=("Arial", 10, "bold"), fg=cores_atuais['cinza_data'], bg=cores_atuais['branco'])
        date_label.pack(anchor='w')
        
        print(f"Data {data}: {len(eventos_do_dia)} eventos")
        
        # Exibir cada evento do dia
        for evento in eventos_do_dia:
            event_frame = tk.Frame(events_frame, bg=cores_atuais['branco'])
            event_frame.pack(fill='x', pady=2, anchor='w')  # Espaçamento reduzido
            
            # Frame para organizar o layout do evento
            event_content_container = tk.Frame(event_frame, bg=cores_atuais['branco'])
            event_content_container.pack(fill='x', expand=True)
            
            # Indicador de cor do evento
            color_indicator = tk.Frame(event_content_container, width=4, 
                                   bg=cor_evento(evento['cor']))
            color_indicator.pack(side='left', fill='y', padx=(0, 6))  # Espaçamento reduzido
            
            # Conteúdo do evento
            event_content = tk.Frame(event_content_container, bg=cores_atuais['branco'])
            event_content.pack(side='left', fill='both', expand=True)
            
            # Título do evento
            title_label = tk.Label(event_content, text=evento['titulo'], 
                               font=("Arial", 10), fg=cores_atuais['cinza_texto'],  # Tamanho reduzido
                               bg=cores_atuais['branco'], anchor='w', justify='left')
            title_label.pack(fill='x', anchor='w')
            
            # Horário (se não for evento de dia inteiro)
            if not evento['dia_inteiro']:
                time_label = tk.Label(event_content, text=evento['hora'], 
                                  font=("Arial", 9), fg=cores_atuais['cinza_data'],  # Tamanho reduzido
                                  bg=cores_atuais['branco'], anchor='w', justify='left')
                time_label.pack(fill='x', anchor='w')
            else:
                time_label = tk.Label(event_content, text="Dia inteiro", 
                                  font=("Arial", 9), fg=cores_atuais['cinza_data'],  # Tamanho reduzido
                                  bg=cores_atuais['branco'], anchor='w', justify='left')
                time_label.pack(fill='x', anchor='w')

def atualizar_widget(events_frame, service, eventos_count_label):
    try:
        # Buscar todos os eventos do mês
        eventos_raw = buscar_eventos(service, max_results=100)
        
        # Converter para formato mais simples
        eventos = [formatar_evento(e) for e in eventos_raw]
        
        # Ordenar eventos por data
        eventos.sort(key=lambda e: e['data_obj'])
        
        # Exibir na interface
        exibir_eventos(events_frame, eventos, eventos_count_label)
    except Exception as e:
        # Exibir mensagem de erro
        for widget in events_frame.winfo_children():
            widget.destroy()
        error_label = tk.Label(events_frame, text=f"Erro ao atualizar: {str(e)}", 
                            font=("Arial", 10), fg=cores_atuais['vermelho'], bg=cores_atuais['branco'])
        error_label.pack(pady=10)
        
        # Exibir detalhes do erro no console
        import traceback
        traceback.print_exc()
    
    # Atualiza a cada 5 minutos
    events_frame.after(5 * 60 * 1000, lambda: atualizar_widget(events_frame, service, eventos_count_label))

def reconstruir_interface(root, callback=None):
    # Chamar callback (como alternar_modo) antes de reconstruir
    if callback:
        callback()
    
    # Destruir a janela atual
    root.destroy()
    
    # Reiniciar a interface
    threading.Thread(target=iniciar_interface).start()

def iniciar_interface():
    try:
        # Autenticar com Google Calendar
        service = autenticar_google_calendar()
        
        # Criar a interface
        root, events_frame, loading_label, eventos_count_label = criar_interface()
        
        # Iniciar a atualização dos eventos (após um curto delay para a interface carregar)
        root.after(500, lambda: atualizar_widget(events_frame, service, eventos_count_label))
        
        # Iniciar loop principal
        root.mainloop()
    except Exception as e:
        print(f"Erro ao iniciar: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    threading.Thread(target=iniciar_interface).start()