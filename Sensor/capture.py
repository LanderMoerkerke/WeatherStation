import datetime
import threading

from Database.DbClass import DbClass
from Sensor.BMP280.BMP280 import BMP280
from Sensor.LightSensor.MCP3008 import MCP3008
from Sensor.TH02.TH02 import TH02

# Sensoren
ls = MCP3008()
ds = BMP280()
ts = TH02()

# Database connector
mc = DbClass()

print("Licht %i" % ls.readChannel(0))
presTemp = ds.getPresTemp()
print("Temperatuur %.2f" % presTemp[0])
print("Temperatuur %.2f" % ts.getTemp())
print("Luchtdruk %.2f" % presTemp[1])
print("Vochtigheid %.2f" % ts.getHum())

presTemp = ds.getPresTemp()
d = datetime.datetime.now()
temp = (presTemp[0] + ts.getTemp()) / 2
lucht = presTemp[1]
vocht = ts.getHum()


# print(mc.executeQuery("select * from db_weerstation.weerstation"))


def capture():
    threading.Timer(5.0, capture).start()
    presTemp = ds.getPresTemp()
    d = datetime.datetime.now()
    temp = (presTemp[0] + ts.getTemp()) / 2
    lucht = presTemp[1]
    vocht = ts.getHum()
    mc.insertSample(temp, vocht, lucht, 5, 1, 2)
    print("Capture successful")


capture()

try:
    while True:
        pass
except KeyboardInterrupt:
    mc.closeCursor()
    print("\nScript ended")
