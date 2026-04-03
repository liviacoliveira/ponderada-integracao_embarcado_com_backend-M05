import serial
import json
import time
import database
try:
    from . import config
except ImportError:
    import config

def iniciar_leitura_serial():
    """Lê dados da porta serial e insere no banco de dados com tratamento de erros."""
    porta = getattr(config, 'SERIAL_PORT', 'COM3')
    baud = getattr(config, 'SERIAL_BAUD', 9600)
    delay_reconexao = getattr(config, 'RECONNECT_DELAY', 5)

    print(f"Iniciando leitor serial na porta {porta} (@{baud} baud)...")

    ser = None
    while True:
        try:
            # Tenta abrir a conexão serial
            if ser is None or not ser.is_open:
                ser = serial.Serial(porta, baud, timeout=1)
                print(f"Conectado ao Arduino na porta {porta}!")

            # Lê uma linha da serial
            linha = ser.readline().decode('utf-8').strip()
            
            if linha:
                print(f"Recebido: {linha}")
                try:
                    # Tenta converter a linha para JSON
                    dados = json.loads(linha)
                    
                    # Extrai os valores (com fallback para None se não existirem)
                    temp = dados.get('temperatura')
                    umid = dados.get('umidade')
                    pres = dados.get('pressao')
                    
                    if temp is not None and umid is not None:
                        database.inserir_leitura(temp, umid, pres)
                        print("Dados salvos no banco com sucesso.")
                    else:
                        print("Aviso: JSON recebido incompleto (faltando temp ou umid).")
                        
                except json.JSONDecodeError:
                    print(f"Erro: Falha ao decodificar JSON: {linha}")
                except Exception as e:
                    print(f"Erro ao salvar no banco: {e}")

        except serial.SerialException as e:
            print(f"Erro de conexão serial: {e}")
            print(f"Tentando reconectar em {delay_reconexao} segundos...")
            if ser:
                ser.close()
            ser = None
            time.sleep(delay_reconexao)
            
        except KeyboardInterrupt:
            print("\nFinalizando leitor serial...")
            if ser:
                ser.close()
            break
            
        except Exception as e:
            print(f"Erro inesperado: {e}")
            time.sleep(delay_reconexao)

if __name__ == "__main__":
    iniciar_leitura_serial()
