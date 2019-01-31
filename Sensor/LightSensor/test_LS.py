import time

from Sensor.LightSensor.MCP3008 import MCP3008

adc = MCP3008()
while True:
    data = adc.readChannel(0)
    print(data)
    time.sleep(.5)
