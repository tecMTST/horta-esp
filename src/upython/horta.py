from machine import UART, Pin, ADC, I2C, Timer, WDT
import utime
from SIM800L import Modem # Comunicação por rede de celular.
import ahtx0 # Sensor de umidade e temperatura.
import tsl2561 # Sensor de luminosidade.


# Xavier: Variáveis não utilizadas (estão hard-coded no URL).
Chave_API = 'GB30A3E1OFJ3SL8O' 
UMIDADE_SOLO_1 = 'field1'
UMIDADE_SOLO_2 = 'field2'
UMIDADE_SOLO_3 = 'field3'
TEMPERATURA_AR = 'field5'
UMIDADE_AR = 'field4'
REINICIALIZACAO = 'field1'
BATERIA = 'field2'
IRRIGACAO = 'field3'


provedor = "Claro" #'Claro', 'Vivo', 'Tim' ou 'Oi'
prov = {'Claro': {'shortname': 'Claro', 'longname': 'Claro',        'id': '72405', 'APN': 'claro.com.br',    'USER': 'claro', 'SENHA': 'claro'},
        'Vivo':  {'shortname': '72410', 'longname': '72410',        'id': '72410', 'APN': 'zap.vivo.com.br', 'USER': 'vivo',  'SENHA': 'vivo' },
        'Tim':   {'shortname': 'TIM',   'longname': 'TIM BRASIL',   'id': '72403', 'APN': 'timbrasil.br',    'USER': 'tim',   'SENHA': 'tim'  },
        'Oi':    {'shortname': 'Oi',    'longname': 'TNL PCS S.A.', 'id': '72431', 'APN': 'gprs.oi.com.br',  'USER': 'oi',    'SENHA': 'oi'   }}


def log(msg):
    global debug_uart
    mensagem = "(log) {}".format(msg)
    print(mensagem)
    debug_uart.write(mensagem+'\n\r')


def loop(tempo_ms): #em milisegundos
#     log(" - Delay de {:.2f} segundos".format(float(tempo_ms/1000)))
    for i in range(0,tempo_ms):
        utime.sleep_ms(1)
    
    
def configura_modem():
    global modem
    log('Começando...')
    # Cria o objeto modem (nosso SIM800L) e configura a interface serial
    modem = Modem(uart=0, MODEM_TX_PIN=1, MODEM_RX_PIN=0)
    while modem.initialize() != 1:   # Inicia o SIM800L
        log('Reconfigurando...')
    escaneia_redes()      # Escaneia as redes de celular
    conexao_provedor()    # Conecta à rede do chip (SIM Card)
    conexao_gprs()        # Conecta à internet


def conexao_gprs():
    global modem, provedor
    log('Conectando à internet da "{}"...'.format(provedor))
    modem.connect(apn=prov[provedor]['APN'],user=prov[provedor]['USER'],pwd=prov[provedor]['SENHA'])    # Conecta ao GPRS
    end_ip_local = modem.get_ip_addr()
    log('Conectado! Endereço IP: "{}"'.format(end_ip_local))


def escaneia_redes(): #escaeia e verifica se há rede do provedor
    global modem, provedor
    log("Escaneando as redes...")
    tem = 0
    while tem == 0:
        escaneia = modem.scan_networks()
        log('Scan de Redes: "{}"'.format(escaneia))
        #verifica se tem a rede do provedor
        for rede in escaneia:
            if rede['name'] == prov[provedor]['shortname']:
                tem = 1
        if tem == 0:
            log('Verifique a posição da antena')
            log('Tentando novamente...')
            loop(5000)


def conexao_provedor(): #verifica se está conectado à rede do provedor, se não estiver força para conectar
    global modem, provedor
    log("Conectando ao Provedor...")
    conectado = 0
    
    while conectado != prov[provedor]['shortname']:
        conectado = modem.get_current_network()
        
        if conectado == prov[provedor]['id']:
            conectado = prov[provedor]['shortname']
            
        elif conectado != prov[provedor]['shortname']:
            log("Tentando conectar novamente...")
            modem.execute_at_command('conectaman', data=prov[provedor]['id']) #conexao manual
            conectado = modem.get_current_network()
            if conectado == prov[provedor]['id']:
                conectado = prov[provedor]['shortname']
            
            elif conectado != prov[provedor]['shortname']:
                log("Escanear as redes novamente...")
                escaneia_redes() #se não escanear a rede novamente
                
        log('Provedor conectado: "{}"'.format(conectado))
        loop(1000)


