"""
Ponto de entrada principal para o Widget de Calendário do Google.
Execute este arquivo para iniciar o aplicativo.
"""
from src.main import iniciar_interface
import threading

if __name__ == "__main__":
    # Inicia o widget em uma thread separada
    threading.Thread(target=iniciar_interface).start() 