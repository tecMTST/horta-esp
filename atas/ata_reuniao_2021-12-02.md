# Reunião de baixo nível da horta (02/12/2021)

## Presentes

* Renato
* Kauê
* Robson
* Willian
* Daniel
* Xavier

## Discussões

### Sensores a serem usados

* De umidade do solo: <https://arduinosantaefigenia.com.br/produto/sensor-de-umidade-de-solo-capacitivo/>
* De luminosidade: [TSL2561](https://arduinosantaefigenia.com.br/produto/sensor-de-luz-tsl2561/)
* De umidade e temperatura do ar: vou (Xavier) verificar qual sensor é melhor em termos de custo benefício:
  [DHT22](https://www.wjcomponentes.com.br/sensor-dht22) ou
  [AHT10](https://arduinosantaefigenia.com.br/produto/aht10-2/)
  ([link alternativo](https://www.usinainfo.com.br/sensor-de-temperatura/sensor-aht10-de-alta-precisao-para-medir-temperatura-e-umidade-5691.html)).
* Faremos um `struct` com os dados dos sensores.

### Lista de materiais para sensores (feita depois da reunião)

* De umidade do solo: [Sensor de umidade capacitivo](https://arduinosantaefigenia.com.br/produto/sensor-de-umidade-de-solo-capacitivo/)
* De luminosidade: [TSL2561](https://arduinosantaefigenia.com.br/produto/sensor-de-luz-tsl2561/)
* De umidade e temperatura do ar: [AHT10](https://arduinosantaefigenia.com.br/produto/aht10-2/)

* Para protótipo de sensor de Índice de área foliar:
  * 2 x Red detector = 650 nm ± 5 nm with 65 nm FWHM
  * 2 x NIR detector = 810 nm ± 5 nm with 65 nm FWHM
  * 2 - 2N3904 NPN transistors ( or SSM2212 NPN matched pair )
  * 1 - 100KΩ resistor
  * 1 - 2.2KΩ resistor
  * 3 - LEDs ( multiple red, yellow and green colors )
  * 1 - Infrared LED ( QED-123 )

Refs:
* <https://www.intechopen.com/chapters/19066>
* <https://wiki.analog.com/university/courses/electronics/electronics-lab-led-sensor>