def inic_sensores(): #inicializa todos os sensores da horta
    global va_min_1,va_min_2,va_min_3,va_max_1,va_max_2,va_max_3,s_umsolo_1,s_umsolo_2,s_umsolo_3
    global s_umtempar, s_lum
    log("Inicializando sensores...")
    va_min_1 = 37433 #umidade 100%
    va_max_1 = 65535 #umidade 0%
    s_umsolo_1 = ADC(0)
    loop(500)
    va_min_2 = 38201 #umidade 100%
    va_max_2 = 65535 #umidade 0%
    s_umsolo_2= ADC(1)
    loop(500)
    va_min_3 = 37449 #umidade 100%
    va_max_3 = 65535 #umidade 0%
    s_umsolo_3 = ADC(2)
    loop(500)
    i2c_1 = I2C(1,scl=Pin(3), sda=Pin(2), freq=10000)
    s_umtempar = ahtx0.AHT10(i2c_1) # sensor de temperatura e umidade do ar 1
    s_lum = tsl2561.TSL2561(i2c_1)
    s_lum.active(True)


def le_umidade_solo(sensor, va_min, va_max): #le umidade do solo
    umsolo = lambda x : 100 if x > 100 else 0 if x < 0 else x
    return umsolo((1 - (sensor.read_u16() - va_min)/(va_max - va_min)) * 100)


def le_sensores(): #le todos os sensores
    global va_min_1,va_min_2,va_min_3,va_max_1,va_max_2,va_max_3,s_umsolo_1,s_umsolo_2,s_umsolo_3
    global umsolo_1, umsolo_2, umsolo_3, umar, tempar, s_umtempar, s_lum, lum
    log("Lendo sensores...")
    
    umsolo_1 = le_umidade_solo(s_umsolo_1,va_min_1,va_max_1)
    log("Umidade do solo 1: {}%".format(umsolo_1))
    loop(100)
    
    umsolo_2 = le_umidade_solo(s_umsolo_2,va_min_2,va_max_2)
    log("Umidade do solo 2: {}%".format(umsolo_2))
    loop(100)
    
    umsolo_3 = le_umidade_solo(s_umsolo_3,va_min_3,va_max_3)
    log("Umidade do solo 3: {}%".format(umsolo_3))
    loop(100)
    
    lum = s_lum.read()
    log("Luminosidade: {:.2f} Lux".format(lum))
    loop(100)

    tempar = s_umtempar.temperature
    log("Temperatura do ar: {:.2f}C".format(tempar))
    loop(1000)
    
    umar = s_umtempar.relative_humidity
    log("Umidade do ar: {:.2f}%".format(umar))
    loop(1000)


def envia_dados(url, tempo_ms):
    conexao_provedor()
    log("Enviando dados por requisição GET...")
    log(' - Dados: "{}"'.format(url))
    response = modem.http_request(url, 'GET')
    log(' - Resposta: Codigo de status = "{}"'.format(response.status_code))
    log(' - Resposta: Numero de Envios = "{}"'.format(response.content))
    log("Aguardando {:.2f} segundos para o proximo ciclo...\n".format(tempo_ms/1000))
    loop(tempo_ms)

        
def feed_wdt(self):
    global wdt, count
    #resetar o RP2 a cada 6h - 21600s
    count+=1
    #21600/7 = 3085 -> 6 horas
    if count < 3085:
        log("Alimenta Watchdog Time")
        wdt.feed()
    else:
        log("RESETAR")
        utime.sleep(5)

# def configura_RTC():
#     global resetar
#     #pega data e hora da rede
#     dataehora = modem.execute_at_command('clock')
#     print('\n\n\n\n{}\n\n\n\n\n'.format(dataehora))
#     ano = int("20"+dataehora[8]+dataehora[9])
#     mes = int(dataehora[11]+dataehora[12])
#     dia = int(dataehora[14]+dataehora[15])
#     hora = int(dataehora[17]+dataehora[18])
#     mint = int(dataehora[20]+dataehora[21])
#     seg = int(dataehora[23]+dataehora[24])
#     print("\n\n{}\n{}\n{}\n{}\n{}\n{}\n\n".format(dia, mes, ano, hora, mint, seg))
#     #esta versão de micropython nao tem RTC implementado...


#inicio
debug_uart = UART(1,baudrate=115200, rx=Pin(5), tx=Pin(4))
log("Inicio...")
inicializacao = 1
count = 0
log("Definindo Timer (7s) para WDT de (8s)...")
tim = Timer(-1)
tim.init(period=7000, mode=Timer.PERIODIC, callback=feed_wdt)
wdt = WDT(id=0,timeout=8000)
log("Aguardando boot do modem (15s)...")
loop(15000)
configura_modem()
# configura_RTC()
inic_sensores()


while True:
    le_sensores()
    url = 'https://api.thingspeak.com/update?api_key=GB30A3E1OFJ3SL8O&field1={:.2f}&field2={:.2f}&field3={:.2f}&field4={:.2f}&field5={:.2f}&field6={:.2f}'.format(umsolo_1,umsolo_2,umsolo_3,umar,tempar,lum)
    envia_dados(url, 30000)
    url = 'https://api.thingspeak.com/update?api_key=U6N0IP91Z7VK92UV&field1={:.2f}&field2={:.2f}&field3={:.2f}'.format(inicializacao,100,0)
    inicializacao = 0
    envia_dados(url, 30000)

    


 