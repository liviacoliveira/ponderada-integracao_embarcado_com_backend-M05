import os

# Configurações do Banco de Dados
DB_FILE = "dados.db"

# Configurações do Flask
FLASK_PORT = 5000
DEBUG = True

# Configurações da Serial (Arduino)
SERIAL_PORT = os.getenv('SERIAL_PORT', 'COM3') 
SERIAL_BAUD = int(os.getenv('SERIAL_BAUD', 9600))
RECONNECT_DELAY = 5 
