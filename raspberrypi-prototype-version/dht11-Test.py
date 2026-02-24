# Source for DHT11 sensor test on Raspberry Pi baseline prototype: https://www.thegeekpub.com/236867/using-the-dht11-temperature-sensor-with-the-raspberry-pi/?srsltid=AfmBOop1MSKZrm5IudM9KHjweXuDKZntLkyoz3QiFeixvxoGdVkVOTR5
# purpose: will be testing the DHT11 sensor GreenSense uses for temperature & humidity for an exploration
# on expanded WiFi/Bluetooth capabilities
import Adafruit_DHT
DHT_PIN = 4

while True:
    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, DHT_PIN)
    if humidity is not None and temperature is not None:
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    else:
        print('Failed to get reading. Try again!')