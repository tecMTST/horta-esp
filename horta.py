from machine import UART, Pin, ADC
import utime
from SIM800L import Modem
import json
from DHT22 import DHT22


Chave_API = 'GB30A3E1OFJ3SL8O'
UMIDADE_SOLO_1 = 'field1'
UMIDADE_SOLO_2 = 'field2'
UMIDADE_SOLO_3 = 'field3'
TEMPERATURA_AR = 'field5'
UMIDADE_AR = 'field4'

provedor = "Claro" #'Claro', 'Vivo', 'Tim' ou 'Oi'
prov = {'Claro': {'shortname': 'Claro', 'longname': 'Claro',        'id': '72405', 'APN': 'claro.com.br',    'USER': 'claro', 'SENHA': 'claro'},
        'Vivo':  {'shortname': '72410', 'longname': '72410',        'id': '72410', 'APN': 'zap.vivo.com.br', 'USER': 'vivo',  'SENHA': 'vivo' },
        'Tim':   {'shortname': 'TIM',   'longname': 'TIM BRASIL',   'id': '72403', 'APN': 'timbrasil.br',    'USER': 'tim',   'SENHA': 'tim'  },
        'Oi':    {'shortname': 'Oi',    'longname': 'TNL PCS S.A.', 'id': '72431', 'APN': 'gprs.oi.com.br',  'USER': 'oi',    'SENHA': 'oi'   }}

def configura_modem():
    global modem
    print('Começando...\n')
    # Cria o objeto modem (nosso SIM800L) e configura a interface serial
    modem = Modem(uart=0, MODEM_TX_PIN=1, MODEM_RX_PIN=0)
    modem.initialize()    # Inicia o SIM800L
    escaneia_redes()
    conexao_provedor()
    modem.connect(apn=prov[provedor]['APN'],user=prov[provedor]['USER'],pwd=prov[provedor]['SENHA'])    # Conecta ao GPRS
    end_ip_local = modem.get_ip_addr()
    print('Endereço IP: "{}"\n'.format(end_ip_local))

def escaneia_redes(): #escaeia e verifica se há rede do provedor
    global modem, provedor
    print('Escaneando as redes...')
    tem = 0
    while tem == 0:
        escaneia = modem.scan_networks()
        print('Scan de Redes: "{}"\n'.format(escaneia))
        #verifica se tem a rede do provedor
        for rede in escaneia:
            if rede['name'] == prov[provedor]['shortname']:
                tem = 1
        if tem == 0:
            print('Verifique a posição da antena')
            print('Tentando novamente...\n')
            utime.sleep_ms(5000)

def conexao_provedor(): #verifica se está conectado à rede do provedor, se não estiver força para conectar
    global modem, provedor
    conectado = 0
    
    while conectado != prov[provedor]['shortname']:
        conectado = modem.get_current_network()
        
        if conectado == prov[provedor]['id']:
            conectado = prov[provedor]['shortname']

        elif conectado != prov[provedor]['shortname']:
            print('Tentando conectar novamente...')
            modem.execute_at_command('conectaman', data=prov[provedor]['id']) #conexao manual
            conectado = modem.get_current_network()
            if conectado == prov[provedor]['id']:
                conectado = prov[provedor]['shortname']
            
            elif conectado != prov[provedor]['shortname']:
                escaneia_redes() #se não escanear a rede novamente
                
        print('Rede conectada: "{}"\n'.format(conectado))
        utime.sleep_ms(1000)

def inic_sensores_umsolo():
    global va_min_1,va_min_2,va_min_3,va_max_1,va_max_2,va_max_3,s_umsolo_1,s_umsolo_2,s_umsolo_3
    va_min_1 = 7900 #umidade 100%
    va_max_1 = 15000 #umidade 0%
    s_umsolo_1 = ADC(0)
    utime.sleep(1)
    va_min_2 = 7900 #umidade 100%
    va_max_2 = 15000 #umidade 0%
    s_umsolo_2= ADC(1)
    utime.sleep(1)
    va_min_3 = 7900 #umidade 100%
    va_max_3 = 15000 #umidade 0%
    s_umsolo_3 = ADC(2)
    utime.sleep(1)
    
def le_umidade_solo(sensor, va_min, va_max):
    umsolo = (1-(sensor.read_u16() - va_min) / (va_max - va_min)) * 100
    if umsolo < 0:
        umsolo = 0
    elif umsolo > 100:
        umsolo = 100    
    return umsolo

configura_modem()
print('a')
inic_sensores_umsolo()
print('b')
s_umtempar = DHT22(Pin(2,Pin.IN))

# Enviando via HTTP
#print('ENVIAR OS DADOS VIA HTTP GET...')

while True:
    conexao_provedor()
    
    umsolo_1 = le_umidade_solo(s_umsolo_1,va_min_1,va_max_1)
    print("umidade do solo: {}%".format(umsolo_1))
    utime.sleep(1)
    umsolo_2 = le_umidade_solo(s_umsolo_2,va_min_2,va_max_2)
    print("umidade do solo: {}%".format(umsolo_2))
    utime.sleep(1)
    umsolo_3 = le_umidade_solo(s_umsolo_3,va_min_3,va_max_3)
    print("umidade do solo: {}%".format(umsolo_3))
    utime.sleep(1)
    
    tempar = s_umtempar.read()[0]
    
    utime.sleep(1)
    umar = s_umtempar.read()[1]
     
    print("temperatura do ar: {}C".format(tempar))
    print("umidade do ar: {}%".format(umar))
    url = 'https://api.thingspeak.com/update?api_key=GB30A3E1OFJ3SL8O&field1={}&field2={}&field3={}&field4={}&field5={}'.format(umsolo_1,umsolo_2,umsolo_3,umar,tempar)
    response = modem.http_request(url, 'GET')
    print('- Codigo de status:', response.status_code)
    print('- Resposta de conteudo:', response.content)
    utime.sleep(30)

# Disconnect Modem
#modem.disconnect()
    


